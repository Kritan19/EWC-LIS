import os

class Settings:
    # --- DATABASE CONFIG ---
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASS = "root"    
    DB_NAME = "lims_db" 

    # --- LISTENER CONFIG ---
    LIS_HOST = "0.0.0.0"
    LIS_PORT = 5001     # Port for the Machine to connect

    # --- LOGGING ---
    LOG_DIR = "atellica_logs"
    LOG_LEVEL = "DEBUG"

settings = Settings()