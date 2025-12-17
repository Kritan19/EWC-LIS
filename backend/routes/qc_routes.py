from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database import db

router = APIRouter()

# --- SCHEMAS ---
class QCDefinitionSchema(BaseModel):
    control_name: str
    lot_number: str
    test_code: str
    mean_value: float
    sd_value: float
    expiration_date: str

class QCResultSchema(BaseModel):
    qc_definition_id: int
    result_value: float
    performed_by: str
    status: str

def get_db_cursor():
    if not db.is_connected():
        db.reconnect()
    return db.cursor(dictionary=True)

# 1. GET ALL QC DEFINITIONS
@router.get("/definitions")
def get_qc_definitions():
    cursor = get_db_cursor()
    cursor.execute("""
        SELECT q.*, t.test_name 
        FROM qc_definitions q
        LEFT JOIN test_definitions t ON q.test_code = t.test_code
        ORDER BY q.test_code
    """)
    return cursor.fetchall()

# 2. CREATE NEW QC DEFINITION (For Settings Page)
@router.post("/definitions")
def add_qc_definition(data: QCDefinitionSchema):
    cursor = get_db_cursor()
    try:
        sql = """
            INSERT INTO qc_definitions 
            (control_name, lot_number, test_code, mean_value, sd_value, expiration_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data.control_name, data.lot_number, data.test_code, 
            data.mean_value, data.sd_value, data.expiration_date
        ))
        db.commit()
        return {"success": True, "message": "QC Definition Created"}
    except Exception as e:
        db.rollback()
        print(f"Error adding QC Def: {e}") # Print error to terminal for debugging
        raise HTTPException(status_code=500, detail=str(e))

# 3. GET RESULTS FOR CHART
@router.get("/results/{qc_id}")
def get_qc_results(qc_id: int):
    cursor = get_db_cursor()
    cursor.execute("SELECT * FROM qc_definitions WHERE id = %s", (qc_id,))
    definition = cursor.fetchone()
    
    if not definition:
        raise HTTPException(status_code=404, detail="QC Definition not found")

    cursor.execute("""
        SELECT result_value, DATE_FORMAT(run_time, '%%Y-%%m-%%d') as date 
        FROM qc_results 
        WHERE qc_definition_id = %s 
        ORDER BY run_time ASC LIMIT 30
    """, (qc_id,))
    results = cursor.fetchall()

    return {"definition": definition, "data": results}

# 4. ADD DAILY RUN (Fixes the error)
@router.post("/results")
def add_qc_result(data: QCResultSchema):
    cursor = get_db_cursor()
    try:
        sql = """
            INSERT INTO qc_results (qc_definition_id, result_value, performed_by, status, run_time)
            VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(sql, (data.qc_definition_id, data.result_value, data.performed_by, data.status))
        db.commit()
        return {"success": True, "message": "QC Result Saved"}
    except Exception as e:
        db.rollback()
        print(f"Error saving result: {e}") # Helps debug
        raise HTTPException(status_code=500, detail=str(e))