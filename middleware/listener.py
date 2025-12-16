import socket
import os
from datetime import datetime
from config import settings
from database import db, cursor
from parser import parse_frame
from db_insert import save_to_db
from utils import ENQ, ACK, EOT, STX, ETX, log_event, RAW_FOLDER, log, cleanup_old_raw_files, cleanup_old_logs

HOST = settings.LIS_HOST
PORT = settings.LIS_PORT

def start_listener():
    # Run cleanup tasks at startup
    cleanup_old_raw_files()
    cleanup_old_logs()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((HOST, PORT))
            s.listen(5)
            log.info(f"ASTM Middleware Listening on {HOST}:{PORT}")
            log_event("STARTUP", f"Listener started on {HOST}:{PORT}")
        except Exception as e:
            log.error(f"Failed to bind port: {e}")
            return

        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    log.info(f"Machine Connected: {addr}")
                    log_event("CONNECT", f"Connection from {addr}")
                    
                    patient_buffers = {} # Buffer for split frames

                    while True:
                        data = conn.recv(4096)
                        if not data:
                            log.info(f"Machine {addr} disconnected")
                            break

                        # 1. Handle Handshake
                        if data == ENQ:
                            conn.sendall(ACK)
                            log.debug("Received ENQ -> Sent ACK")
                            continue

                        # 2. Handle End of Transmission
                        if data == EOT:
                            log.info("Received EOT (End of Transmission)")
                            break

                        # 3. Handle Data Frames
                        if STX in data:
                            # Split multiple frames if stuck together
                            segments = data.split(STX)
                            for seg in segments:
                                if not seg: continue
                                
                                # Check if frame is complete (has ETX)
                                if ETX in seg:
                                    # Extract content up to ETX
                                    frame_content, _ = seg.split(ETX, 1)
                                    
                                    # Handle partial buffers
                                    if "partial" in patient_buffers:
                                        frame_content = patient_buffers["partial"] + frame_content
                                        patient_buffers["partial"] = b""

                                    # Save Raw Data
                                    raw_text = frame_content.decode(errors='ignore')
                                    save_raw_file(raw_text)

                                    # Parse Data
                                    try:
                                        patient, order, results = parse_frame(frame_content)
                                        log.info(f"Parsed: {len(results)} results for {patient.get('patient_name', 'Unknown')}")
                                        
                                        # Insert into Database
                                        save_to_db(patient, order, results)
                                    except Exception as e:
                                        log.error(f"Parsing Error: {e}")
                                        log_event("PARSE_ERROR", str(e))

                                    # Acknowledge Receipt
                                    conn.sendall(ACK)
                                else:
                                    # Store partial frame
                                    patient_buffers["partial"] = seg

            except Exception as e:
                log.error(f"Connection Error: {e}")
                log_event("ERROR", str(e))

def save_raw_file(text):
    """Saves raw instrument data to a text file for debugging"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(RAW_FOLDER, f"data_{date_str}.txt")
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}]\n{text}\n\n")
    except Exception as e:
        log.error(f"Could not save raw file: {e}")

if __name__ == "__main__":
    start_listener()