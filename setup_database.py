import os
# Import the Cloud SQL Python Connector and a compatible driver (e.g., pg8000)
from google.cloud.sql.connector import Connector, IPTypes
import pg8000.dbapi 
from psycopg2 import sql, OperationalError 
from dotenv import load_dotenv
cloud_sql_connector = None
load_dotenv() 
def get_db_connection():
    """Establishes a connection to the PostgreSQL database via Cloud SQL Proxy."""
    global cloud_sql_connector
    instance_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")

    if not all([instance_connection_name, db_user, db_password, db_name]):
        print("ðŸ”´ Error: Missing one or more required environment variables for Cloud SQL.")
        print("Please set CLOUD_SQL_CONNECTION_NAME, DB_USER, DB_PASSWORD, and DB_NAME.")
        raise ValueError("Cloud SQL environment variables not set.")

    try:
        if cloud_sql_connector is None:
            ip_type = IPTypes.PUBLIC # Or IPTypes.PRIVATE
            cloud_sql_connector = Connector(ip_type=ip_type)
        conn = cloud_sql_connector.connect(
            instance_connection_name,
            "pg8000", 
            user=db_user,
            password=db_password,
            db=db_name,
        )
        return conn
    except Exception as e:
        print(f"ðŸ”´ Error: Could not connect to the Cloud SQL database.")
        print(f"Please ensure CLOUD_SQL_CONNECTION_NAME ('{instance_connection_name}') is correct,")
        print(f"and that your application has permission (Cloud SQL Client role) to connect.")
        raise e

