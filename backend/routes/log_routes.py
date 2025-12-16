from fastapi import APIRouter
from database import db, cursor

router = APIRouter()

@router.get("/")
def get_logs():
    cursor.execute("SELECT * FROM listener_log ORDER BY id DESC")
    return cursor.fetchall()
