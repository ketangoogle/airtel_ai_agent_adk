import psycopg2 
from typing import Dict
from dotenv import load_dotenv
import datetime
from app.services.cloud_connection import get_cloud_sql_connection
load_dotenv()

def run_sql(query: str) -> dict:
    """
    Connects to the PostgreSQL database, executes a query, and returns a JSON-serializable result.
    It now handles datetime objects by converting them to ISO 8601 strings.
    """
    conn = None
    try:
        conn = get_cloud_sql_connection()
        cursor = conn.cursor()
        cursor.execute(query)

        if cursor.description:
            colnames = [desc[0] for desc in cursor.description]
            records = cursor.fetchall()
            
            processed_records = []
            for record in records:
                row_dict = {}
                for i, col in enumerate(colnames):
                    value = record[i]
                    # CORRECTED TYPE CHECK
                    if isinstance(value, datetime.datetime): 
                        row_dict[col] = value.isoformat() 
                    else:
                        row_dict[col] = value
                processed_records.append(row_dict)
            result = processed_records
        else:
            result = {"status": "success", "rows_affected": cursor.rowcount}

        conn.commit()
        cursor.close()
        return {"result": result}
    except (Exception, psycopg2.Error) as e:
        return {"error": f"Database error: {e}"}
    finally:
        if conn is not None:
            conn.close()