def setup_database():
    """
    Executes the full database setup: drops the existing table,
    creates a new one, and inserts all dummy data.
    """
    commands = [
        # Drop the table if it exists to ensure a clean slate.
        "DROP TABLE IF EXISTS task;",

        # Create the main 'task' table.
        """
        CREATE TABLE task (
            order_id VARCHAR(50) PRIMARY KEY,
            corelation_id VARCHAR(50) UNIQUE,
            status VARCHAR(50),
            task_type VARCHAR(50),
            organisation_process_path VARCHAR(100),
            common_details JSONB,
            one_airtel_suborder BOOLEAN,
            pending_with_details VARCHAR(50),
            rsu VARCHAR(50),
            operating_boundary_path VARCHAR(100),
            created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            modified_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # Add comments to the table and columns for clarity.
        "COMMENT ON TABLE task IS 'Stores tasks for installations, fault repairs, and other customer support scenarios.';",
        "COMMENT ON COLUMN task.order_id IS 'Unique identifier for the customer order or service request.';",
        "COMMENT ON COLUMN task.corelation_id IS 'Correlation ID for tracking across different microservices.';",
        "COMMENT ON COLUMN task.status IS 'The current lifecycle status of the task (e.g., ''Feasibility Check'', ''Activation In Progress'').';",
        "COMMENT ON COLUMN task.common_details IS 'A JSON blob for storing nested, issue-specific details like FFC/RC values.';",
        "COMMENT ON COLUMN task.rsu IS 'Residential Service Unit, relevant for broadband feasibility.';",

        # --- Insert Dummy Data ---

        # SOP #1: DTH Activation Stuck
        """
        INSERT INTO task (order_id, corelation_id, status, task_type, organisation_process_path, created_date) VALUES
        ('DT100987654', 'cor_dth_stuck_123', 'Activation In Progress', 'INSTALL', 'AIRTEL.DTH.INSTALL_AND_FAULT_REPAIR', CURRENT_DATE - INTERVAL '2 day');
        """,

        # SOP #2: Broadband Order Stuck in 'Feasibility Check'
        """
        INSERT INTO task (order_id, status, rsu, operating_boundary_path, task_type, organisation_process_path) VALUES
        ('XBB10054321', 'Feasibility Check', NULL, 'OB_PATH_VALID_123', 'INSTALL', 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR');
        """,

        # SOP #3: Postpaid Bill Not Generated
        """
        INSERT INTO task (order_id, corelation_id, status, created_date, task_type, organisation_process_path) VALUES
        ('SR_POSTPAID_98765', 'cor_postpaid_bill_789', 'Pending with Billing System', '2025-06-27 12:00:00+00', 'BILLING', 'AIRTEL.POSTPAID.BILLING');
        """,

        # SOP #5: Broadband Order Stuck due to Incorrect Sub-Order Flag
        """
        INSERT INTO task (order_id, corelation_id, status, one_airtel_suborder, task_type, organisation_process_path) VALUES
        ('XBB_STUCK_999', 'cor_stuck_sub_456', 'Pending', true, 'INSTALL', 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR');
        """,

        # Older SOP Scenario: FFC RC Issue
        """
        INSERT INTO task (order_id, status, task_type, organisation_process_path, common_details) VALUES
        ('10045909651', 'Fault Repair', 'Fault Repair', 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR',
        '{
          "commonDetails": {
            "telemedia": {
              "problemType": "Hardware Related",
              "problemSubType": "CPE accessories related issues",
              "productType": "FLVOICE",
              "ffc": "Jumpering Issues",
              "rc": "Jumpering issue rectified at MDF or Pillar or Sub Pillar"
            }
          }
        }');
        """,

        # Older SOP Scenario: Order stuck at Installation Engineer Assignment (OAOE Order)
        """
        INSERT INTO task (order_id, corelation_id, status, one_airtel_suborder, common_details, task_type, organisation_process_path) VALUES
        ('OAOE_ORDER_123', 'cor12345oaoe', 'Installation Engineer Assignment', true,
        '{
          "commonDetails": {
            "telemedia": {
              "bin": "OAOE"
            }
          }
        }', 'INSTALL', 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR');
        """,

        # Older SOP Scenario: Unable to mark onsite
        """
        INSERT INTO task (order_id, status, organisation_process_path, pending_with_details, created_date, task_type) VALUES
        ('ONSITE_ISSUE_101', 'Reached Onsite', 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR', '9860434407', '2025-02-15 11:00:00+00', 'Fault Repair');
        """
    ]

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        print("âœ… Database connection successful. Setting up tables...")

        # Execute each command
        for command in commands:
            print(f"Executing: {command.strip().splitlines()[0]}...") # Print first line of command
            cur.execute(command)

        # Commit the changes
        conn.commit()
        cur.close()
        print("âœ… Database initialization complete. The 'task' table has been created and populated.")

    except (Exception, pg8000.dbapi.Error) as error: # Catch pg8000's specific error type
        print(f"ðŸ”´ Error during database setup: {error}")
        if conn is not None:
            conn.rollback() # Roll back the transaction on error
    finally:
        if conn is not None:
            conn.close()
            print("Connection closed.")
        # Ensure the global connector is closed when the script finishes
        global cloud_sql_connector
        if cloud_sql_connector:
            cloud_sql_connector.close()
            print("Cloud SQL Connector resources released.")


if __name__ == '__main__':
    # This block runs when the script is executed directly from the command line.
    # To run this script:
    # 1. Make sure your virtual environment is activated.
    # 2. Set the following environment variables BEFORE running the script:
    #    - CLOUD_SQL_CONNECTION_NAME (e.g., my-gcp-project:asia-south1:my-airtel-pg-instance)
    #    - DB_USER (your PostgreSQL username)
    #    - DB_PASSWORD (your PostgreSQL password)
    #    - DB_NAME (your PostgreSQL database name, e.g., airtel_db)
    # 3. Run 'python setup_database.py' in your terminal.

    # Example of how to set environment variables in bash (for testing):
    # export CLOUD_SQL_CONNECTION_NAME="your-project-id:your-region:your-instance-name"
    # export DB_USER="your_db_user"
    # export DB_PASSWORD="your_db_password"
    # export DB_NAME="airtel_db"
    # python setup_database.py

    setup_database()