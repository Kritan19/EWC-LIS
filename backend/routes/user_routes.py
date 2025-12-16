from fastapi import APIRouter, HTTPException, Depends
from mysql.connector import connect
from auth import hash_password, verify_password, create_token
from schemas.user_schema import UserRegister, UserLogin, UserResponse
from config import settings

router = APIRouter()


# --- Database connection helper ---
def get_db():
  db = connect(
    host=settings.DB_HOST,
    user=settings.DB_USER,
    password=settings.DB_PASS,
    database=settings.DB_NAME
  )
  cursor = db.cursor(dictionary=True)
  try:
    yield db, cursor
  finally:
    cursor.close()
    db.close()


# --- Register ---
@router.post("/register", response_model=UserResponse)
def register_user(user: UserRegister, db_data: tuple = Depends(get_db)):
  db, cursor = db_data
  # Check if user exists
  cursor.execute("SELECT * FROM users WHERE email=%s", (user.email,))
  if cursor.fetchone():
    raise HTTPException(status_code=400, detail="User already exists")

  hashed = hash_password(user.password)
  cursor.execute("INSERT INTO users (email,username, password) VALUES (%s, %s,%s)", (user.email,user.username, hashed))
  db.commit()
  user_id = cursor.lastrowid
  return {"id": user_id,"username":user.username, "email": user.email}


# --- Login ---
@router.post("/login")
def login_user(user: UserLogin, db_data: tuple = Depends(get_db)):
  db, cursor = db_data
  cursor.execute("SELECT * FROM users WHERE email=%s", (user.email,))
  row = cursor.fetchone()
  if not row:
    raise HTTPException(status_code=401, detail="Invalid credentials")

  hashed_password = row["password"]
  if not verify_password(user.password, hashed_password):
    raise HTTPException(status_code=401, detail="Invalid credentials")

  token = create_token({"sub": row["email"], "id": row["id"]})
  return {"access_token": token, "token_type": "bearer"}

# from fastapi import APIRouter, HTTPException, status
# from auth import hash_password, verify_password, create_token
# from schemas.user_schema import UserRegister,UserLogin,UserResponse
# from database import cursor, db  # your MySQL connection
#
# router = APIRouter()
#
#
# @router.post("/register", response_model=UserResponse)
# def register_user(user: UserRegister):
#   # Check if email already exists
#   cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
#   existing_user = cursor.fetchone()
#   if existing_user:
#     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
#
#   hashed_pwd = hash_password(user.password)
#   cursor.execute(
#     "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
#     (user.username, user.email, hashed_pwd)
#   )
#   db.commit()
#   user_id = cursor.lastrowid
#   return UserResponse(id=user_id, username=user.username, email=user.email)
#
#
# @router.post("/login")
# def login_user(user: UserLogin):
#   cursor.execute("SELECT id, username, password FROM users WHERE email = %s", (user.email,))
#   db_user = cursor.fetchone()
#   if not db_user:
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
#
#   user_id, username, hashed_pwd = db_user
#   if not verify_password(user.password, hashed_pwd):
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
#
#   token = create_token({"user_id": user_id, "username": username})
#   return {"access_token": token, "token_type": "bearer"}
