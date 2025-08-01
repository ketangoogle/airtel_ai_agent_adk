from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from app.services.cloud_connection import get_cloud_sql_connection
from app.tools.run_sql_tool import run_sql
from app.tools.api_call_tool import make_api_call

MODEL_GEMINI = "gemini-2.0-flash"
sql_tool = FunctionTool(func=run_sql)
api_call_tool = FunctionTool(func=make_api_call)

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