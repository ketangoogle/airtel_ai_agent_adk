from fastapi import FastAPI

# Initialize the FastAPI application
# You can add metadata which will be displayed in the automatic docs
app = FastAPI(
    title="Airtel Support Knowledge Base API",
    description="This API provides access to Standard Operating Procedures (SOPs) and Frequently Asked Questions (FAQs).",
)

# --- Data for SOPs (Standard Operating Procedures) ---
# This data is sourced from the provided "Airtel Support: SOP & FAQ Document".
SOP_DATA = {
    "document_title": "SOP (Standard Operating Procedures) - Technical Challenges",
    "procedures": [
        {
            "id": "SOP01",
            "title": "DTH Activation Stuck at 'Activation In Progress'",
            "issue": "A DTH installation order is complete, but the status in the system remains 'Activation In Progress'. This usually means the final activation confirmation (QMS callback) was not received from the DTH platform.",
            "plan_of_action": [
                "Confirm the Issue: First, I need to check the database to verify that the DTH order is actually stuck with an 'Activation In Progress' status.",
                "Force the Next Step: If the order is confirmed to be stuck, I will make an API call to manually push the workflow to the 'Completed' state. This should resolve the issue.",
                "Escalate if Needed: If the manual API call fails or returns an error, I cannot solve this alone. I must escalate the problem to the DTH Backend Team, providing them with the order_id and the API error log."
            ],
            "solution_steps": [
                {
                    "step": "a",
                    "description": "Execute this query to confirm the order status:",
                    "command_type": "sql",
                    "command": "select order_id, status, created_date, modified_date from public.task where organisation_process_path='AIRTEL.DTH.INSTALL_AND_FAULT_REPAIR' and task_type='INSTALL' and status = 'Activation In Progress' and order_id in ('DT100987654');"
                },
                {
                    "step": "b",
                    "description": "If the status is confirmed, execute this API call to manually advance the workflow. Remember to use the correct corelation_id:",
                    "command_type": "api_call",
                    "command": "curl --location --request POST 'https://honcho-service.airtelwork.com/honcho/stateJump/{{corelation_id}}' --header 'Content-Type: application/json' --data-raw '{\"createContext\": false, \"nextState\": \"Completed\", \"transitionType\": \"dummy\"}'"
                },
                {
                    "step": "c",
                    "description": "If step (b) fails, raise a ticket to the DTH Backend Team."
                }
            ]
        },
        {
            "id": "SOP02",
            "title": "Broadband Order Stuck in 'Feasibility Check' due to Address Mismatch",
            "issue": "A new broadband order is stuck at the 'Feasibility Check' stage. The logs indicate an error like GIS_BOUNDARY_NOT_FOUND or ADDRESS_PARSE_FAILURE.",
            "plan_of_action": [
                "Check Address Data: The problem is likely related to the customer's address. I will query the database to see if the address information (operating_boundary_path and rsu) is missing for this order.",
                "Escalate to the GIS Team: If the address data is missing, it means our system couldn't map it. I need to raise a ticket with the GIS team so they can manually fix the address data.",
                "Re-push the Order: After the GIS team confirms they have fixed the address, I need to re-process the order using the designated Jenkins job.",
                "Trigger the Jenkins Job: I will access the Jenkins URL, input the order_id, and trigger the build to re-initiate the feasibility check with the corrected data."
            ],
            "solution_steps": [
                {
                    "step": "a",
                    "description": "Check the address details for the given order_id in the task table. You need to retrieve the current status, rsu, and operating_boundary_path for that order."
                },
                {
                    "step": "b",
                    "description": "If operating_boundary_path or rsu is NULL, raise a ticket to the GIS team."
                },
                {
                    "step": "c",
                    "description": "Once the GIS team confirms the fix, use this Jenkins job to re-push the order:",
                    "command_type": "url",
                    "command": "http://jenkins-service.airtelworld.in:8080/job/airtelwork-telemedia-bussiness-automation/build?delay=0sec"
                },
                {
                    "step": "d",
                    "description": "In the Jenkins job, provide the order_id as a parameter and trigger the build."
                }
            ]
        },
        {
            "id": "SOP03",
            "title": "Postpaid Mobile Bill Not Generated (SR in 'Pending with Billing System')",
            "issue": "A customer reports that their monthly postpaid bill has not been generated, and a service request (SR) for this is stuck.",
            "plan_of_action": [
                "Get Order Details: I need to start by getting the key details for this service request from the database, specifically the corelation_id.",
                "Check Billing System Status: Using the corelation_id, I will make an API call to the billing service. This will tell me the current status of the billing cycle for this customer.",
                "Analyze the System's Response: If the cycle is still running, I can inform the user of the expected completion time. If I receive an error like 'Account Not Found in Cycle,' it points to a configuration issue.",
                "Escalate to Billing Operations: If there is a configuration error, I cannot fix it. I will raise a ticket to the Billing Operations Team with all the details I've gathered."
            ],
            "solution_steps": [
                {
                    "step": "a",
                    "description": "First, execute this query to fetch the corelation_id for the SR:",
                    "command_type": "sql",
                    "command": "select order_id, corelation_id, status, created_date from task where order_id in ('SR_POSTPAID_98765');"
                },
                {
                    "step": "b",
                    "description": "Next, use the corelation_id to make this API call to the billing service:",
                    "command_type": "api_call",
                    "command": "curl --location --request GET 'https://billing-service.airtelwork.com/api/v1/cycle/status/{{corelation_id}}' --header 'Authorization: Bearer {token}'"
                },
                {
                    "step": "c",
                    "description": "Analyze the API response: {\"status\": \"CYCLE_RUNNING\", ...} -> Inform user of the delay. {\"status\": \"ERROR\", \"errorCode\": \"B-501\", ...} -> Proceed to the next step."
                },
                {
                    "step": "d",
                    "description": "If a configuration error is found, raise a ticket to the Billing Operations Team. Include the order_id, corelation_id, and the full API response from step (b)."
                }
            ]
        }
    ]
}


