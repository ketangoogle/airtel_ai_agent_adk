from google.adk.agents import LlmAgent
from .sub_agents.knowledge_agent.agent import knowledge_agent
from .sub_agents.execution_agent.agent import execution_agent
from dotenv import load_dotenv
from google.adk.tools import FunctionTool
import pandas as pd

load_dotenv()

# Use a valid and available Gemini model name
MODEL_GEMINI = "gemini-2.0-flash"
FAQ_CSV_FILE_PATH = "FAQ.csv" 


# --- Agent Definitions ---
def update_faq_csv(question: str, answer: str) -> dict:
    """
    Appends a new question and answer to the FAQ.csv file.
    Checks for duplicates before adding.
    """
    try:
        # Read the existing FAQ file
        faq_df = pd.read_csv(FAQ_CSV_FILE_PATH)

        # Check if the question already exists to prevent duplicates
        if question in faq_df['question'].values:
            return {"status": "skipped", "reason": "Question already exists in FAQ."}

        # Create a new DataFrame for the new row
        new_row = pd.DataFrame([{'question': question, 'answer': answer}])

        # Append the new row and save the file
        updated_faq_df = pd.concat([faq_df, new_row], ignore_index=True)
        updated_faq_df.to_csv(FAQ_CSV_FILE_PATH, index=False)

        return {"status": "success", "message": f"Successfully added new entry to {FAQ_CSV_FILE_PATH}"}

    except FileNotFoundError:
        return {"status": "error", "message": f"File not found: {FAQ_CSV_FILE_PATH}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to update FAQ file: {e}"}

# --- Tool Definition ---
faq_update_tool = FunctionTool(
    func=update_faq_csv
)


root_agent = LlmAgent(
    name="airtel_support_agent",
    model=MODEL_GEMINI,
    description="A multi-agent system for Airtel customer and technical support.",
    sub_agents=[knowledge_agent, execution_agent],
    tools=[faq_update_tool],
    instruction="""
    You are the main routing agent for Airtel support. Your job is to understand the user's query and orchestrate a solution using your specialist agents.

    1.  **First, always consult the `knowledge_agent`** to see if the user's problem is described in the SOP/FAQ document.
    2.  If the `knowledge_agent` provides a solution that involves a technical step (a SQL query or an API call), you must then **delegate that specific step to the `execution_agent`**.
    3.  Analyze the result from the `execution_agent`. If the result resolves the issue, present the final answer to the user.
    4.  If the `execution_agent` result indicates a further step is needed (e.g., escalating to a team), provide that recommendation to the user.
    5.  If the `knowledge_agent` cannot find a solution, inform the user and ask for more details.
    """,
)
