from fastapi import APIRouter
from typing import List
from datetime import datetime

from database import db, cursor
from schemas.patient_schema import PatientModel, PatientResponse

router = APIRouter()

# ---------- GET ALL PATIENTS ----------
@router.get("/", response_model=List[PatientResponse])
def get_patients():
    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = cursor.fetchall()
    result = []
    for r in rows:
        result.append(PatientResponse(
            id=r[0],
            patient_id=r[1],
            patient_name=r[2],
            dob=r[3],
            gender=r[4],
            phone=r[5],
            address=r[6],
            timestamp=r[7]
        ))
    return result

# ---------- CREATE PATIENT ----------
@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientModel):
    cursor.execute("""
        INSERT INTO patients (patient_id, patient_name, dob, gender,phone,address, timestamp)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE patient_name=%s
    """, (
        patient.patient_id,
        patient.patient_name,
        patient.dob,
        patient.gender,
        patient.phone,
        patient.address,
        datetime.now(),
        patient.patient_name
    ))
    db.commit()
    cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (patient.patient_id,))
    r = cursor.fetchone()
    return PatientResponse(
        id=r[0],
        patient_id=r[1],
        patient_name=r[2],
        dob=r[3],
        gender=r[4],
        phone=r[5],
        address=r[6],
        timestamp=r[7]
    )

# ---------- UPDATE PATIENT ----------
@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: str, patient: PatientModel):
    cursor.execute("""
        UPDATE patients SET patient_name=%s, dob=%s, gender=%s,phone%s,address%s, timestamp=%s
        WHERE patient_id=%s
    """, (
        patient.patient_name,
        patient.dob,
        patient.gender,
        patient.phone,
        patient.address,
        datetime.now(),
        patient_id
    ))
    db.commit()
    cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (patient_id,))
    r = cursor.fetchone()
    return PatientResponse(
        id=r[0],
        patient_id=r[1],
        patient_name=r[2],
        dob=r[3],
        gender=r[4],
        phone=r[5],
        address=r[6],
        timestamp=r[7]
    )

# ---------- DELETE PATIENT ----------
@router.delete("/{patient_id}")
def delete_patient(patient_id: str):
    cursor.execute("DELETE FROM patients WHERE patient_id=%s", (patient_id,))
    db.commit()
    return {"status": "Patient deleted", "patient_id": patient_id}
