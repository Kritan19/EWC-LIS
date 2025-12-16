from fastapi import APIRouter
from typing import List
from datetime import datetime
from database import cursor, db
from schemas.result_schema import ResultModel, ResultResponse

router = APIRouter()

# ======================================================
# Get All Results
# ======================================================
@router.get("/", response_model=List[ResultResponse])
def get_results():
    cursor.execute("SELECT * FROM results ORDER BY id DESC")
    rows = cursor.fetchall()
    results = []
    for r in rows:
        results.append(ResultResponse(
            id=r[0],
            patient_id=r[1] or None,
            order_id=r[2] or None,
            placer_order=r[3] or None,
            filler_order=r[4] or None,
            test_code=r[5] or None,
            result_value=r[6] or None,
            unit=r[7] or None,
            ref_range=r[8] or None,
            abnormal_flag=r[9] or None,
            result_status=r[10] or None,
            result_flags=r[11] or None,
            instrument_id=r[12] or None,
            result_datetime=r[13] or None,
            instrument_run_id=r[14] or None,
            result_timestamp=r[15] or datetime.now()
        ))
    return results


# ======================================================
# Create Results
# ======================================================
@router.post("/", response_model=ResultResponse)
def create_result(result: ResultModel):
    result_dt = result.result_datetime or datetime.now()
    timestamp = datetime.now()

    cursor.execute("""
        INSERT INTO results (
            patient_id, order_id, placer_order, filler_order,
            test_code, result_value, unit, ref_range,
            abnormal_flag, result_status, result_flags, instrument_id,
            result_datetime, instrument_run_id, result_timestamp
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        result.patient_id, result.order_id, result.placer_order, result.filler_order,
        result.test_code, result.result_value, result.unit, result.ref_range,
        result.abnormal_flag, result.result_status, result.result_flags, result.instrument_id,
        result_dt, result.instrument_run_id, timestamp
    ))
    db.commit()

    # ======================================================
    # Fetch data using id
    # ======================================================
    cursor.execute("SELECT * FROM results WHERE id=LAST_INSERT_ID()")
    r = cursor.fetchone()

    return ResultResponse(
        id=r[0],
        patient_id=r[1] or None,
        order_id=r[2] or None,
        placer_order=r[3] or None,
        filler_order=r[4] or None,
        test_code=r[5] or None,
        result_value=r[6] or None,
        unit=r[7] or None,
        ref_range=r[8] or None,
        abnormal_flag=r[9] or None,
        result_status=r[10] or None,
        result_flags=r[11] or None,
        instrument_id=r[12] or None,
        result_datetime=r[13] or None,
        instrument_run_id=r[14] or None,
        result_timestamp=r[15] or timestamp
    )


# ======================================================
# Update Results
# ======================================================
@router.put("/{result_id}", response_model=ResultResponse)
def update_result(result_id: int, result: ResultModel):
    try:
        result_dt = result.result_datetime or datetime.now()
        timestamp = datetime.now()

        cursor.execute("""
            UPDATE results SET
                patient_id=%s,
                order_id=%s,
                placer_order=%s,
                filler_order=%s,
                test_code=%s,
                result_value=%s,
                unit=%s,
                ref_range=%s,
                abnormal_flag=%s,
                result_status=%s,
                result_flags=%s,
                instrument_id=%s,
                result_datetime=%s,
                instrument_run_id=%s,
                result_timestamp=%s
            WHERE id=%s
        """, (
            result.patient_id, result.order_id, result.placer_order, result.filler_order,
            result.test_code, result.result_value, result.unit, result.ref_range,
            result.abnormal_flag, result.result_status, result.result_flags, result.instrument_id,
            result_dt, result.instrument_run_id, timestamp, result_id
        ))
        db.commit()

        cursor.execute("SELECT * FROM results WHERE id=%s", (result_id,))
        r = cursor.fetchone()
        if not r:
            return {"error": "Result not found"}

        return ResultResponse(
            id=r[0],
            patient_id=r[1] or None,
            order_id=r[2] or None,
            placer_order=r[3] or None,
            filler_order=r[4] or None,
            test_code=r[5] or None,
            result_value=r[6] or None,
            unit=r[7] or None,
            ref_range=r[8] or None,
            abnormal_flag=r[9] or None,
            result_status=r[10] or None,
            result_flags=r[11] or None,
            instrument_id=r[12] or None,
            result_datetime=r[13] or None,
            instrument_run_id=r[14] or None,
            result_timestamp=r[15] or timestamp
        )
    except Exception as e:
        return {"error": str(e)}


# ======================================================
# Delete Results
# ======================================================
@router.delete("/{result_id}")
def delete_result(result_id: int):
    try:
        cursor.execute("DELETE FROM results WHERE id=%s", (result_id,))
        db.commit()
        return {"status": "Result deleted", "result_id": result_id}
    except Exception as e:
        return {"error": str(e)}
