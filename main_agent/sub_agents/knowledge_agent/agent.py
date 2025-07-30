from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
import os
from .bigquery_knowledge_base import search_knowledge_base


# --- Database Functionality (Previously in db_operations.py) ---
SOP_FAQ_FILE_PATH = "Airtel_Support_SOP_FAQ.pdf" 
MODEL_GEMINI = "gemini-2.0-flash"


# def read_knowledge_base(file_path: str) -> str:
#     """
#     Reads the content of the SOP/FAQ document.
#     """
#     if not os.path.exists(file_path):
#         return f"Error: Knowledge base file not found at '{file_path}'"
#     return f"Successfully accessed the knowledge base file at '{file_path}'. The agent should now use its internal knowledge to answer based on the SOPs and FAQs within."


# def get_knowledge_base_content():
#     """
#     Helper function to get the content of the knowledge base.
#     This function will be wrapped by FunctionTool to give it a proper name.
#     """
#     return {"content": read_knowledge_base(SOP_FAQ_FILE_PATH)}


knowledge_tool = FunctionTool(
    func= search_knowledge_base # Now using a named function
)

knowledge_agent = LlmAgent(
    name="knowledge_agent",
    model=MODEL_GEMINI,
    description="Answers user questions and follows procedures described in the SOP/FAQ document.",
    instruction="You are a support agent who answers questions by consulting the provided knowledge base. You must use the 'read_knowledge_base' tool to access the SOP/FAQ document and provide solutions from it. If the solution requires a technical step like a database query or an API call, clearly state the required command. and pass it to the execution agent for execution."
    "If the SOP says create a ticket, use the `ticket_creation_agent` to create a support ticket." \
    "If the order_id is given in the chat go to the `execution_agent` to execute the SQL query and provide the result. and look what is wrong then refer the SOP if you find the solution then provide the solution to the user. If you don't find the solution then pass it to the `ticket_creation_agent` to create a support ticket.",
    tools=[knowledge_tool]
)
