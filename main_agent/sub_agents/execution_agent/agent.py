from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
import os
import requests
import psycopg2 
from google.cloud.sql.connector import Connector, IPTypes
import pg8000.dbapi
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import datetime # CORRECTED IMPORT

MODEL_GEMINI = "gemini-2.0-flash"
load_dotenv()

# Global variable for the Cloud SQL Connector instance
cloud_sql_connector = None

def get_cloud_sql_connection():
    """Establishes a connection to the PostgresSQL database via Cloud Sql Connector."""
    global cloud_sql_connector
    instance_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")

    if not all([instance_connection_name, db_user, db_password, db_name]):
        raise ValueError("Cloud SQL environment variables not set.")
    
    try:
        if cloud_sql_connector is None:
            ip_type = IPTypes.PUBLIC
            cloud_sql_connector = Connector(ip_type=ip_type)
        conn = cloud_sql_connector.connect(
            instance_connection_name, "pg8000", user=db_user, password=db_password, db=db_name
        )
        return conn
    except Exception as e:
        raise e

def run_sql(query: str) -> dict:
    """
    Connects to the PostgreSQL database, executes a query, and returns a JSON-serializable result.
    It now handles datetime objects by converting them to ISO 8601 strings.
    """
    conn = None
    try:
        conn = get_cloud_sql_connection()
        cursor = conn.cursor()
        cursor.execute(query)

        if cursor.description:
            colnames = [desc[0] for desc in cursor.description]
            records = cursor.fetchall()
            
            processed_records = []
            for record in records:
                row_dict = {}
                for i, col in enumerate(colnames):
                    value = record[i]
                    # CORRECTED TYPE CHECK
                    if isinstance(value, datetime.datetime): 
                        row_dict[col] = value.isoformat() 
                    else:
                        row_dict[col] = value
                processed_records.append(row_dict)
            result = processed_records
        else:
            result = {"status": "success", "rows_affected": cursor.rowcount}

        conn.commit()
        cursor.close()
        return {"result": result}
    except (Exception, psycopg2.Error) as e:
        return {"error": f"Database error: {e}"}
    finally:
        if conn is not None:
            conn.close()

def make_api_call(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None) -> dict:
    """Makes an HTTP request to a specified URL."""
    try:
        response = requests.request(
            method, url, headers=headers, params=params, json=data, timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

# --- Tool Definitions ---
sql_tool = FunctionTool(func=run_sql)
api_call_tool = FunctionTool(func=make_api_call)

# --- Agent Definition ---
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
    """,
    tools=[sql_tool, api_call_tool]
)