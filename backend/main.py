from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import setup_tables

# --- IMPORT ROUTERS ---
from routes.user_routes import router as user_router
from routes.order_routes import router as order_router
from routes.patient_routes import router as patient_router
from routes.result_routes import router as result_router
from routes.worklists_routes import router as patients_results_router
from routes.batch_order_routes import router as batch_order_router
from routes.log_routes import router as log_router
from routes.manual_entry_routes import router as manual_entry_router
from routes.settings_routes import router as settings_router
from routes.dashboard_routes import router as dashboard_router
from routes.sample_routes import router as sample_router
from routes.qc_routes import router as qc_router
from routes.report_routes import router as report_router

app = FastAPI(title="Atellica LIS API", version="1.0.0")

# --- CORS SETTINGS (Allow Frontend) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev, change to ["http://localhost:5173"] for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE SETUP ---
@app.on_event("startup")
def on_startup():
    setup_tables()
    print("Database tables checked/created.")

# --- REGISTER ROUTES ---
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(order_router, prefix="/api/orders", tags=["Orders"])
app.include_router(patient_router, prefix="/api/patients", tags=["Patients"])
app.include_router(result_router, prefix="/api/results", tags=["Results"])
app.include_router(patients_results_router, prefix="/api/worklists", tags=["Worklists"])
app.include_router(batch_order_router, prefix="/api/batch", tags=["Batch Orders"])
app.include_router(log_router, prefix="/api/logs", tags=["Logs"])
app.include_router(manual_entry_router, prefix="/api/manual", tags=["Manual Entry"])
app.include_router(settings_router, prefix="/api/settings", tags=["Settings"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(sample_router, prefix="/api/samples", tags=["Samples List"])
app.include_router(qc_router, prefix="/api/qc", tags=["Quality Control"])
app.include_router(report_router, prefix="/api/report", tags=["Reports"])

@app.get("/")
def home():
    return {"message": "LIMS API is running"}