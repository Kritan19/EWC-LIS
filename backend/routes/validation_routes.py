from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()

def get_db_cursor():
    if not db.is_connected():
        db.reconnect()
    return db.cursor(dictionary=True)

@router.get("/")
def get_pending_samples():
    cursor = get_db_cursor()
    try:
        # Fetch samples that are NOT approved yet
        query = "SELECT * FROM samples WHERE status = 'PENDING' ORDER BY id DESC"
        cursor.execute(query)
        samples = cursor.fetchall()
        
        # Transform data to match React Frontend expected format
        formatted_samples = []
        for s in samples:
            formatted_samples.append({
                "id": s['id'],
                "name": s['patient_name'],
                "barcode": s['barcode'],
                "time": s['collection_time'],
                "status": s['status'],
                "critical": bool(s['is_critical'])
            })
            
        return formatted_samples
    except Exception as e:
        print(f"Error fetching pending samples: {e}")
        raise HTTPException(status_code=500, detail=str(e))