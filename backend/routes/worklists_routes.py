from fastapi import APIRouter
from database import cursor
from typing import List, Dict

router = APIRouter()

@router.get("/", response_model=List[Dict])
def get_all_patient_results():
    cursor.execute("""
        SELECT id, order_id, patient_id, test_code, result_value, unit,
               result_datetime, result_status, result_flags,
               instrument_id, instrument_run_id, received_at
        FROM patient_results
        ORDER BY received_at DESC
    """)
    rows = cursor.fetchall()

    columns = [col[0] for col in cursor.description]

    return [dict(zip(columns, row)) for row in rows]

