import os
import time
import logging
from datetime import datetime
from database import cursor, db

# ==========================
# ASTM Constants
# ==========================
ENQ = b'\x05'
ACK = b'\x06'
EOT = b'\x04'
STX = b'\x02'
ETX = b'\x03'
CR = b'\x0D'
LF = b'\x0A'

# ==========================
# Directories
# ==========================
LOG_DIR = "logs"           # <--- Variable defined here
RAW_FOLDER = "raw_frames"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RAW_FOLDER, exist_ok=True)

# ==========================
# Logging Setup
# ==========================
def setup_logger(name, filename):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent adding duplicate handlers
    if not logger.handlers:
        handler = logging.FileHandler(os.path.join(LOG_DIR, filename))
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Add console handler for the main log only
        if name == 'system':
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            logger.addHandler(console)
            
    return logger

# Specific Loggers
log = setup_logger('system', 'middleware.log')
result_log = setup_logger('results', 'results.log')
error_log = setup_logger('errors', 'error.log')
status_log = setup_logger('status', 'machine_status.log')
qc_log = setup_logger('qc', 'qc.log')

def log_event(category, message):
    """
    Logs to specific files based on category and optionally to DB.
    """
    # 1. File Logging
    msg_str = str(message)
    if category == 'result':
        result_log.info(msg_str)
    elif category == 'error':
        error_log.error(msg_str)
    elif category == 'status' or category in ['STARTUP', 'CONNECT', 'DISCONNECT']:
        status_log.info(f"[{category}] {msg_str}")
    elif category == 'qc':
        qc_log.info(msg_str)
    else:
        log.info(f"[{category}] {msg_str}")

    # 2. Database Logging
    try:
        if not db.is_connected():
            db.reconnect()
        cursor.execute("INSERT INTO listener_log (event_type, message) VALUES (%s, %s)", (category, msg_str))
        db.commit()
    except Exception as e:
        # Avoid infinite recursion if DB log fails
        if category != 'error':
            error_log.error(f"DB Log Failed: {e}")

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
    
    # FIXED: Using LOG_DIR instead of LOG_FOLDER
    if not os.path.exists(LOG_DIR):
        return

    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff:
            try:
                os.remove(file_path)
                log.info(f"Deleted old log file: {filename}")
            except Exception as e:
                log.error(f"Error deleting {filename}: {e}")