# --- Data for FAQs (Frequently Asked Questions) ---
# This data is sourced from the provided "Airtel Support: SOP & FAQ Document".
FAQ_DATA = {
    "document_title": "FAQ (Frequently Asked Questions) - Customer Challenges",
    "questions": [
        {
            "id": "FAQ01",
            "question": "What should I do if the 'LOS' light on my broadband router is blinking red?",
            "answer": "A red blinking 'LOS' (Loss of Signal) light indicates a problem with the incoming fiber optic signal. Please follow these steps: Check Physical Connection: Ensure the thin green fiber optic cable is securely plugged into the back of your router and into the wall socket. It should 'click' into place. Inspect the Cable: Look for any sharp bends, cuts, or damage along the length of the fiber cable. The cable is delicate and can be easily damaged. Reboot Your Router: Turn off the power to your router, wait for 30 seconds, and then turn it back on. Wait for 2-3 minutes for the lights to stabilize. Contact Support: If the 'LOS' light is still red after these steps, it signifies an issue with the external fiber line in your area. Please use the Airtel Thanks App to raise a service request or call our customer care for assistance. A field engineer will need to investigate."
        },
        {
            "id": "FAQ02",
            "question": "My mobile data is very slow even though I have 4G/5G coverage.",
            "answer": "Slow data speeds can be caused by several factors. Here are a few quick things you can try: Toggle Airplane Mode: The simplest fix is often to turn Airplane Mode on for 10 seconds and then turn it off. This forces your phone to reconnect to the nearest cell tower. Restart Your Phone: A simple restart can resolve many temporary network glitches. Check for Local Outages: Use the Airtel Thanks App to check if there are any reported network outages or maintenance activities in your specific area. Reset Network Settings: If the problem persists, you can try resetting your phone's network settings. On iPhone: Go to Settings > General > Transfer or Reset iPhone > Reset > Reset Network Settings. On Android: Go to Settings > System > Reset options > Reset Wi-Fi, mobile & Bluetooth. Note: This will erase your saved Wi-Fi passwords, so you will need to re-enter them. If none of these steps work, please contact customer support."
        },
        {
            "id": "FAQ03",
            "question": "I can send text messages (SMS), but I am not receiving any.",
            "answer": "This issue is usually related to your device settings or SIM card. Please try the following: Check Phone Storage: If your phone's internal memory or inbox is full, it can prevent new messages from being received. Delete old messages and files to free up space. Review Block List: Make sure you haven't accidentally blocked the numbers you are expecting messages from. Check your phone's call and message blocking settings. Restart Your Device: Turn your phone off and on again. This can often solve the problem. Re-insert SIM Card: Power off your phone, carefully remove the SIM card, wipe it with a soft, dry cloth, and re-insert it correctly. Power your phone back on. Check in Another Phone: If possible, insert your SIM card into a different phone. If you start receiving messages on the other phone, the issue is with your device settings. If you still don't receive messages, the problem might be with your SIM or our network service provisioning. In this case, please contact customer care."
        }
    ]
}


@app.get("/")
def read_root():
    """
    Root endpoint to confirm the server is running.
    """
    return {"message": "API Server is running. Go to /docs for interactive API documentation."}


@app.get("/api/faq", tags=["Knowledge Base"])
def get_faqs() -> dict:
    """
    API endpoint to serve the FAQ data. FastAPI automatically converts dict to JSON.
    """
    return FAQ_DATA


@app.get("/api/sop", tags=["Knowledge Base"])
def get_sops() -> dict:
    """
    API endpoint to serve the SOP data. FastAPI automatically converts dict to JSON.
    """
    return SOP_DATA
