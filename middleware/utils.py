import os
import time
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from database import cursor, db  # Imports from local middleware/database.py

# ==========================
# ASTM Constants
# ==========================
ENQ = b'\x05'
ACK = b'\x06'
EOT = b'\x04'
STX = b'\x02'
ETX = b'\x03'
CR = b'\x0D'

# ==========================
# Database Logging
# ==========================
def log_event(event_type, message):
    """Logs significant events to the MySQL database."""
    try:
        # Reconnect if needed
        if not db.is_connected():
            db.reconnect()
            
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {event_type}: {message}")
        cursor.execute("""
            INSERT INTO listener_log (event_time, event_type, message)
            VALUES (%s, %s, %s)
        """, (datetime.now(), event_type, str(message)))
        db.commit()
    except Exception as e:
        print(f"!!! Failed to log event to DB: {e}")

# ==========================
# File Logging Setup
# ==========================
LOG_FOLDER = "logs"
RAW_FOLDER = "raw_frames"

os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(RAW_FOLDER, exist_ok=True)

def setup_logger():
    logger = logging.getLogger("middleware_logger")
    logger.setLevel(logging.DEBUG)

    # Prevent adding duplicate handlers if function is called twice
    if logger.hasHandlers():
        return logger

    # 1. File Handler (Rotates after 5MB)
    file_handler = RotatingFileHandler(
        os.path.join(LOG_FOLDER, "middleware.log"),
        maxBytes=5*1024*1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(file_handler)

    # 2. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s"))
    logger.addHandler(console_handler)

    return logger

log = setup_logger()

# ==========================
# Cleanup Functions
# ==========================
def cleanup_old_raw_files(days=7):
    """Delete raw frame files older than `days`."""
    now = time.time()
    cutoff = now - (days * 86400)
    if not os.path.exists(RAW_FOLDER):
        return

    for filename in os.listdir(RAW_FOLDER):
        file_path = os.path.join(RAW_FOLDER, filename)
        if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff:
            try:
                os.remove(file_path)
                log.info(f"Deleted old raw file: {filename}")
            except Exception as e:
                log.error(f"Error deleting {filename}: {e}")

def cleanup_old_logs(days=30):
    """Delete log files older than `days`."""
    now = time.time()
    cutoff = now - (days * 86400)
    if not os.path.exists(LOG_FOLDER):
        return

    for filename in os.listdir(LOG_FOLDER):
        file_path = os.path.join(LOG_FOLDER, filename)
        if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff:
            try:
                os.remove(file_path)
                log.info(f"Deleted old log file: {filename}")
            except Exception as e:
                log.error(f"Error deleting {filename}: {e}")