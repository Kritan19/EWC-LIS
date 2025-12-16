### Python ASTM Protocol With Atellica And MySql through TCP

### Install Dependencies:
#### Method 1
```
pip install mysql-connector-python
pip install FastAPI uvicorn 
pip install requests
pip install PyJWT
pip install bcrypt
pip install email-validator
pip install passlib[bcrypt]
pip install pydantic-settings
pip install python-dotenv

```
#### Method 2
```    
pip install -r requirements.txt
```
### Freeze 
```
pip freeze > requirements.txt -----optional
```
### Variable environment

```
python -m venv venv
```

Exact .env file has not been attached in this repo hence follow the following pattern.

```
# --- DATABASE ---
DB_HOST=database_host
DB_USER=database_user
DB_PASS=database_password
DB_NAME=database_name

# --- LISTENER ---
LIS_HOST=0.0.0.0
LIS_PORT=5001

# --- ATELLICA CLIENT ---
ATELLICA_HOST=127.0.0.1
ATELLICA_PORT=15000

# --- TOKENS (IF USING FASTAPI JWT) ---
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# --- LOGGING ---
LOG_DIR=atellica_logs
LOG_LEVEL=DEBUG

```
### To run multiple server at a time
To run multiple server at a time that is for api
http://127.0.0.1:8000 for docs http://127.0.0.1:8000/docs 
and listener eg: ASTM Listener running on 0.0.0.0:7777
```
uvicorn main:app --reload 
```
### Create Folder for Logs
Logs folder has not been attached in this repo hence follow the following pattern and create following folder
and files.

```
    logs
       critical_atellica.log
       debug_atellica.log
       error_atellica.log
       info_atellica.log
       warning_atellica.log
           
```
### Create Folder for Raw Files
atellica_logs folder has not been attached in this repo hence follow the following pattern and create following folder.
```
FolderName = atellica_logs  ---eg: atellica_yyyy-mm-d.txt
```

### To Run single file
```
python nmc.py
```

To run simulator for single file

```
python nmc_simulator.py
```

