from google.adk.agents import LlmAgent
from .sub_agents.knowledge_agent.agent import knowledge_agent
from .sub_agents.execution_agent.agent import execution_agent
from .sub_agents.ticket_creation.agent import ticket_creation_agent
from dotenv import load_dotenv

load_dotenv()

# Use a valid and available Gemini model name
MODEL_GEMINI = "gemini-2.0-flash"
SOP_FAQ_FILE_PATH = "Airtel_Support_SOP_FAQ.pdf" # Make sure this PDF file is in the same directory


# --- Agent Definitions ---


root_agent = LlmAgent(
    name="airtel_support_agent",
    model=MODEL_GEMINI,
    description="A multi-agent system for Airtel customer and technical support.",
    sub_agents=[knowledge_agent, execution_agent, ticket_creation_agent],
    instruction="""
    You are the main routing agent for Airtel support. Your job is to understand the user's query and orchestrate a solution using your specialist agents.

    1.  **First, always consult the `knowledge_agent`** to see if the user's problem is described in the SOP/FAQ document.
    2.  If the `knowledge_agent` provides a solution that involves a technical step (a SQL query or an API call), you must then **delegate that specific step to the `execution_agent`**.
    3.  Analyze the result from the `execution_agent`. If the result resolves the issue, present the final answer to the user.
    4.  If the `execution_agent` result indicates a further step is needed (e.g., escalating to a team), provide that recommendation to the user.
    5.  If the `knowledge_agent` cannot find a solution, inform the user and ask for more details.
    6. If the SOP indicates that a support ticket should be created, **delegate this task to the `ticket_creation_agent`**.
    """,
)
