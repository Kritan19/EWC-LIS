from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()

def get_db_cursor():
    if not db.is_connected():
        db.reconnect()
    return db.cursor(dictionary=True)

@router.get("/{barcode}")
def get_results_by_barcode(barcode: str):
    # 1. FORCE REFRESH (The Magic Fix)
    # This tells MySQL: "Close my previous view and show me the latest data"
    db.commit() 
    
    cursor = get_db_cursor()
    try:
        # 2. Fetch Patient Info
        cursor.execute("SELECT * FROM samples WHERE barcode = %s", (barcode,))
        patient = cursor.fetchone()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Sample not found")

        # 3. Fetch Results
        # We look for results linked to this barcode
        query = """
            SELECT 
                test_name, 
                result_value, 
                unit, 
                ref_range, 
                flag 
            FROM results 
            WHERE sample_barcode = %s
        """
        cursor.execute(query, (barcode,))
        results = cursor.fetchall()
        
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