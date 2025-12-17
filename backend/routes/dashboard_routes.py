from fastapi import APIRouter, Depends
from database import db
from datetime import date

router = APIRouter()

def get_db_cursor():
    if not db.is_connected():
        db.reconnect()
    return db.cursor(dictionary=True)

@router.get("/stats")
def get_dashboard_stats():
    cursor = get_db_cursor()
    today = date.today()
    
    stats = {
        "total_today": 0,
        "pending": 0,
        "approved": 0,
        "critical": 0
    }

    try:
        # 1. Total Samples Today
        cursor.execute("SELECT COUNT(*) as count FROM samples WHERE DATE(collection_time) = %s", (today,))
        stats["total_today"] = cursor.fetchone()["count"]

        # 2. Pending (All time)
        cursor.execute("SELECT COUNT(*) as count FROM samples WHERE status = 'PENDING'")
        stats["pending"] = cursor.fetchone()["count"]

        # 3. Approved (Today)
        cursor.execute("SELECT COUNT(*) as count FROM samples WHERE status = 'APPROVED' AND DATE(collection_time) = %s", (today,))
        stats["approved"] = cursor.fetchone()["count"]

        # 4. Critical (Pending)
        # Note: Depending on your schema, you might need to join results or check samples.is_critical
        cursor.execute("SELECT COUNT(*) as count FROM samples WHERE is_critical = TRUE AND status = 'PENDING'")
        stats["critical"] = cursor.fetchone()["count"]

        return stats

    except Exception as e:
        print(f"Dashboard Stats Error: {e}")
        return stats