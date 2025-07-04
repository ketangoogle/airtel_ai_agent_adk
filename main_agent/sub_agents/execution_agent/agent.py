from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from psycopg2 import sql, OperationalError
import os
import requests
import psycopg2 
from typing import Optional, Dict, Any

MODEL_GEMINI = "gemini-2.0-flash"
def run_sql(query: str) -> dict:
    """
    Connects to the PostgreSQL database, executes a given SQL query, and returns the result.
    Database connection details are sourced from environment variables.
    """
    conn = None
    try:
        # Establish connection using environment variables for security
        conn = psycopg2.connect(
            host=os.environ.get("PG_HOST", "localhost"),
            dbname=os.environ.get("PG_DBNAME", "airtel_support"),
            user=os.environ.get("PG_USER", "postgres"),
            password=os.environ.get("PG_PASSWORD"), # Ensure this is set in your environment
            port=os.environ.get("PG_PORT", 5432)
        )
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

