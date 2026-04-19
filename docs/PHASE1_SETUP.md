# Phase 1 Setup Guide

## 1) Start local database stack

```powershell
cd c:\Users\sahar\OneDrive\Desktop\Blood_Bank\Blood_Bank_Management_System\infra
Copy-Item .env.example .env
docker compose up -d
docker compose ps
```

## 2) Access pgAdmin

- URL: http://localhost:5050
- Login email: value of `PGADMIN_DEFAULT_EMAIL` in `.env`
- Login password: value of `PGADMIN_DEFAULT_PASSWORD` in `.env`

Server connection in pgAdmin:

- Host name: `postgres`
- Port: `5432`
- Username: value of `POSTGRES_USER`
- Password: value of `POSTGRES_PASSWORD`
- Database: value of `POSTGRES_DB`

## 3) Backend environment and migrations

```powershell
cd c:\Users\sahar\OneDrive\Desktop\Blood_Bank\Blood_Bank_Management_System\apps\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python scripts/run_quality_checks.py
```

## 4) Phase 1 data model outcomes

- Donor management base tables with medical history support.
- Blood inventory lifecycle with strict expiration checks.
- Hospital and request ownership relations with explicit delete policies.
- Indexed search paths for stock lookup and urgent request workflows.
