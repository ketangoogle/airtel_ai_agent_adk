from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from psycopg2 import sql, OperationalError
import os
import requests
import psycopg2 
from google.cloud.sql.connector import Connector, IPTypes
import pg8000.dbapi
from typing import Optional, Dict, Any
from dotenv import load_dotenv


MODEL_GEMINI = "gemini-2.0-flash"
SOP_FAQ_FILE_PATH = "Airtel_Support_SOP_FAQ.pdf" 
load_dotenv()
# Global variable for the Cloud SQL Connector instance to manage its lifecycle
cloud_sql_connector = None

def get_cloud_sql_connection():
    """Establishes a connection to the PostgresSQL database vial Cloud Sql Connector. 
    This internal helper function ensures the connector is initialized only once.\
    and uses env variables for security.

    Returns:
        pg8000.dbapi.Connection: An active connection object to the PostgreSQL database.
    Raises:
        ValueError: If any required environment variable is not set.
        Exception: If the connection fails for any reason.
    """
    global cloud_sql_connector
    instance_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")

    if not all([instance_connection_name, db_user, db_password, db_name]):
        print("ðŸ”´ Error: Missing one or more required environment variables for Cloud SQL.")
        print("Please set CLOUD_SQL_CONNECTION_NAME, DB_USER, DB_PASSWORD, and DB_NAME.")
        raise ValueError("Cloud SQL environment variables not set.")
    try:
        if cloud_sql_connector is None:
            ip_type = IPTypes.PUBLIC
            cloud_sql_connector = Connector(ip_type=ip_type)

        conn = cloud_sql_connector.connect(
            instance_connection_name,
            "pg8000",  # Specify the driver the connector should use
            user=db_user,
            password=db_password,
            db=db_name,
        )
        return conn
    except Exception as e:
        print(f"ðŸ”´ Error: Could not connect to the Cloud SQL database.")
        print(f"Please ensure CLOUD_SQL_CONNECTION_NAME ('{instance_connection_name}') is correct,")
        print(f"and that your application has permission (Cloud SQL Client role) to connect.")
        raise e

def run_sql(query: str) -> dict:
    """
    Connects to the PostgreSQL database, executes a given SQL query, and returns the result.
    Database connection details are sourced from environment variables.
    """
    conn = None
    try:
        # Establish connection using environment variables for security
        conn = get_cloud_sql_connection()
        cursor = conn.cursor()
        cursor.execute(query)

        # Check if the query was a SELECT to fetch results
        if cursor.description:
            # Fetch all rows and column names
            colnames = [desc[0] for desc in cursor.description]
            records = cursor.fetchall()
            result = [dict(zip(colnames, record)) for record in records]
        else:
            # For non-SELECT queries (INSERT, UPDATE, DELETE)
            result = {"status": "success", "rows_affected": cursor.rowcount}

        conn.commit()
        cursor.close()
        return {"result": result}
    except (OperationalError, psycopg2.Error) as e:
        # Handle database connection or query errors
        return {"error": f"Database error: {e}"}
    finally:
        if conn is not None:
            conn.close()

# --- Core Agent Functions ---


sql_tool = FunctionTool(
    func=run_sql
)

def make_api_call(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None) -> dict:
    """
    Makes an HTTP request to a specified URL.
    """
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            json=data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

# --- Tool Definitions ---
# CORRECTED: Removed the 'description' keyword argument.


api_call_tool = FunctionTool(
    func=make_api_call
)
execution_agent = LlmAgent(
    name="execution_agent",
    model=MODEL_GEMINI,
    description="Executes technical tasks like running SQL queries and making API calls.",
    instruction="""
    You are a highly skilled technical execution agent and a PostgreSQL expert. Your primary goal is to resolve issues by interacting with a database or APIs.

    1. You will receive a user request and a relevant Standard Operating Procedure (SOP).
    2. Analyze the user's request to extract key details (e.g., order_id).
    3. Follow the SOP step-by-step.
    4. First, use the `run_sql` tool to execute the necessary query from the SOP to diagnose the problem.
    5. **Analyze the result of the SQL query.**
    6. Based on the result and the SOP, decide on the next step. This could be making an API call with the `api_call_tool` or providing an escalation instruction.
    7. Continue executing steps until the SOP is complete or requires escalation.
    8. If the SOP says create a ticket, use the `ticket_creation_agent` to create a support ticket.
    
    **Your Final Output:**
    - Provide a summary of the actions taken and the final outcome or the required escalation message.
    
    **Database Context:**
    You will be working with a primary table named `task`. Here is its schema:
    - `order_id` (VARCHAR): The unique ID of the order.
    - `corelation_id` (VARCHAR): A correlation ID for tracking.
    - `status` (VARCHAR): The current state of the task (e.g., 'Feasibility Check', 'Installation Engineer Assignment', 'Reached Onsite').
    - `task_type` (VARCHAR): The type of task ('Install', 'Fault Repair').
    - `organisation_process_path` (VARCHAR): The business process path (e.g., 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR').
    - `common_details` (JSONB): Contains nested details. You can query it like `common_details->'commonDetails'->'telemedia'->>'bin' = 'OAOE'`.
    - `pending_with_details` (VARCHAR): Shows who the task is pending with (e.g., an engineer's mobile number).
    - `rsu` (VARCHAR): The Residential Service Unit.
    - `created_date` (TIMESTAMP): The timestamp when the task was created.
    """,
    tools=[sql_tool, api_call_tool]
)
