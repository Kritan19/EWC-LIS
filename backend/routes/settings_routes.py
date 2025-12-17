from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from database import db  # Imports from backend/database.py

router = APIRouter()

# --- Schemas ---
class TestDefinitionSchema(BaseModel):
    test_code: str
    test_name: str
    unit: str
    min_male: float
    max_male: float
    min_female: float
    max_female: float

class MachineSchema(BaseModel):
    machine_name: str
    ip_address: str
    protocol: str
    division: str

# --- Helper ---
def get_db_cursor():
    if not db.is_connected():
        db.reconnect()
    return db.cursor(dictionary=True)

# --- ROUTES ---

# 1. GET ALL TESTS
@router.get("/tests")
def get_tests():
    cursor = get_db_cursor()
    cursor.execute("SELECT * FROM test_definitions ORDER BY test_code")
    return cursor.fetchall()

# 2. ADD TEST (Admin Only)
@router.post("/tests")
def add_test(test: TestDefinitionSchema):
    cursor = get_db_cursor()
    try:
        sql = """
            INSERT INTO test_definitions 
            (test_code, test_name, unit, min_range_male, max_range_male, min_range_female, max_range_female)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            test.test_code, test.test_name, test.unit,
            test.min_male, test.max_male, test.min_female, test.max_female
        ))
        db.commit()
        return {"success": True, "message": "Test Code Added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. GET MACHINES
@router.get("/machines")
def get_machines():
    cursor = get_db_cursor()
    cursor.execute("SELECT * FROM machines")
    return cursor.fetchall()

# 4. ADD MACHINE (Admin Only)
@router.post("/machines")
def add_machine(machine: MachineSchema):
    cursor = get_db_cursor()
    try:
        sql = """
            INSERT INTO machines (machine_name, ip_address, protocol, division)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (machine.machine_name, machine.ip_address, machine.protocol, machine.division))
        db.commit()
        return {"success": True, "message": "Machine Added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))