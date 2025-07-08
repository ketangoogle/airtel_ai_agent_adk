from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
import os
import time
from typing import Dict, Any

MODEL_GEMINI = "gemini-2.0-flash"

def create_ticket_api_call(ticket_details:Dict[str, Any]) -> dict:
    """
    Simlulates the creation of a new support ticket with a hardcoded/generated ID, without making an actual API call.
    Args: 
        ticket_details(Dict[str,Any]): A dictionary conntaining details for the ticket, such as subject,decription,customer_id, etc.

    Returns:
         dict: A dictionary indicating the status of the ticket creation (success/faliure) and the generated ticket ID.
    
    """
    print(f"Creating ticket with details: {ticket_details}")    

    try:
        # Simulate a unique ticket using cureent timestamp and a hash of details
        #This will create a "hardcoded" simulation without needing an actual API. 
        simulated_ticket_id = f"SIM-TKT- {int(time.time() *1000)- abs(hash(str(ticket_details)) % 10000)}"

        return {
            "status": "success",
            "ticket_id": simulated_ticket_id,
            "message": f"Simulated ticket '{simulated_ticket_id}' created successfully with provided details."
        }
    except Exception as e:
        print(f"ðŸ”´ Error: Failed to create ticket. {str(e)}")
        return {
            "status": "failure",
            "message": f"Failed to create ticket: {str(e)}"
        }
create_ticket_tool = FunctionTool(
    func = create_ticket_api_call,
)
ticket_creation_agent = LlmAgent(
    name = "ticket_creation_agent",
    model = MODEL_GEMINI,
    description = "Creates support tickets based on user requests.",
    instruction="""
    You are a specialized agent responsible for creating new support tickets.
    You will receive instructions from the main agent, including the necessary details to create a ticket.
    Your primary function is to call the `create_ticket_api_call` tool with the provided `ticket_details`.
    
    **Input:** Expect a dictionary of `ticket_details` which should contain at least:
    - `subject` (str): A brief description of the issue.
    - `description` (str): Detailed information about the problem.
    - `customer_id` (str, optional): The ID of the affected customer.
    - `priority` (str, optional): The urgency of the ticket (e.g., 'Low', 'Medium', 'High', 'Urgent').
    - `category` (str, optional): The category of the issue (e.g., 'Billing', 'Technical', 'Network').

    **Process:**
    1. Extract all relevant `ticket_details` from the instruction. Ensure all required fields (`subject`, `description`) are present.
    2. Call the `create_ticket_api_call` tool with these details.
    3. Report the outcome (success/failure and ticket ID if successful) back to the main agent.
    """,
    tools=[create_ticket_tool]
)