from database import cursor, db
from utils import log_event

def save_to_db(patient, order, results):
    if not db.is_connected():
        db.reconnect()

    try:
        # 1. Identify Barcode/Sample ID
        barcode = order.get('order_id') or order.get('placer_order') or patient.get('patient_id')
        
        if not barcode:
            log_event('error', "Skipping insert: No Barcode found in data.")
            return

        patient_name = patient.get('patient_name', 'Unknown')

        # 2. Check/Insert Sample (Essential for Frontend Sidebar)
        cursor.execute("SELECT id FROM samples WHERE barcode = %s", (barcode,))
        exists = cursor.fetchone()

        if not exists:
            # Create new pending sample
            cursor.execute("""
                INSERT INTO samples (patient_name, barcode, collection_time, status)
                VALUES (%s, %s, NOW(), 'PENDING')
            """, (patient_name, barcode))
            log_event('status', f"New Sample Created: {barcode}")
        
        # 3. Insert Results
        for r in results:
            # Check for QC or empty test codes
            test_code = r.get('test_code', '')
            if not test_code: continue

            # Insert Result
            cursor.execute("""
                INSERT INTO results 
                (sample_barcode, test_name, result_value, unit, ref_range, flag)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                barcode,
                test_code,
                r.get('result_value'),
                r.get('unit'),
                r.get('ref_range'),
                r.get('abnormal_flag')
            ))

        db.commit()
        
        # LOGGING SUCCESS (This writes to results.log)
        log_msg = f"Saved {len(results)} results for {patient_name} (Barcode: {barcode})"
        log_event('result', log_msg)
        print(f"   💾 DB SUCCESS: {log_msg}") # Print to terminal to confirm

    except Exception as e:
        db.rollback()
        log_event('error', f"DB Insert Failed: {e}")
        print(f"   ❌ DB ERROR: {e}")