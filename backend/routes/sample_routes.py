from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db

router = APIRouter()

def get_db_cursor():
    if not db.is_connected():
        db.reconnect()
    return db.cursor(dictionary=True)

@router.get("/all")
def get_all_samples(search: Optional[str] = None, status: Optional[str] = None):
    cursor = get_db_cursor()
    
    # Base Query
    query = "SELECT * FROM samples WHERE 1=1"
    params = []

    # Dynamic Filtering
    if status and status != "All":
        query += " AND status = %s"
        params.append(status)
    
    if search:
        # Search by Name OR Barcode
        query += " AND (patient_name LIKE %s OR barcode LIKE %s)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])

    query += " ORDER BY id DESC LIMIT 100" # Limit to last 100 for performance

    try:
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))