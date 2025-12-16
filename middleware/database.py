import mysql.connector
from config import settings

try:
    db = mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASS,
        database=settings.DB_NAME
    )
    cursor = db.cursor(dictionary=True)
    print("Middleware connected to Database successfully.")
except Exception as e:
    print(f"Middleware DB Connection Error: {e}")

# This function helps keep the connection alive
def get_db_connection():
    if not db.is_connected():
        db.reconnect()
    return db