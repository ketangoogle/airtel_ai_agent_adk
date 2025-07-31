import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Application settings loaded from environment variables.
    """
    PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT") 
    CLOUD_SQL_CONNECTION_NAME: str = os.getenv("CLOUD_SQL_CONNECTION_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")
settings = Settings()
if not all([settings.CLOUD_SQL_CONNECTION_NAME, settings.DB_USER, settings.DB_PASSWORD, settings.DB_NAME]):
    raise ValueError("One or more required Cloud SQL environment variables are not set. Please check your .env file.")
