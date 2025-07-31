import sys
import os
import pg8000.dbapi
from app.services.cloud_connection import {
    get_cloud_sql_connection,
    close_connector
}

def setup_database():
    """
    Executes the full database setup: drops the existing table,
    creates a new one, and inserts all dummy data using a centralized connection function.
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
        """
        INSERT INTO task (order_id, corelation_id, status, task_type, organisation_process_path, created_date) VALUES
        ('DT100987654', 'cor_dth_stuck_123', 'Activation In Progress', 'INSTALL', 'AIRTEL.DTH.INSTALL_AND_FAULT_REPAIR', CURRENT_DATE - INTERVAL '2 day');
        """,
        """
        INSERT INTO task (order_id, status, rsu, operating_boundary_path, task_type, organisation_process_path) VALUES
        ('XBB10054321', 'Feasibility Check', NULL, 'OB_PATH_VALID_123', 'INSTALL', 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR');
        """,
        """
        INSERT INTO task (order_id, corelation_id, status, created_date, task_type, organisation_process_path) VALUES
        ('SR_POSTPAID_98765', 'cor_postpaid_bill_789', 'Pending with Billing System', '2025-06-27 12:00:00+00', 'BILLING', 'AIRTEL.POSTPAID.BILLING');
        """,
        """
        INSERT INTO task (order_id, corelation_id, status, one_airtel_suborder, task_type, organisation_process_path) VALUES
        ('XBB_STUCK_999', 'cor_stuck_sub_456', 'Pending', true, 'INSTALL', 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR');
        """,
        """
        INSERT INTO task (order_id, status, task_type, organisation_process_path, common_details) VALUES
        ('10045909651', 'Fault Repair', 'Fault Repair', 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR',
        '{"commonDetails": {"telemedia": {"problemType": "Hardware Related", "problemSubType": "CPE accessories related issues", "productType": "FLVOICE", "ffc": "Jumpering Issues", "rc": "Jumpering issue rectified at MDF or Pillar or Sub Pillar"}}}');
        """,
        """
        INSERT INTO task (order_id, corelation_id, status, one_airtel_suborder, common_details, task_type, organisation_process_path) VALUES
        ('OAOE_ORDER_123', 'cor12345oaoe', 'Installation Engineer Assignment', true,
        '{"commonDetails": {"telemedia": {"bin": "OAOE"}}}', 'INSTALL', 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR');
        """,
        """
        INSERT INTO task (order_id, status, organisation_process_path, pending_with_details, created_date, task_type) VALUES
        ('ONSITE_ISSUE_101', 'Reached Onsite', 'AIRTEL.TELEMEDIA.INSTALLATION___FAULT_REPAIR', '9860434407', '2025-02-15 11:00:00+00', 'Fault Repair');
        """
    ]

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        print("✅ Database connection successful. Setting up tables...")

        for command in commands:
            print(f"Executing: {command.strip().splitlines()[0]}...")
            cur.execute(command)
        conn.commit()
        cur.close()
        print("✅ Database initialization complete. The 'task' table has been created and populated.")

    except (Exception, pg8000.dbapi.Error) as error:
        print(f"🔴 Error during database setup: {error}")
        if conn is not None:
            conn.rollback()
    finally:
        if conn is not None:
            conn.close()
            print("Connection closed.")
        close_connector()

if __name__ == '__main__':
    setup_database()
