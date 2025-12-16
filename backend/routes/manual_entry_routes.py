from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import db, cursor 

router = APIRouter()

# --- Schema ---
class ManualOrderRequest(BaseModel):
    patient_id: str
    full_name: str
    age: Optional[str] = None
    gender: str
    barcode: str
    tests: List[str]  # ["WBC", "RBC"]

# --- Helper to get DB connection ---
def get_db_cursor():
    if not db.is_connected():
        db.reconnect()
    return db.cursor(dictionary=True)

@router.post("/create")
def create_manual_order(order: ManualOrderRequest):
    cursor = get_db_cursor()
    try:
        # 1. Insert/Update Patient
        # We use ON DUPLICATE KEY UPDATE to handle returning patients
        sql_patient = """
            INSERT INTO patients (patient_id, patient_name, gender, timestamp) 
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE patient_name = VALUES(patient_name)
        """
        cursor.execute(sql_patient, (order.patient_id, order.full_name, order.gender))
        
        # 2. Insert Order (The Barcode)
        # We store the selected tests as a comma-separated string for now
        test_string = ",".join(order.tests)
        
        sql_order = """
            INSERT INTO orders (patient_id, order_id, test_codes, sample_type, order_timestamp)
            VALUES (%s, %s, %s, 'Serum', NOW())
        """
        cursor.execute(sql_order, (order.patient_id, order.barcode, test_string))
        
        # 3. Create 'Pending' Entries in Samples Table (For the Dashboard View)
        # This bridges the gap between the complex schema and the simple dashboard
        sql_sample = """
            INSERT INTO samples (patient_name, barcode, collection_time, status)
            VALUES (%s, %s, NOW(), 'PENDING')
        """
        cursor.execute(sql_sample, (order.full_name, order.barcode))

        db.commit()
        return {"success": True, "message": "Order created successfully"}

    except Exception as e:
        db.rollback()
        print(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))