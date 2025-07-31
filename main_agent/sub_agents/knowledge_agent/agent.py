from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from app.tools.knowledge_base_tool import search_knowledge_base


MODEL_GEMINI = "gemini-2.5-flash"

knowledge_tool = FunctionTool(
    func= search_knowledge_base 
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
