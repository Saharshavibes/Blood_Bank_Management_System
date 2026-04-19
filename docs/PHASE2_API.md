# Phase 2 Backend API Guide

## 1) Install backend dependencies

```powershell
cd c:\Users\sahar\OneDrive\Desktop\Blood_Bank\Blood_Bank_Management_System\apps\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## 2) Run database migrations

```powershell
alembic revision --autogenerate -m "phase2 auth and api"
alembic upgrade head
```

## 3) Start API server

```powershell
uvicorn app.main:app --reload
```

## 4) Base URL and docs

- API base: http://localhost:8000/api/v1
- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

## 5) Authentication endpoints

- POST /api/v1/auth/register/admin
- POST /api/v1/auth/register/donor
- POST /api/v1/auth/register/hospital
- POST /api/v1/auth/login
- GET /api/v1/auth/me

## 6) Donor CRUD endpoints

- POST /api/v1/donors
- GET /api/v1/donors
- GET /api/v1/donors/{donor_id}
- GET /api/v1/donors/me/profile
- PUT /api/v1/donors/{donor_id}
- DELETE /api/v1/donors/{donor_id}

## 7) Inventory endpoints (add/scan CRUD)

- POST /api/v1/inventory/bags
- GET /api/v1/inventory/bags
- GET /api/v1/inventory/bags/{bag_id}
- GET /api/v1/inventory/scan/{bag_number}
- PATCH /api/v1/inventory/bags/{bag_id}
- DELETE /api/v1/inventory/bags/{bag_id}

## 8) Hospital request CRUD endpoints

- POST /api/v1/requests
- GET /api/v1/requests
- GET /api/v1/requests/{request_id}
- PATCH /api/v1/requests/{request_id}
- DELETE /api/v1/requests/{request_id}
