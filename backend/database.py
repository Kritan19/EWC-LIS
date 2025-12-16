import mysql.connector
from config import settings  # your Pydantic settings object

# Connect to MySQL using settings
db = mysql.connector.connect(
    host=settings.DB_HOST,
    user=settings.DB_USER,
    password=settings.DB_PASS
)

cursor = db.cursor(dictionary=True)  # optional: get results as dictionaries

# Create database if it doesn't exist
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME}")
db.database = settings.DB_NAME


def setup_tables():
  cursor.execute("""
   CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255)
  )
    """)
  cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id VARCHAR(50) UNIQUE,
        patient_name VARCHAR(255),
        dob DATE NULL,
        gender VARCHAR(10) NULL,
        phone VARCHAR(255) NULL,
        address VARCHAR(255) NULL,
        timestamp DATETIME
    )
    """)

  cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id VARCHAR(50),
        order_id VARCHAR(50) UNIQUE,
        placer_order VARCHAR(50),
        package_id VARCHAR(50),
        run_id INT NULL DEFAULT 0,
        filler_order VARCHAR(50),
        filler_sub VARCHAR(50),
        priority VARCHAR(5),
        order_datetime DATETIME,
        test_codes TEXT,
        sample_type VARCHAR(50),
        order_timestamp DATETIME,
        batch_id VARCHAR(50) NULL,
        batch_timestamp DATETIME NULL,
        FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
    )
    """)

  cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id VARCHAR(50),
        patient_id VARCHAR(50),
        placer_order VARCHAR(50),
        filler_order VARCHAR(50),
        test_code VARCHAR(50),
        result_value VARCHAR(50),
        unit VARCHAR(20),
        ref_range VARCHAR(50),
        abnormal_flag VARCHAR(5),
        result_status VARCHAR(5),
        result_flags VARCHAR(50),
        instrument_id VARCHAR(50),
        result_datetime DATETIME,
        instrument_run_id VARCHAR(50),
        result_timestamp DATETIME,
        FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY(order_id) REFERENCES orders(order_id)
    )
    """)
  cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_results(
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50),
    patient_id VARCHAR(50),
    test_code VARCHAR(50),
    result_value VARCHAR(50),
    unit VARCHAR(20),
    ref_range VARCHAR(50),
    result_datetime DATETIME,
    result_status VARCHAR(10),
    result_flags VARCHAR(50),
    instrument_id VARCHAR(50),
    instrument_run_id VARCHAR(150),
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS qc_config (
  id INT AUTO_INCREMENT PRIMARY KEY,
  analyte VARCHAR(50) NOT NULL,
  level VARCHAR(50) NOT NULL,          -- e.g. "level1", "level2"
  lot VARCHAR(100) NULL,               -- lot number
  target_value DECIMAL(12,6) NULL,
  sd DECIMAL(12,6) NULL,
  unit VARCHAR(20) NULL,
  notes TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (analyte, level, lot)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS qc_runs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  run_id VARCHAR(100) UNIQUE,          -- instrument run id or lab-internal uuid
  qc_config_id INT NULL,               -- optional link to config (if single config)
  instrument_id VARCHAR(100) NULL,
  operator VARCHAR(100) NULL,
  run_datetime DATETIME NULL,
  status VARCHAR(20) DEFAULT 'NEW',    -- NEW,RUNNING,COMPLETED,FAILED,TRANSMITTED
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (qc_config_id) REFERENCES qc_config(id) ON DELETE SET NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS qc_results (
  id INT AUTO_INCREMENT PRIMARY KEY,
  run_id VARCHAR(100),                  -- matches qc_runs.run_id
  qc_config_id INT NULL,                -- optional (for fast lookup)
  test_code VARCHAR(50) NOT NULL,       -- e.g. "GLU", "ALB"
  measured_value DECIMAL(14,6) NULL,
  unit VARCHAR(20) NULL,
  flag VARCHAR(10) NULL,                -- e.g. "N" (normal), "H", "L", or instrument flags
  result_status VARCHAR(10) NULL,       -- e.g. "F" final, "P" preliminary
  instrument_run_id VARCHAR(150) NULL,
  result_datetime DATETIME NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (qc_config_id) REFERENCES qc_config(id) ON DELETE SET NULL
)
 """)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS listener_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        event_time DATETIME,
        event_type VARCHAR(50),
        message TEXT
    )
    """)
db.commit()
