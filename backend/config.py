import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

class Settings:
    # Database
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")

    # Listener
    LIS_HOST = os.getenv("LIS_HOST")
    LIS_PORT = int(os.getenv("LIS_PORT", 5001))

    # Atellica Client
    ATELLICA_HOST = os.getenv("ATELLICA_HOST")
    ATELLICA_PORT = int(os.getenv("ATELLICA_PORT", 15000))

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # Logging
    LOG_DIR = os.getenv("LOG_DIR", "atellica_logs")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

settings = Settings()
