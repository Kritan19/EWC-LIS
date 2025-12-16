from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

# Input model for creating/updating a patient
class PatientModel(BaseModel):
    patient_id: str
    patient_name: str
    dob: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

# Output model for responses
class PatientResponse(PatientModel):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
