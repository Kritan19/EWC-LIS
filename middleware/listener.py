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
    cleanup_old_raw_files()
    cleanup_old_logs()

    print(f"--- STARTING DEBUG LISTENER ON {HOST}:{PORT} ---")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((HOST, PORT))
            s.listen(5)
            print("✅ WAITING FOR CONNECTION...")
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
                        # 1. Receive Data
                        data = conn.recv(4096)
                        if not data:
                            print("🔌 DISCONNECTED (No Data)")
                            break
                        
                        # --- DEBUG PRINT: SHOW EXACTLY WHAT WE GOT ---
                        print(f"RAW RECEIVED ({len(data)} bytes): {data}")
                        # ---------------------------------------------

                        # 2. Handle Handshake (ENQ)
                        # We use 'in' instead of '==' to be safer against buffering
                        if ENQ in data:
                            print("   -> Found ENQ (Handshake). Sending ACK...")
                            conn.sendall(ACK)
                            continue

                        # 3. Handle End of Transmission (EOT)
                        if EOT in data:
                            print("   -> Found EOT (End). Transmission Complete.")
                            # We don't break here, in case machines start a new transmission immediately
                            continue

                        # 4. Handle Data Frames (STX ... ETX)
                        if STX in data:
                            print("   -> Found STX (Start of Text). Processing Frame...")
                            segments = data.split(STX)
                            for seg in segments:
                                if not seg: continue
                                
                                if ETX in seg:
                                    frame_content, _ = seg.split(ETX, 1)
                                    
                                    if "partial" in patient_buffers:
                                        frame_content = patient_buffers["partial"] + frame_content
                                        patient_buffers["partial"] = b""

                                    raw_text = frame_content.decode(errors='ignore')
                                    print(f"   📜 DECODED TEXT: {raw_text[:50]}...") # Show first 50 chars

                                    try:
                                        patient, order, results = parse_frame(frame_content)
                                        print(f"   ✅ SAVING: {patient.get('patient_name')} ({len(results)} results)")
                                        save_to_db(patient, order, results)
                                        conn.sendall(ACK)
                                        print("   -> Sent ACK for Frame")
                                    except Exception as e:
                                        print(f"   ❌ PARSING ERROR: {e}")
                                        conn.sendall(ACK) # Ack anyway to keep connection alive
                                else:
                                    print("   -> Partial frame received, buffering...")
                                    patient_buffers["partial"] = seg

            except Exception as e:
                print(f"❌ CONNECTION ERROR: {e}")

if __name__ == "__main__":
    start_listener()