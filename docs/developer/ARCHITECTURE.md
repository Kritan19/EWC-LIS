# EWC LIS - System Architecture

## Overview
EWC LIS is a 3-tier Laboratory Information System designed for high-throughput labs.

## Components

### 1. Frontend (Client)
- **Tech Stack:** React 19, Vite, CoreUI.
- **Port:** 5173.
- **Role:** User Interface for Pathologists and Technicians.

### 2. Backend (API)
- **Tech Stack:** Python 3.x, FastAPI, Uvicorn.
- **Port:** 8000.
- **Role:** Handles business logic, authentication, and database CRUD operations.

### 3. Middleware (Machine Interface)
- **Tech Stack:** Python 3.x, TCP Sockets.
- **Port:** 5001.
- **Role:** Listens for incoming ASTM/HL7 data from laboratory instruments and writes directly to the database.

### 4. Database
- **Tech Stack:** MySQL 8.0.
- **Role:** Central repository for Users, Patients, Orders, and Results.

## Data Flow
1. Instrument sends data -> Middleware (Port 5001).
2. Middleware parses frame -> Inserts into MySQL.
3. Frontend polls API -> API reads MySQL -> Returns JSON.
4. Pathologist approves result -> API updates status in MySQL.