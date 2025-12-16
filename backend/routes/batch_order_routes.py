# routes/order_routes.py
from fastapi import APIRouter
from typing import List
from database import cursor, db
from schemas.batch_order_schema import BatchOrderRequest
from db_insert import save_to_db  # reuse your function

router = APIRouter()


@router.post("/")
def create_batch_order(batch: BatchOrderRequest):
    inserted_orders = []
    for order_item in batch.orders:
        patient = {"patient_id": order_item.patient_id, "patient_name": "unknown", "timestamp": None}
        order = {
            "patient_id": order_item.patient_id,
            "order_id": order_item.order_id,
            "placer_order": order_item.placer_order,
            "package_id": order_item.package_id,
            "priority": order_item.priority,
            "sample_type": order_item.sample_type,
            "order_datetime": order_item.order_datetime,
            "order_timestamp": order_item.order_datetime
        }
        results = []
        for r in order_item.results:
            results.append({
                "patient_id": order_item.patient_id,
                "test_code": r.test_code,
                "result_value": r.result_value,
                "unit": r.unit,
                "ref_range": r.ref_range,
                "abnormal_flag": r.abnormal_flag,
                "result_status": "F",
                "result_flags": "",
                "instrument_id": "API",
                "result_datetime": order_item.order_datetime,
                "instrument_run_id": "",
                "result_timestamp": order_item.order_datetime
            })

        # Save to DB using your existing function
        save_to_db(patient, order, results)
        inserted_orders.append(order_item.order_id)

    return {"status": "success", "inserted_orders": inserted_orders}
