# setup_database.py
# This script initializes the database for the Airtel Support Agent using Python.
# It connects to the PostgreSQL database, creates the 'task' table,
# and populates it with dummy data for testing SOP scenarios
import os
import psycopg2
from psycopg2 import sql, OperationalError

def get_db_connection():
    """Establishes a connection to the PostgreSQL database using environment variables."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("PG_HOST", "localhost"),
            dbname=os.environ.get("PG_DBNAME", "airtel_db"),
            user=os.environ.get("PG_USER", "postgres"),
            password=os.environ.get("PG_PASSWORD"),
            port=os.environ.get("PG_PORT", 5432)
        )
        return conn
    except OperationalError as e:
        print(f"🔴 Error: Could not connect to the database.")
        print("Please ensure that PostgreSQL is running and that your environment variables (PG_HOST, PG_DBNAME, PG_USER, PG_PASSWORD, PG_PORT) are set correctly.")
        raise e

def setup_database():
    """
    Executes the full database setup: drops the existing table,
    creates a new one, and inserts all dummy data.
    """
    # SQL commands are stored in a list for sequential execution.
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
        ('SR_POSTPAID_98765', 'cor_postpaid_bill_789', 'Pending with Billing System', '2025-06-27T12:00:00Z', 'BILLING', 'AIRTEL.POSTPAID.BILLING');
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
        ('ONSITE_ISSUE_101', 'Reached Onsite', 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR', '9860434407', '2025-02-15T11:00:00Z', 'Fault Repair');
        """
    ]

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        print("✅ Database connection successful. Setting up tables...")

        # Execute each command
        for command in commands:
            cur.execute(command)

        # Commit the changes
        conn.commit()
        cur.close()
        print("✅ Database initialization complete. The 'task' table has been created and populated.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"🔴 Error during database setup: {error}")
        if conn is not None:
            conn.rollback() # Roll back the transaction on error
    finally:
        if conn is not None:
            conn.close()
            print("Connection closed.")

if __name__ == '__main__':
    # This block runs when the script is executed directly from the command line.
    # To run this script:
    # 1. Make sure your virtual environment is activated.
    # 2. Ensure your PostgreSQL environment variables are set.
    # 3. Run 'python setup_database.py' in your terminal.
    setup_database()
