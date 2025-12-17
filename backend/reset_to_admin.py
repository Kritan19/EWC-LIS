import mysql.connector
from auth import hash_password
from config import settings

try:
    # 1. Connect
    db = mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASS,
        database=settings.DB_NAME
    )
    cursor = db.cursor()
    print("Connected to database...")

    # 2. Settings for the NEW Admin
    target_email = "admin@hospital.com"
    target_username = "admin"
    target_password = "123"
    target_name = "System Admin" # <--- Generic Name
    target_role = "Admin"        # <--- Generic Role

    # 3. Clean up OLD users (Remove Dr. Sarah or old Admin)
    print("Removing old admin accounts...")
    cursor.execute("DELETE FROM users WHERE email = %s", (target_email,))
    cursor.execute("DELETE FROM users WHERE username = %s", (target_username,))
    db.commit()

    # 4. Insert NEW Admin
    print("Creating new System Admin...")
    hashed_pw = hash_password(target_password)
    
    # We explicitly insert the Name and Role now
    # Note: If your colleague's 'users' table structure doesn't have 'full_name' or 'role' columns 
    # in the schema yet, we might need to add them. 
    # Based on previous steps, we added 'email'. Let's ensure 'full_name' and 'role' exist.
    
    try:
        # Try inserting with full details
        query = """
        INSERT INTO users (username, email, password, full_name, role) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (target_username, target_email, hashed_pw, target_name, target_role))
    except mysql.connector.Error as err:
        # If columns missing, just insert basics (logic fallback)
        print(f"Warning: {err}. Inserting basic credentials only.")
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (target_username, target_email, hashed_pw))

    db.commit()
    print("✅ Success! Login with: admin@hospital.com / 123")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    if 'db' in locals() and db.is_connected():
        cursor.close()
        db.close()