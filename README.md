Airtel Support Agent - Multi-Agent System with ADK
This project demonstrates a multi-agent customer support system for a telecom company like Airtel, built using the Google Agent Development Kit (ADK). The agent is designed to understand user queries, consult a knowledge base, and execute technical tasks like running SQL queries against a PostgreSQL database to solve customer issues.

✨ Features
- Multi-Agent Architecture: Uses a root_agent to orchestrate tasks between a knowledge_agent (for retrieving information) and an execution_agent (for performing actions).

- SQL Generation & Execution: The execution_agent can understand plain English requests, generate the appropriate PostgreSQL query, and run it against the database.

- Knowledge Retrieval: The knowledge_agent is designed to consult an SOP/FAQ document (in this case, Airtel_Support_SOP_FAQ.pdf).

- Database Integration: Connects to a PostgreSQL database to fetch and manage data related to customer support tasks.

🛠️ Setup and Installation
Follow these steps to get the project running on your local machine.

1. Prerequisites
Make sure you have the following installed on your system:

Python (version 3.9 or higher)

PostgreSQL (version 12 or higher)

Google ADK CLI: If you haven't already, install it using pip install google-adk.

2. Project Setup
a. Clone the Repository
``` bash
git clone <your-repo-url>
cd <your-repo-name>
```

b. Create a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.

# Create the virtual environment
``` bash
python3 -m venv .venv
```
# Activate it
``` bash
source .venv/bin/activate
```
c. Install Dependencies
Install all the required Python packages.
``` bash
pip install -r requirements.txt
```
3. PostgreSQL Database Setup
This agent requires a PostgreSQL database to store and retrieve task information.

a. Install PostgreSQL
If you don't have PostgreSQL installed, download it from the official website for your operating system.

b. Create the Database and User
Once installed, open the PostgreSQL command-line tool (psql) and create a new database and a user.

-- Create a new user with a password
``` bash
CREATE USER airtel_agent_user WITH PASSWORD 'your_secure_password';
```

-- Create the database
``` bash
CREATE DATABASE airtel_support OWNER airtel_agent_user;
```

c. Set Environment Variables
The application connects to the database using environment variables. Create a file named .env in the root of your project directory and add the following details.

.env
``` bash
PG_HOST="localhost"
PG_PORT="5432"
PG_DBNAME="airtel_support"
PG_USER="airtel_agent_user"
PG_PASSWORD="your_secure_password"
```

Important: The application will automatically load these variables.

d. Populate the Database
Run the provided Python script to create the necessary tables and fill them with dummy data for testing.
``` bash
python3 setup_database.py
```

You should see a success message indicating that the task table has been created and populated.

🚀 Running the Agent
1. Start the ADK Web Server
From the root of your project directory, run the following command:
``` bash
adk web 
```

2. Access the Development UI
Once the server is running, open your web browser and navigate to the following URL:

http://localhost:8000/dev-ui?app=main_agent

Note: It's important to use the ?app=main_agent parameter to ensure the correct application is loaded, avoiding potential browser caching issues.

🧪 How to Use
Once the UI is loaded, you can test the agent's capabilities. Here are some sample queries you can try:

- The broadband order is stuck in feasibility check

- (After the agent responds) The order ID is XBB10054321

- Find all DTH orders stuck in activation

- A customer with mobile number 9860434407 is unable to have a technician mark their task as 'Reached Onsite'