from database import cursor, db
from utils import log_event, log

def save_to_db(patient, order, results):
    if not db.is_connected():
        db.reconnect()

    try:
        # 1. INSERT PATIENT (Update name if ID exists)
        # Note: We use 'samples' table as the main patient/order tracking in your simplified DB
        # If you have a separate patients table, uncomment the logic below.
        # For now, we update the 'samples' table based on Barcode (Order ID)
        
        # In your specific ASTM logic, 'patient_id' usually maps to Patient ID
        # and 'order_id' or 'placer_order' maps to Barcode.
        
        barcode = order.get('order_id') or order.get('placer_order')
        
        if not barcode:
            log.warning("No Barcode found in order.kBypassing DB insert.")
            return

        # Ensure sample exists in 'samples' table
        cursor.execute("""
            INSERT INTO samples (patient_name, barcode, collection_time, status)
            VALUES (%s, %s, NOW(), 'PENDING')
            ON DUPLICATE KEY UPDATE patient_name = VALUES(patient_name)
        """, (patient.get('patient_name'), barcode))
        db.commit()

        # 2. INSERT RESULTS
        for r in results:
            cursor.execute("""
                INSERT INTO results 
                (sample_barcode, test_name, result_value, unit, ref_range, flag)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                barcode,
                r.get('test_code'),
                r.get('result_value'),
                r.get('unit'),
                r.get('ref_range'),
                r.get('abnormal_flag')
            ))
        
        db.commit()
        log.info(f"Saved {len(results)} results for Barcode: {barcode}")
        log_event("DB_SAVE", f"Saved {len(results)} results for {barcode}")

    except Exception as e:
        log.error(f"Database Insert Error: {e}")
        log_event("DB_ERROR", str(e))
        db.rollback()