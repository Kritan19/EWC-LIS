from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()

def get_db_cursor():
    if not db.is_connected():
        db.reconnect()
    return db.cursor(dictionary=True)

@router.get("/{barcode}")
def get_results_by_barcode(barcode: str):
    cursor = get_db_cursor()
    try:
        # 1. Fetch Patient Info
        cursor.execute("SELECT * FROM samples WHERE barcode = %s", (barcode,))
        patient = cursor.fetchone()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Sample not found")

        # 2. Fetch Results (SMART CHECK)
        # We try to query using 'sample_barcode' first. 
        # If that fails (column doesn't exist), we try 'order_id'.
        try:
            query = """
                SELECT test_name, result_value, unit, ref_range, flag 
                FROM results WHERE sample_barcode = %s
            """
            cursor.execute(query, (barcode,))
        except Exception:
            # Fallback for old schema
            db.reconnect() # Reset connection after error
            cursor = db.cursor(dictionary=True)
            query = """
                SELECT test_code as test_name, result_value, unit, ref_range, abnormal_flag as flag 
                FROM results WHERE order_id = %s
            """
            cursor.execute(query, (barcode,))

        results = cursor.fetchall()
        
        # Debug Print to Terminal
        print(f"DEBUG: Fetched {len(results)} results for {barcode}")

        return {
            "patient": {
                "name": patient['patient_name'],
                "barcode": patient['barcode'],
                "status": patient['status']
            },
            "results": results 
        }

    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))