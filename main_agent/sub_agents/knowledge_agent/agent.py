from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
import pandas as pd
import os

# --- Agent Configuration ---

MODEL_GEMINI = "gemini-2.0-flash"
FAQ_CSV_FILE_PATH = "FAQ.csv" # Path to your FAQ file
SOP_CSV_FILE_PATH = "SOP.csv" # Path to your SOP file

# --- Core Functions ---

def read_csv_knowledge_base(faq_file_path: str, sop_file_path: str) -> str:
    """
    Reads and combines the content of the FAQ and SOP CSV files using pandas.
    It converts the CSV data into a markdown format for the LLM to easily understand.
    """
    try:
        # Read the FAQ and SOP CSV files into pandas DataFrames
        faq_df = pd.read_csv(faq_file_path)
        sop_df = pd.read_csv(sop_file_path)

        # Convert the DataFrames to a clean, readable markdown format
        # This helps the LLM distinguish between the columns and rows
        faq_content = faq_df.to_markdown(index=False)
        sop_content = sop_df.to_markdown(index=False)

        # Combine both contents into a single string for the agent
        combined_content = f"### FAQs\n{faq_content}\n\n### SOPs\n{sop_content}"

        return combined_content

    except FileNotFoundError as e:
        # Handle cases where a file might be missing
        return f"Error: The knowledge base file '{e.filename}' was not found."
    except Exception as e:
        # Handle other potential errors during file reading or processing
        return f"An error occurred while reading the CSV files: {e}"


def get_knowledge_base_content() -> dict:
    """
    A helper function that calls the main reading function with the correct file paths.
    This is wrapped by the FunctionTool.
    """
    content = read_csv_knowledge_base(FAQ_CSV_FILE_PATH, SOP_CSV_FILE_PATH)
    return {"content": content}


# --- Tool and Agent Definitions ---

# The tool that allows the agent to access the knowledge base
knowledge_tool = FunctionTool(
    func=get_knowledge_base_content
)

# The knowledge agent, now with an updated instruction
knowledge_agent = LlmAgent(
    name="knowledge_agent",
    model=MODEL_GEMINI,
    description="Answers user questions by consulting the FAQ and SOP documents.",
    # The instruction is updated to guide the agent on how to use the two new data sources
    instruction="""
You are a meticulous Support Analyst. Your primary function is to consult a knowledge base containing both FAQs and SOPs to find precise answers.

1.  **Analyze the User's Query:** Carefully read the user's problem statement.

2.  **Prioritize FAQs:** First, search the FAQs. Try to find a 'question' that closely matches the user's query. **If you find a direct match**, you must stop and immediately return the result in the following exact JSON format. Do not add any extra text or explanations outside the JSON object.
    `{"source": "FAQ", "question": "The exact question from the FAQ file", "answer": "The corresponding answer from the FAQ file"}`

3.  **Consult SOPs:** If, and only if, you cannot find a suitable answer in the FAQs, search the SOPs. Find an 'Issue' that matches the user's problem. **If you find a relevant SOP**, you must return the result in this exact JSON format. Adhere strictly to this structure.
    `{"source": "SOP", "issue": "The exact issue from the SOP file", "plan_of_action": "The corresponding plan of action", "solution_steps": "The corresponding solution steps"}`
    
4.  **Handle No Solution:** If you exhaust both the FAQs and SOPs and still cannot find a relevant answer, you must return the following specific JSON object:
    `{"source": "None", "answer": "I could not find a solution for this issue in the knowledge base."}`
""",
    tools=[knowledge_tool]
)