# BBMS Frontend (Phase 3)

React + Vite + TypeScript + Tailwind foundation for donor, admin, and hospital portals.

## Quick start

```powershell
cd c:\Users\sahar\OneDrive\Desktop\Blood_Bank\Blood_Bank_Management_System\apps\frontend
Copy-Item .env.example .env
npm install
npm run dev
```

## Environment

- VITE_API_BASE_URL=http://localhost:8000/api/v1

## Implemented in this phase

- Routing and role-based guards for all three portals.
- Authentication context with login and registration wiring.
- Axios client with JWT bearer token propagation.
- Shared portal layout system (responsive top bar + sidebar).
- Base inventory data table with filtering and fallback sample data.
