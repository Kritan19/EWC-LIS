from fastapi import APIRouter
from typing import List
from datetime import datetime
from database import cursor, db
from schemas.order_schema import OrderModel, OrderResponse

router = APIRouter()

# ---------- GET All Orders ----------
@router.get("/", response_model=List[OrderResponse])
def get_orders():
    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = cursor.fetchall()
    result = []
    for r in rows:
        result.append(OrderResponse(
            id=r[0], patient_id=r[1], order_id=r[2], placer_order=r[3],
            package_id=r[4], run_id=r[5], filler_order=r[6], filler_sub=r[7],
            priority=r[8], order_datetime=r[9], test_codes=r[10],
            sample_type=r[11], order_timestamp=r[12]
        ))
    return result

# ---------- CREATE Order ----------
@router.post("/", response_model=OrderResponse)
def create_order(order: OrderModel):
    cursor.execute("""
        INSERT INTO orders (patient_id, order_id, placer_order, package_id, run_id,
                            filler_order, filler_sub, priority, order_datetime,
                            test_codes, sample_type, order_timestamp)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (order.patient_id, order.order_id, order.placer_order, order.package_id, order.run_id,
          order.filler_order, order.filler_sub, order.priority, order.order_datetime,
          order.test_codes, order.sample_type, datetime.now()))
    db.commit()
    cursor.execute("SELECT * FROM orders WHERE order_id=%s", (order.order_id,))
    r = cursor.fetchone()
    return OrderResponse(
        id=r[0], patient_id=r[1], order_id=r[2], placer_order=r[3],
        package_id=r[4], run_id=r[5], filler_order=r[6], filler_sub=r[7],
        priority=r[8], order_datetime=r[9], test_codes=r[10],
        sample_type=r[11], order_timestamp=r[12]
    )

# ---------- UPDATE Order ----------
@router.put("/{order_id}")
def update_order(order_id: str, order: OrderModel):
    try:
        cursor.execute("""
            UPDATE orders SET patient_id=%s, placer_order=%s, package_id=%s,
                              run_id=%s, filler_order=%s, filler_sub=%s,
                              priority=%s, order_datetime=%s, test_codes=%s,
                              sample_type=%s, order_timestamp=%s
            WHERE order_id=%s
        """, (order.patient_id, order.placer_order, order.package_id, order.run_id,
              order.filler_order, order.filler_sub, order.priority, order.order_datetime,
              order.test_codes, order.sample_type, datetime.now(), order_id))
        db.commit()
        return {"status": "Order updated", "order_id": order_id}
    except Exception as e:
        return {"error": str(e)}

# ---------- DELETE Order ----------
@router.delete("/{order_id}")
def delete_order(order_id: str):
    try:
        cursor.execute("DELETE FROM orders WHERE order_id=%s", (order_id,))
        db.commit()
        return {"status": "Order deleted", "order_id": order_id}
    except Exception as e:
        return {"error": str(e)}
