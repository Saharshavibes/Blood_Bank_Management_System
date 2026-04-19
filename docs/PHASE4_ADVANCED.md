# Phase 4 Advanced Features Guide

## 1) Backend: nearest blood bank routing

Implemented endpoint:

- GET /api/v1/requests/{request_id}/nearest-banks?max_results=5

Behavior:

- Only urgent or critical requests are eligible for nearest-bank routing.
- Uses Haversine distance math over latitude/longitude.
- Filters candidate source hospitals to active hospitals with AVAILABLE matching blood stock.
- Returns sorted nearest candidates with distance, available units, and available volume.

Related backend files:

- app/services/routing.py
- app/schemas/routing.py
- app/api/v1/requests.py

## 2) Backend: donor impact analytics

Implemented endpoints:

- GET /api/v1/donors/me/impact
- GET /api/v1/donors/{donor_id}/impact

Behavior:

- Aggregates donor blood bag history into total donated volume and donation count.
- Calculates estimated lives impacted.
- Computes monthly trend data for the latest 6 months.
- Calculates milestone achievements and next badge progression.

Related backend files:

- app/schemas/impact.py
- app/api/v1/donors.py

## 3) Frontend: Leaflet urgent routing map

Implemented page:

- /hospital/urgent

Features:

- Input urgent request ID.
- Fetch nearest banks from backend.
- Select candidate source hospital from ranked list.
- Render requester + candidates on Leaflet map.
- Draw direct route polyline to selected candidate.

Related frontend files:

- src/pages/hospital/HospitalUrgentPage.tsx
- src/components/maps/UrgentRoutingMap.tsx
- src/services/routing.ts
- src/types/routing.ts

## 4) Frontend: donor impact chart dashboard

Implemented page:

- /donor

Features:

- Fetch donor impact analytics from backend.
- Show KPI cards (volume, donations, lives impacted, badge).
- Render milestone progress bar.
- Render volume area chart and donation count bar chart via Recharts.

Related frontend files:

- src/components/donor/DonorImpactDashboard.tsx
- src/pages/donor/DonorDashboardPage.tsx
- src/services/impact.ts
- src/types/impact.ts

## 5) Dependencies added

Frontend package dependencies:

- leaflet
- react-leaflet
- recharts

## 6) Run commands

Backend:

```powershell
cd c:\Users\sahar\OneDrive\Desktop\Blood_Bank\Blood_Bank_Management_System\apps\backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd c:\Users\sahar\OneDrive\Desktop\Blood_Bank\Blood_Bank_Management_System\apps\frontend
npm install
npm run dev
```

## 7) Notes

- If backend APIs are unavailable, donor impact and urgent map screens include resilient fallback messaging.
- The urgent map requires requester hospital coordinates and source hospital coordinates to compute distances.
