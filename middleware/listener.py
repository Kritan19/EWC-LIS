import socket
import os
import time
from config import settings
from database import db
from parser import parse_frame
from db_insert import save_to_db
from utils import ENQ, ACK, EOT, STX, ETX, log_event, RAW_FOLDER, log, cleanup_old_raw_files, cleanup_old_logs

HOST = settings.LIS_HOST
PORT = settings.LIS_PORT

def start_listener():
    # 1. Cleanup old logs
    try:
        cleanup_old_raw_files()
        cleanup_old_logs()
    except Exception as e:
        print(f"⚠️ Warning during cleanup: {e}")

    print(f"\n--- STARTING LISTENER ON {HOST}:{PORT} ---")

    # 2. Start Socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((HOST, PORT))
            s.listen(5)
            print("✅ WAITING FOR MACHINES...")
            log.info(f"ASTM Middleware Listening on {HOST}:{PORT}")
        except Exception as e:
            print(f"❌ PORT ERROR: {e}")
            return

        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    print(f"\n🔌 CONNECTED: {addr}")
                    patient_buffers = {} 

                    while True:
                        data = conn.recv(4096)
                        if not data:
                            print("🔌 DISCONNECTED (No Data)")
                            break
                        
                        # Debug Print
                        print(f"RAW RECEIVED: {data}")

                        # 1. Handle Handshake
                        if ENQ in data:
                            conn.sendall(ACK)
                            print("   -> Handshake (ACK Sent)")
                            continue

                        # 2. Handle ASTM Data (STX)
                        if STX in data:
                            segments = data.split(STX)
                            for seg in segments:
                                if not seg: continue
                                if ETX in seg:
                                    frame_content, _ = seg.split(ETX, 1)
                                    process_data(frame_content)
                                    conn.sendall(ACK)
                        
                        # 3. Handle Raw Data (Fallback)
                        elif b'H|' in data or b'P|' in data or b'O|' in data:
                            print("   ⚠️ RAW DATA DETECTED - Processing...")
                            process_data(data)
                            conn.sendall(ACK)

                        if EOT in data:
                            print("   -> End of Transmission.")

            except Exception as e:
                print(f"❌ CONNECTION ERROR: {e}")

def process_data(raw_bytes):
    """Helper to parse and save data"""
    try:
        # Convert bytes to string for printing
        raw_text = raw_bytes.decode(errors='ignore')
        print(f"   📜 PROCESSING: {raw_text[:30]}...") 
        
        # Save raw file for debugging
        save_raw_file(raw_text)

        # Parse
        patient, order, results = parse_frame(raw_bytes)
        
        if patient.get('patient_name'):
            print(f"   ✅ IDENTIFIED: {patient.get('patient_name')}")
            save_to_db(patient, order, results)
        else:
            print("   ⚠️ NO PATIENT NAME FOUND IN DATA")
            
    except Exception as e:
        print(f"   ❌ PROCESSING ERROR: {e}")

def save_raw_file(text):
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(RAW_FOLDER, f"data_{date_str}.txt")
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}]\n{text}\n\n")
    except Exception as e:
        print(f"Could not save raw file: {e}")

# --- THIS IS THE PART THAT WAS LIKELY MISSING ---
if __name__ == "__main__":
    start_listener()