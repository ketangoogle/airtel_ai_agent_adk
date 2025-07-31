import os
from google.cloud.sql.connector import Connector, IPTypes
import pg8000.dbapi
from dotenv import load_dotenv

load_dotenv()

cloud_sql_connector = None

def get_cloud_sql_connection():
    """
    Establishes and returns a connection to the PostgreSQL database 
    using the Cloud SQL Python Connector.
    """
    global cloud_sql_connector
    instance_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")

    if not all([instance_connection_name, db_user, db_password, db_name]):
        print("🔴 Error: Missing one or more required environment variables for Cloud SQL.")
        print("Please set CLOUD_SQL_CONNECTION_NAME, DB_USER, DB_PASSWORD, and DB_NAME in your .env file.")
        raise ValueError("Cloud SQL environment variables not set.")

    try:
        # Initialize the connector if it hasn't been already
        if cloud_sql_connector is None:
        
            ip_type = IPTypes.PUBLIC 
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
        print(f"🔴 Error: Could not connect to the Cloud SQL database.")
        print(f"Please ensure CLOUD_SQL_CONNECTION_NAME ('{instance_connection_name}') is correct,")
        print(f"and that your application has permission (Cloud SQL Client role) to connect.")
        raise e

def close_connector():
    """
    Closes the global connector to release resources.
    Should be called when the application is shutting down.
    """
    global cloud_sql_connector
    if cloud_sql_connector:
        cloud_sql_connector.close()
        print("Cloud SQL Connector resources released.")

