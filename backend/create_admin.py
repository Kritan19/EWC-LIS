import mysql.connector
from auth import hash_password
from config import settings

# 1. Connect to Database
try:
    db = mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASS,
        database=settings.DB_NAME
    )
    cursor = db.cursor()
    print("Connected to database...")

    # 2. Define the Admin User
    username = "admin"
    raw_password = "123"
    hashed_password = hash_password(raw_password) # <--- THIS ENCRYPTS IT
    full_name = "Dr. Sarah"
    role = "Pathologist"
    email = "admin@hospital.com"

    # 3. Delete old admin if exists (to fix the broken one)
    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    db.commit()

    # 4. Insert new Admin
    query = """
    INSERT INTO users (username, email, password) 
    VALUES (%s, %s, %s)
    """
    # Note: Your colleague's schema might be using 'email' or 'username'. 
    # Based on database.py, the table has: id, username, email, password.
    # We will insert username, email, and the HASHED password.
    
    cursor.execute(query, (username, email, hashed_password))
    db.commit()

    print(f"✅ Success! User '{username}' created with password '{raw_password}'")
    print(f"Encrypted password stored as: {hashed_password[:10]}...")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    if 'db' in locals() and db.is_connected():
        cursor.close()
        db.close()