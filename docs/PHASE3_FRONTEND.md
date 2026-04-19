# Phase 3 Frontend Guide

## 1) Environment setup

```powershell
cd c:\Users\sahar\OneDrive\Desktop\Blood_Bank\Blood_Bank_Management_System\apps\frontend
Copy-Item .env.example .env
npm install
```

## 2) Start the app

```powershell
npm run dev
```

- Frontend URL: http://localhost:5173
- Backend API expected at: http://localhost:8000/api/v1

## 3) Implemented architecture

- React + Vite + TypeScript project scaffold.
- Tailwind CSS setup with global theme and responsive layout primitives.
- React Router portal routing for donor, admin, and hospital domains.
- Auth context with JWT token persistence and role-aware redirects.
- Axios API client with Authorization bearer token interception.
- Shared portal layout (top bar + sidebar + protected route guard).
- Base inventory table with filters and live API fetch fallback.

## 4) Route map

### Public
- /auth/login
- /auth/register-donor
- /auth/register-hospital

### Donor
- /donor
- /donor/appointments

### Admin
- /admin
- /admin/inventory
- /admin/hospitals

### Hospital
- /hospital
- /hospital/urgent

## 5) Data dependencies

- Login form calls POST /auth/login
- Session bootstrap calls GET /auth/me
- Inventory table calls GET /inventory/bags

## 6) Notes

- If live backend is unavailable, the inventory table renders sample rows so layout and interactions can still be reviewed.
- Role protection is enforced at the route level based on the authenticated user role.
