from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ResultItem(BaseModel):
    test_code: str
    result_value: str
    unit: Optional[str] = None
    ref_range: Optional[str] = None
    abnormal_flag: Optional[str] = None

class OrderItem(BaseModel):
    patient_id: str
    order_id: str
    placer_order: Optional[str] = None
    package_id: Optional[str] = None
    sample_type: Optional[str] = None
    priority: Optional[str] = None
    order_datetime: Optional[datetime] = None
    results: Optional[List[ResultItem]] = []

class BatchOrderRequest(BaseModel):
    orders: List[OrderItem]
