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

        # 2. Check/Insert Sample
        cursor.execute("SELECT id FROM samples WHERE barcode = %s", (barcode,))
        exists = cursor.fetchone()

        if not exists:
            # Create new sample
            cursor.execute("""
                INSERT INTO samples (patient_name, barcode, collection_time, status)
                VALUES (%s, %s, NOW(), 'PENDING')
            """, (patient_name, barcode))
            log_event('status', f"New Sample Created: {barcode}")
        else:
            # Update existing sample details and reset status to PENDING for review
            cursor.execute("""
                UPDATE samples 
                SET patient_name = %s, status = 'PENDING' 
                WHERE barcode = %s
            """, (patient_name, barcode))

        # 3. Process Results (Insert or Update)
        count_inserted = 0
        count_updated = 0

        for r in results:
            test_code = r.get('test_code', '')
            if not test_code: continue

            # Check if this specific test already exists for this barcode
            cursor.execute("""
                SELECT id FROM results WHERE sample_barcode = %s AND test_name = %s
            """, (barcode, test_code))
            
            existing_result = cursor.fetchone()

            if existing_result:
                # UPDATE existing result
                cursor.execute("""
                    UPDATE results 
                    SET result_value=%s, unit=%s, ref_range=%s, flag=%s 
                    WHERE id=%s
                """, (
                    r.get('result_value'), 
                    r.get('unit'), 
                    r.get('ref_range'), 
                    r.get('abnormal_flag'), 
                    existing_result['id']
                ))
                count_updated += 1
            else:
                # INSERT new result
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
                count_inserted += 1

        db.commit()
        
        log_msg = f"Processed {patient_name} (ID: {barcode}): {count_inserted} Added, {count_updated} Updated."
        log_event('result', log_msg)
        print(f"   💾 DB SUCCESS: {log_msg}")

    except Exception as e:
        db.rollback()
        log_event('error', f"DB Insert Failed: {e}")
        print(f"   ❌ DB ERROR: {e}")