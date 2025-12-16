import socket
import mysql.connector
from datetime import datetime

# ==========================
# MySQL Connection & Setup
# ==========================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "root"
DB_NAME = "nmc_check"

db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS
)
cursor = db.cursor()

# ==========================
# Create database if not exists
# ==========================
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
db.database = DB_NAME

# ==========================
# Patients table
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(50) UNIQUE,
    patient_name VARCHAR(255),
    dob DATE NULL,
    gender VARCHAR(10) NULL,
    timestamp DATETIME
)
""")
# ==========================
# Orders table
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(50),
    order_id VARCHAR(50),
    test_codes TEXT,
    sample_type VARCHAR(50),
    order_timestamp DATETIME,
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
)
""")
# ==========================
# Results table
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(50),
    test_code VARCHAR(50),
    result_value VARCHAR(50),
    unit VARCHAR(20),
    flag VARCHAR(5),
    result_timestamp DATETIME,
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
)
""")
# ==========================
# Listener log table
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS listener_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_time DATETIME,
    event_type VARCHAR(50),
    message TEXT
)
""")
db.commit()

# ==========================
# ASTM Control Characters
# ==========================
ENQ = b'\x05'
ACK = b'\x06'
EOT = b'\x04'
STX = b'\x02'
ETX = b'\x03'
CR = b'\x0D'


# ==========================
# Logging Function
# ==========================
def log_event(event_type, message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {event_type}: {message}")
    cursor.execute("""
        INSERT INTO listener_log (event_time, event_type, message)
        VALUES (%s, %s, %s)
    """, (datetime.now(), event_type, message))
    db.commit()


# ==========================
# Parser Function
# ==========================
def parse_frame(frame):
    message = frame.decode(errors='ignore')
    lines = message.split('\r')
    patient = {}
    order = {}
    results = []

    for line in lines:
        parts = line.split('|')
        # ==========================
        # Patient Segment
        # ==========================
        if line.startswith('P|'):
            patient['patient_id'] = parts[2].strip() if len(parts) > 2 else None
            patient['patient_name'] = parts[5].strip() if len(parts) > 5 else None
            dob_raw = parts[7].strip() if len(parts) > 7 else None
            # DOB
            dob_raw = parts[7].strip() if len(parts) > 7 and parts[7].strip() else None
            if dob_raw:
                try:
                    patient['dob'] = datetime.strptime(dob_raw, "%Y%m%d").date()
                except:
                    patient['dob'] = None
            else:
                patient['dob'] = None
            # Gender
            gender_raw = parts[8].strip() if len(parts) > 8 and parts[8].strip() else None
            patient['gender'] = gender_raw[0] if gender_raw else None

            patient['timestamp'] = datetime.now()

        # ==========================
        # Order Segment
        # ==========================
        elif line.startswith('O|'):
            order['patient_id'] = patient.get('patient_id')
            order['order_id'] = parts[1].strip() if len(parts) > 1 else None
            # ==========================
            # Test Code
            # ==========================
            if len(parts) > 4 and parts[4].strip():
                order['test_codes'] = ','.join([t.strip() for t in parts[4].split('\\') if t.strip()])
            else:
                order['test_codes'] = None
                # ==========================
                # Sample type: last non-empty field after order date (field 7+)
                # ==========================
            order['sample_type'] = None
            for field in reversed(parts[5:]):
                if field.strip() and not field.startswith('R|') and not field.startswith('L|'):
                    order['sample_type'] = field.strip()
                    break

        # ==========================
        # Result Segment
        # ==========================
        elif line.startswith('R|'):
            test_code = None
            if len(parts) > 2:
                for p in parts[2].split('^'):
                    if p.strip():
                        test_code = p.strip()
                        break
            results.append({
                'patient_id': patient.get('patient_id'),
                'test_code': test_code,
                'result_value': parts[3].strip() if len(parts) > 3 else None,
                'unit': parts[4].strip() if len(parts) > 4 else None,
                'flag': parts[5].strip() if len(parts) > 5 else None,
                'result_timestamp': datetime.now()
            })

    return patient, order, results


# ==========================
# Data Insert
# ==========================
def save_to_db(patient, order, results):
    try:
        # Patients
        cursor.execute("""
            INSERT INTO patients (patient_id, patient_name, dob, gender, timestamp)
            VALUES (%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE patient_name=%s
        """, (
            patient.get('patient_id'),
            patient.get('patient_name'),
            patient.get('dob'),
            patient.get('gender'),
            patient.get('timestamp'),
            patient.get('patient_name')
        ))
        db.commit()
        log_event("DB_INSERT", f"Patient inserted/updated: {patient.get('patient_id')}")

        # Orders
        cursor.execute("""
            INSERT INTO orders (patient_id, order_id, test_codes, sample_type, order_timestamp)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            order.get('patient_id'),
            order.get('order_id'),
            order.get('test_codes'),
            order.get('sample_type'),
            order.get('order_timestamp')
        ))
        db.commit()
        log_event("DB_INSERT", f"Order inserted: {order.get('order_id')}")

        # Results
        for r in results:
            cursor.execute("""
                INSERT INTO results (patient_id, test_code, result_value, unit, flag, result_timestamp)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                r.get('patient_id'),
                r.get('test_code'),
                r.get('result_value'),
                r.get('unit'),
                r.get('flag'),
                r.get('result_timestamp')
            ))
        db.commit()
        log_event("DB_INSERT", f"{len(results)} Results inserted for patient {patient.get('patient_id')}")

    except Exception as e:
        log_event("ERROR", f"DB insert failed: {e}")


# ==========================
# Listener Segment
# ==========================
HOST = '0.0.0.0'
PORT = 8002

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    log_event("LISTENER_START", f"ASTM Listener running on {HOST}:{PORT}")

    conn, addr = s.accept()
    with conn:
        log_event("CONNECTION", f"Connected by {addr}")
        buffer = b""

        while True:
            data = conn.recv(1024)
            if not data:
                log_event("DISCONNECT", f"Client {addr} disconnected")
                break

            # ENQ handshake
            if data == ENQ:
                conn.sendall(ACK)
                log_event("HANDSHAKE", "ENQ received, ACK sent")
                continue

            # Frame
            if data.startswith(STX):
                buffer += data[1:-3]  # remove STX and ETX+checksum+CR
                log_event("FRAME_RECEIVED", buffer.decode(errors='ignore'))
                patient, order, results = parse_frame(buffer)
                log_event("PARSE", f"Patient: {patient}, Order: {order}, Results: {results}")
                save_to_db(patient, order, results)
                conn.sendall(ACK)
                buffer = b""

            # EOT
            if data == EOT:
                log_event("EOT", "Transmission completed")
                break
