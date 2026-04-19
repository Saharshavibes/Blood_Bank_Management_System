# Phase 5 Deployment and CI/CD Guide

## 1) What was added

- Backend production container: apps/backend/Dockerfile
- Frontend production container: apps/frontend/Dockerfile
- Frontend Nginx SPA config: apps/frontend/nginx.conf
- Production compose stack: infra/docker-compose.prod.yml
- CI workflow: .github/workflows/ci.yml
- CD workflow via deploy hooks: .github/workflows/deploy.yml
- Render service template: render.yaml
- Vercel SPA rewrite config: apps/frontend/vercel.json

## 2) Local production-mode run with Docker

```powershell
cd c:\Users\sahar\OneDrive\Desktop\Blood_Bank\Blood_Bank_Management_System\infra
Copy-Item .env.prod.example .env.prod
# Update secrets in .env.prod before first run

docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

Run backend migrations before first production traffic:

```powershell
cd c:\Users\sahar\OneDrive\Desktop\Blood_Bank\Blood_Bank_Management_System\apps\backend
alembic -c alembic.ini upgrade head
```

Endpoints:

- Frontend: http://localhost:8080
- Backend API: http://localhost:8000/api/v1
- Health: http://localhost:8000/api/v1/health

## 3) Managed Postgres on Neon or Supabase

### Neon

1. Create a project and database.
2. Copy the connection string.
3. Convert to SQLAlchemy URL format for backend:

```text
postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
```

### Supabase

1. Create a project.
2. Open Database settings and copy the pooled/direct connection string.
3. Convert to SQLAlchemy URL format:

```text
postgresql+psycopg2://USER:PASSWORD@HOST:5432/postgres?sslmode=require
```

Use this as DATABASE_URL in Render (or any backend host).

## 4) Deploy backend to Render

Option A (recommended in this repo): Blueprint using render.yaml

1. Push repository to GitHub.
2. In Render, create a Blueprint and point to the repository.
3. Render reads render.yaml and provisions bbms-backend.
4. Set required secret env vars in Render:

- DATABASE_URL
- JWT_SECRET_KEY
- CORS_ORIGINS

Option B: Manual Web Service

- Root Directory: apps/backend
- Runtime: Docker
- Dockerfile: apps/backend/Dockerfile
- Health Check Path: /api/v1/health

## 5) Deploy frontend to Vercel

1. Import the same GitHub repository in Vercel.
2. Set Root Directory to apps/frontend.
3. Build command: npm run build
4. Output directory: dist
5. Set environment variable:

- VITE_API_BASE_URL=https://<your-render-domain>/api/v1

6. Deploy.

The SPA fallback rewrite is already configured in apps/frontend/vercel.json.

## 6) Configure CI/CD on GitHub

### CI (.github/workflows/ci.yml)

On push/PR, this workflow:

- Installs backend dependencies and compiles app package for syntax/import checks.
- Installs frontend dependencies, runs typecheck, and builds the app.

### Release Gate (.github/workflows/release-gate.yml)

Manual workflow that runs full backend/frontend quality gates and deployment smoke checks before release approval.
Use this before running production deploy hooks.

### CD (.github/workflows/deploy.yml)

On push to main (or manual trigger), this workflow can trigger deployment hooks.

Add these repository secrets:

- RENDER_DEPLOY_HOOK_URL
- VERCEL_DEPLOY_HOOK_URL

Recommended environment-scoped secrets:

- RENDER_DEPLOY_HOOK_URL_PRODUCTION
- VERCEL_DEPLOY_HOOK_URL_PRODUCTION
- BACKEND_HEALTH_URL_PRODUCTION
- FRONTEND_URL_PRODUCTION
- RENDER_DEPLOY_HOOK_URL_STAGING
- VERCEL_DEPLOY_HOOK_URL_STAGING
- BACKEND_HEALTH_URL_STAGING
- FRONTEND_URL_STAGING

Reference template: .env.day2.example

Day 3 release runbook: docs/PHASE6_DAY3_RELEASE.md

If hooks are missing, CD exits gracefully without failing the pipeline.

## 7) Recommended production env values

Backend:

- ENVIRONMENT=production
- JWT_SECRET_KEY=<strong secret>
- CORS_ORIGINS=https://<your-vercel-domain>
- DATABASE_URL=<neon/supabase SQLAlchemy URL>

Frontend:

- VITE_API_BASE_URL=https://<your-render-domain>/api/v1

## 8) Post-deployment smoke checks

1. Open backend health URL.
2. Open frontend URL and verify login page loads.
3. Register a hospital or donor user.
4. Login and verify role-based redirect works.
5. Verify one protected API request from UI succeeds.

Automated smoke check script:

```powershell
cd c:\Users\sahar\OneDrive\Desktop\Blood_Bank\Blood_Bank_Management_System
python scripts\deploy\smoke_check.py --backend-health-url https://your-backend.onrender.com/api/v1/health --frontend-url https://your-frontend.vercel.app
```

Optional auth check argument:

```powershell
python scripts\deploy\smoke_check.py --backend-health-url https://your-backend.onrender.com/api/v1/health --frontend-url https://your-frontend.vercel.app --auth-login-url https://your-backend.onrender.com/api/v1/auth/login
```
