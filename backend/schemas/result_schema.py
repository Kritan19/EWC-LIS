from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Input model for creating/updating a result
class ResultModel(BaseModel):
    patient_id: Optional[str] = None
    order_id: Optional[str] = None
    placer_order: Optional[str] = None
    filler_order:Optional[str] = None
    test_code: Optional[str] = None
    result_value: Optional[str] = None
    unit: Optional[str] = None
    ref_range: Optional[str] = None
    abnormal_flag: Optional[str] = None
    result_status: Optional[str] = None
    result_flags: Optional[str] = None
    instrument_id: Optional[str] = None
    result_datetime: Optional[datetime] = None
    instrument_run_id: Optional[str] = None

# Output model for responses
class ResultResponse(ResultModel):
    id: int
    result_timestamp: datetime

    class Config:
        from_attributes = True
