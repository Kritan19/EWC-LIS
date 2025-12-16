from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Input model for creating/updating an order
class OrderModel(BaseModel):
    patient_id: str
    order_id: str
    placer_order: Optional[str] = None
    package_id: Optional[str] = None
    run_id: Optional[int] = 0
    filler_order: Optional[str] = None
    filler_sub: Optional[str] = None
    priority: Optional[str] = None
    order_datetime: Optional[datetime] = None
    test_codes: Optional[str] = None
    sample_type: Optional[str] = None

# Output model for responses
class OrderResponse(OrderModel):
    id: int
    order_timestamp: datetime

    class Config:
        from_attributes = True
