# AI State

## Sprint Goal
Stabilize and ship the Blood Bank Management System with reliable backend and frontend quality gates, reproducible deployment, and operationally safe releases.

## Architecture Snapshot
- Monorepo with backend in `apps/backend`, frontend in `apps/frontend`, infrastructure in `infra`, and CI/CD workflows in `.github/workflows`.
- Backend stack: FastAPI, SQLAlchemy, Alembic, Pydantic settings, JWT auth.
- Frontend stack: React, TypeScript, Vite, Tailwind, React Router, Axios.
- Deployment targets: Render backend and Vercel frontend, with smoke-check automation in `scripts/deploy/smoke_check.py`.

## Current Baseline
- Database schema, auth, donor, inventory, and request APIs are in place under `/api/v1`.
- Frontend role-based portals and protected routing are in place for donor, admin, and hospital users.
- CI, deploy hook workflow, and release gate workflow are configured.

## Known Risks
- Production secrets and deploy hook URLs must be complete for release and deploy workflows to pass.
- Migrations must be applied before serving API in a new environment.
- CORS and frontend API base URL alignment must be validated per environment.

## Pending Tasks
1. Keep `AI_STATE.md` updated at the end of each substantial development session.
2. Continue phase work by prioritizing high-impact bug fixes and integration validation.
3. Maintain docs-to-code alignment when architecture or workflow behavior changes.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-18

#### 1. Architecture & Context Shifts
* Added workspace-level AI instruction bootstrap file at `.github/copilot-instructions.md`.
* Established `AI_STATE.md` as persistent session initialization context.

#### 2. What Was Accomplished
* Mapped and validated backend and frontend architecture boundaries from source files.
* Verified local build and quality commands from package/config/workflow files.
* Cataloged existing docs and linked them from workspace instructions.

#### 3. Known Issues & Tech Debt
* No new runtime code paths were changed in this session.
* Cross-platform command variants are not fully normalized across docs and workflows.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Enforce consistent env validation between local scripts and CI/deploy workflows.
* Step 2: Add targeted backend and frontend tests for high-risk flows.
* Step 3: Harden release verification with broader smoke checks and role-based API probes.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-18

#### 1. Architecture & Context Shifts
* Extracted donor impact computation from `apps/backend/app/api/v1/donors.py` into `apps/backend/app/services/donor_impact.py` to tighten router-service boundaries.
* Extracted blood request workflow helpers from `apps/backend/app/api/v1/requests.py` into `apps/backend/app/services/request_management.py` for request number generation, access checks, hospital resolution, and fulfillment timestamp transitions.
* Added frontend shared domain contract module `apps/frontend/src/types/domain.ts` and aligned consumer types to backend enum values.

#### 2. What Was Accomplished
* Refactored backend donor and request routers to consume service-layer business logic instead of embedding complex flows directly.
* Reworked frontend type contracts in `types/auth.ts`, `types/inventory.ts`, `types/request.ts`, and `types/routing.ts` to use shared domain aliases.
* Updated `RegisterDonorPage.tsx` and `InventoryTable.tsx` to consume shared domain constants and stricter filter/form types.
* Resolved one introduced export regression by re-exporting `BloodBagStatus` from `types/inventory.ts`.

#### 3. Known Issues & Tech Debt
* Backend pytest execution remains environment-sensitive: conda-based run fails on dotenv list parsing for `CORS_ORIGINS`, while workspace `.venv` currently lacks `pytest`.
* Frontend production build still fails on existing Leaflet typing issues in `src/components/maps/UrgentRoutingMap.tsx` that predate this step.
* Frontend dependencies were installed locally under `apps/frontend/node_modules` to enable typecheck/build validation.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Normalize backend test environment so `pytest -q` runs consistently across local and CI with stable settings parsing.
* Step 2: Fix Leaflet type integration for production build reliability and lock map component typings.
* Step 3: Continue Step 2 of the sprint by hardening auth/session handling and failure semantics after contract-boundary cleanup.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-18

#### 1. Architecture & Context Shifts
* Hardened backend settings bootstrapping by resolving env file path from backend root and supporting both CSV and JSON array parsing for CORS origins.
* Reworked frontend session handling from local storage token persistence to expiring in-memory plus session storage semantics with centralized 401 invalidation events.
* Added explicit degraded-mode UX surfaces for donor impact, inventory feed, and urgent routing workflows with deterministic retry actions.

#### 2. What Was Accomplished
* Implemented robust `cors_origins` parsing in `apps/backend/app/config.py` and added regression tests in `apps/backend/tests/test_config_settings.py`.
* Installed and wired Leaflet typings (`@types/leaflet`) and updated map coordinate typing in `apps/frontend/src/components/maps/UrgentRoutingMap.tsx`.
* Added `apps/frontend/src/lib/session.ts`, updated `apps/frontend/src/lib/api.ts` and `apps/frontend/src/context/AuthContext.tsx` for session expiry checks and unauthorized event-driven logout.
* Added reusable degraded-state component `apps/frontend/src/components/ui/DegradedStateBanner.tsx` and integrated it into inventory, donor impact, and urgent routing pages.
* Validated backend checks and frontend build gates in local runtime.

#### 3. Known Issues & Tech Debt
* Session hardening is still bearer-token based and does not yet include refresh-token rotation or server-managed revocation lists.
* Build validation succeeded locally, but repository-level guardrails still depend on maintaining one canonical Python interpreter selection in each developer setup.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Introduce refresh-token flow and secure token rotation boundaries across backend auth and frontend session handling.
* Step 2: Add centralized degraded-state telemetry/reporting so degraded mode transitions are observable in operations.
* Step 3: Extend automated test coverage for auth invalidation events and degraded-mode retry paths across portals.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-18 14:14:08 +05:30

#### 1. Architecture & Context Shifts
* Added frontend test harness support with Vitest + Testing Library and project-level test setup in `apps/frontend/src/test/setup.ts`.
* Introduced explicit regression coverage for auth invalidation and degraded-mode recovery flows across donor, inventory, and hospital portals.

#### 2. What Was Accomplished
* Added `AuthContext` invalidation tests in `apps/frontend/src/context/AuthContext.test.tsx` to validate unauthorized-event logout and bootstrap-failure session invalidation.
* Added degraded retry + telemetry transition tests in `apps/frontend/src/components/donor/DonorImpactDashboard.test.tsx`, `apps/frontend/src/components/inventory/InventoryTable.test.tsx`, and `apps/frontend/src/pages/hospital/HospitalUrgentPage.test.tsx`.
* Added shared test bootstrap in `apps/frontend/src/test/setup.ts` and updated frontend scripts/config for test execution (`package.json`, `vite.config.ts`).
* Executed validation gates: frontend `npm run test`, `npm run typecheck`, `npm run build`; backend `pytest -q`; backend `scripts/run_quality_checks.py`.

#### 3. Known Issues & Tech Debt
* Production build command output remains truncated in this shell integration, requiring exit-code verification rather than full terminal summary lines.
* Repository currently contains generated artifacts (`node_modules`, `package-lock.json`, `*.pyc`, `*.tsbuildinfo`) that should be reviewed for commit policy before final merge.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Add backend API tests for refresh token rotation/reuse-detection/logout-all behavior to match new auth session model.
* Step 2: Add telemetry API endpoint tests for degraded event ingestion/report retrieval and role access boundaries.
* Step 3: Review and clean generated artifacts from source control and finalize release branch with focused diffs.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-18 14:27:32 +05:30

#### 1. Architecture & Context Shifts
* Added backend API-level tests for auth session refresh rotation/reuse detection/logout-all behavior and telemetry endpoint role boundaries.
* Added backend artifact ignore policy in `apps/backend/.gitignore` and extended frontend ignore rules for TypeScript build metadata.

#### 2. What Was Accomplished
* Implemented `apps/backend/tests/test_auth_sessions_and_telemetry_api.py` with route-level coverage for `/auth/refresh`, `/auth/logout-all`, `/telemetry/degraded-state` POST and GET, including admin/non-admin/unauthenticated boundaries.
* Cleaned generated artifacts from workspace (`apps/backend/**/__pycache__`, `*.pyc`, and `apps/frontend/tsconfig.app.tsbuildinfo`) and verified they no longer appear in git status noise.
* Re-ran validation gates: backend `pytest -q` (11 passed) and frontend `npm run test` (5 passed).

#### 3. Known Issues & Tech Debt
* Repository currently appears as mostly untracked at root (`git status` shows top-level directories as new), so release finalization should include an intentional staging strategy to keep commit scope controlled.
* `rg` is unavailable in the current shell environment; PowerShell-native discovery commands were used for artifact auditing.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Stage only release-target files and generate a scoped change review before merge.
* Step 2: Expand backend tests to include edge cases for refresh expiry and inactive-user revocation reasons.
* Step 3: Run full backend quality script and frontend typecheck/build again immediately before release cut.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-18 14:37:58 +05:30

#### 1. Architecture & Context Shifts
* Extended auth session test surface to cover refresh expiry and inactive-user revocation reason paths in refresh workflow.
* Kept release staging scope constrained to four target files to isolate merge risk from broad untracked baseline.

#### 2. What Was Accomplished
* Added two new backend edge-case tests in apps/backend/tests/test_auth_sessions_and_telemetry_api.py for expired refresh token revocation reason expired and inactive-user revocation reason user_inactive.
* Generated scoped staged-change review using staged file list and staged diff stats before merge.
* Ran release-cut verification gates: backend scripts/run_quality_checks.py with 13 passing tests, frontend typecheck pass, frontend build artifact generation confirmed.

#### 3. Known Issues & Tech Debt
* Frontend build output in this shell can truncate after transformed modules summary, so artifact existence check is used as additional completion signal.
* Repository baseline remains mostly untracked and will require explicit repository initialization strategy beyond this scoped release set.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Perform intentional first commit(s) for repository baseline to reduce long-term staging noise.
* Step 2: Add targeted auth refresh tests for missing-user edge path and token hash lookup miss metrics.
* Step 3: Run release-gate workflow manually for staging and capture smoke-check artifacts before production deploy.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-18 15:12:40 +05:30

#### 1. Architecture & Context Shifts
* Added repo-level secret scanning guardrails with pre-commit and gitleaks configuration plus unified ignore policy coverage for env and secret artifacts.

#### 2. What Was Accomplished
* Added root hook configuration in .pre-commit-config.yaml and scanner policy in .gitleaks.toml.
* Added and updated ignore rules in .gitignore, apps/backend/.gitignore, and apps/frontend/.gitignore to prevent env, secret, and scanner artifact leakage.
* Installed pre-commit in the conda environment, installed hooks successfully, and validated with pre-commit run --all-files where gitleaks-secret-scan passed.

#### 3. Known Issues & Tech Debt
* First-time hook setup on Windows can leave a stale pre-commit lock when interrupted; recovery requires terminating stale installer processes and removing C:\Users\sahar\.cache\pre-commit\.lock.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Keep commit scope focused to security and release-target files only.
* Step 2: Add pre-commit bootstrap instructions to setup docs for new contributors.
* Step 3: Extend secret scanning into CI release gates for parity with local pre-commit checks.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-18 16:50:12 +05:30

#### 1. Architecture & Context Shifts
* Formalized a scope-lock snapshot for release execution with 7 staged files and 139 untracked baseline files kept out of the release slice.
* Added repository-memory execution notes for PowerShell npm policy fallback (`npm.cmd`) and PATH-independent pre-commit invocation via Python module.

#### 2. What Was Accomplished
* Generated and executed the first scope-lock run using staged-only validation.
* Ran staged-slice hook validation where gitleaks-secret-scan passed.
* Ran targeted backend tests (`tests/test_auth_sessions_and_telemetry_api.py`) with 9 passing tests.
* Ran full backend quality checks (`scripts/run_quality_checks.py`) with 13 passing tests.
* Ran frontend local gates (`typecheck` and `build`) using `npm.cmd` and verified successful completion via exit code and build artifact check.

#### 3. Known Issues & Tech Debt
* External CI and release-gate workflow runs are still pending and remain required before GO decision.
* Untracked repository baseline remains large and should be intentionally batched if additional scope is needed.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Trigger CI and Release Gate (staging and production) against the exact scoped commit.
* Step 2: Maintain strict staged-slice release unless a deliberate cohort-expansion plan is approved.
* Step 3: Capture deploy secret-readiness and rollback-target evidence for final Phase 1 GO or NO-GO.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-19 23:46:07 +05:30

#### 1. Architecture & Context Shifts
* Linked Vercel project for `apps/frontend` as `blood-bank-management-frontend` under `saharshavibes-projects` and established production alias routing.
* Added Vercel project environment configuration for `VITE_API_BASE_URL` on production and development targets using expected Render service URL pattern.

#### 2. What Was Accomplished
* Completed Vercel CLI authentication and project linking from terminal-first flow.
* Deployed frontend twice to production and confirmed active alias `https://blood-bank-management-frontend-black.vercel.app`.
* Validated public reachability check with frontend returning HTTP 200.
* Verified backend health endpoint candidates are not live yet, confirming backend deployment is still pending.

#### 3. Known Issues & Tech Debt
* GitHub CLI remains unauthenticated in this session, which blocks terminal-based GitHub secrets provisioning and workflow dispatch.
* Render backend is not deployed yet and no `RENDER_API_KEY` is configured in shell, preventing API-driven provisioning from terminal.
* Vercel preview environment variable branch binding requires connected Git integration and is currently unavailable for this project state.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Complete `gh auth login` device flow and verify with `gh auth status`.
* Step 2: Provision or link Render backend service from `render.yaml`, set required env vars (`DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ORIGINS`), and validate `/api/v1/health`.
* Step 3: Update Vercel `VITE_API_BASE_URL` if backend URL differs, redeploy frontend, and then execute release/deploy workflow chain.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-20 00:00:51 +05:30

#### 1. Architecture & Context Shifts
* Connected GitHub CLI auth for repository-level workflow and secrets automation.
* Established partial GitHub Actions secret baseline for production URL resolution (`FRONTEND_URL*`, `BACKEND_HEALTH_URL*`, `BACKEND_AUTH_LOGIN_URL*`).

#### 2. What Was Accomplished
* Completed `gh auth login` and verified active account/token scope using `gh auth status`.
* Triggered Release Gate run `24635968981` to validate initial secret requirements and observed expected missing-backend-url stop.
* Added frontend and backend URL secrets, then reran Release Gate as run `24636020084`; backend/frontend quality jobs passed and smoke gate reached runtime probe stage.
* Triggered Deploy workflow run `24636095081` and captured hard failure on missing deploy hooks (`RENDER_DEPLOY_HOOK_URL`, `VERCEL_DEPLOY_HOOK_URL`).

#### 3. Known Issues & Tech Debt
* Production deploy workflow remains blocked until both deploy hook secrets are provisioned.
* Current backend URL assumption (`bbms-backend.onrender.com`) responds with non-FastAPI 404 payload (`Cannot GET /api/v1/health`), indicating endpoint mismatch or undeployed target.
* Vercel project is not connected to Git integration yet, so Vercel deploy hooks and branch-scoped preview env wiring cannot be created from CLI.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Connect Vercel project to GitHub repository in Vercel settings and generate `VERCEL_DEPLOY_HOOK_URL_PRODUCTION` (or fallback key).
* Step 2: Provision/verify Render backend service URL and create `RENDER_DEPLOY_HOOK_URL_PRODUCTION`, then correct backend URL secrets to the actual live endpoint.
* Step 3: Re-run `release-gate.yml` and `deploy.yml` for production after hook and URL corrections, then confirm smoke-check pass.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-20 01:09:54 +05:30

#### 1. Architecture & Context Shifts
* Increased deployment smoke-check resilience in `.github/workflows/deploy.yml` and `.github/workflows/release-gate.yml` by passing `--retries 24 --delay-seconds 10`.
* Updated backend container runtime in `apps/backend/Dockerfile` to bind `uvicorn` to `${PORT:-8000}` for Render compatibility.

#### 2. What Was Accomplished
* Provisioned production/fallback GitHub secrets for deploy hooks and backend/frontend endpoint URLs.
* Triggered and analyzed release/deploy workflow runs to isolate failures: `24636859428`, `24637036475`, and follow-up push-triggered runs.
* Confirmed deploy hook steps now execute successfully in `deploy.yml` with configured secret set.
* Committed and pushed workflow + runtime fixes in commits `aa435ec` and `4d3b4b6`.

#### 3. Known Issues & Tech Debt
* Latest push-triggered deploy run (`24637315412`) is still in progress at checkpoint time, with smoke check waiting on backend readiness.
* Backend health URL `https://bbms-backend-ff6b.onrender.com/api/v1/health` currently returns 503 from external probing, indicating Render app availability issues remain.
* Vercel project is still not Git-connected in Vercel dashboard, limiting branch-scoped preview variable workflows and CLI deploy-hook management semantics.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Confirm outcome/logs of run `24637315412` and validate if backend health transitions to 200 after Render redeploy completes.
* Step 2: If backend remains unavailable, inspect Render service logs and runtime env at platform level, then correct startup/runtime faults.
* Step 3: Re-run `release-gate.yml` production after deploy success to capture end-to-end green evidence.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-21 — Comprehensive Audit & Deployment Roadmap

#### 1. Architecture & Context Shifts
* Conducted full deployment audit targeting a 16 GB CPU-only host. Roadmap persisted at `C:\Users\Muzaffar\.claude\plans\mission-execute-an-merry-walrus.md`.
* Confirmed stack is CPU-pure: zero GPU/ML dependencies in `apps/backend/requirements.txt`; no torch/transformers/faiss/vllm anywhere in tree.
* Verified Alembic env.py metadata is complete — `app/models/__init__.py` re-exports all seven models, so `Base.metadata` registers `RefreshToken` and `DegradedStateEvent` despite env.py only naming five symbols. An earlier "missing import" reading was a false positive.

#### 2. What Was Accomplished
* Mapped 25 backend endpoints; confirmed 18 have no frontend caller (full CRUD on donors/inventory/requests, plus admin registration and logout-all). Logged as RBAC-coverage risk, not a deploy blocker.
* Produced gap matrix grading every deployment-relevant feature P0–P3 across migrations, resource limits, worker concurrency, secret hygiene, network exposure, log rotation, and schema completeness.
* Validated FK constraints, Enum values, and Pydantic IO contracts align with Alembic schema for every wired endpoint.

#### 3. Known Issues & Tech Debt
* **P0 — Container does not self-bootstrap DB.** `apps/backend/Dockerfile:22` runs uvicorn directly; fresh `docker compose -f infra/docker-compose.prod.yml up` leaves an empty schema. Fix: add `apps/backend/scripts/entrypoint.sh` that runs `alembic upgrade head` before exec'ing uvicorn.
* **P0 — No `deploy.resources.limits` in `infra/docker-compose.prod.yml`.** A single OOM event on a 16 GB host can take down Postgres. Proposed caps: postgres 4 GB / 2 cpu, backend 2 GB / 1.5 cpu, frontend 256 MB / 0.5 cpu.
* **P1 — Working defaults templated for `JWT_SECRET_KEY` and `POSTGRES_PASSWORD`** in `infra/docker-compose.prod.yml`. Replace with `${VAR:?...required}` to fail before image build instead of after.
* **P1 — Single uvicorn worker + sync psycopg2** blocks all requests on long queries. Set `WEB_CONCURRENCY=2` via the entrypoint script.
* **P1 — Postgres published on 0.0.0.0** with default creds. Bind to `127.0.0.1` in self-host compose.
* **P2 — Hospital lacks Pydantic IO schemas** under `app/schemas/`. Future endpoints returning Hospital rows could leak the ORM model.
* **P2 — Frontend nginx logs unbounded** (default json-file driver, no max-size). Disk-fill scenario.
* **P2 — No `infra/HOST_PREFLIGHT.md`** capturing swap setup and the single "go" command for self-host.
* **P3 — `Numeric(9,6)` lat/long mapped to Python `float`** in `app/models/hospital.py:30-31`. Sub-meter routing drift.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Implement Step A1 of the audit roadmap — entrypoint script + Dockerfile change so `docker compose up` self-bootstraps the database. Recursive prompt is captured in the plan file.
* Step 2: Apply Step B1–B3 — resource limits, json-file log rotation (10m × 5), localhost-bind Postgres in `infra/docker-compose.prod.yml`.
* Step 3: Add `infra/HOST_PREFLIGHT.md` and `apps/backend/app/schemas/hospital.py`; verify end-to-end with `scripts/deploy/smoke_check.py` against the local prod stack.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-21 — Step A1 Implementation: Self-Bootstrapping Backend Container

#### 1. Architecture & Context Shifts
* Backend image now self-bootstraps the schema. New `apps/backend/scripts/entrypoint.sh` runs `alembic upgrade head` then exec's uvicorn. `apps/backend/Dockerfile` switched its `CMD` to `["/entrypoint.sh"]` and now also `COPY`s `alembic.ini` (previously missing — would have made `alembic upgrade head` inside the image impossible).
* `WEB_CONCURRENCY` env var now drives uvicorn `--workers` (default 2). `PORT` env var fallback (`${PORT:-8000}`) preserved.

#### 2. What Was Accomplished
* Created `apps/backend/scripts/entrypoint.sh` (POSIX sh, `set -e`, LF line endings verified via `od -c`).
* Patched `apps/backend/Dockerfile`: added `COPY alembic.ini ./alembic.ini`, `COPY scripts/entrypoint.sh /entrypoint.sh`, `RUN chmod +x /entrypoint.sh`, replaced `CMD` with `["/entrypoint.sh"]`.
* Confirmed `apps/backend/.dockerignore` does not exclude `scripts/` or `alembic.ini` (it only filters venv/cache/git artifacts).
* Resolved the Step A1 P0 finding: a fresh `docker compose -f infra/docker-compose.prod.yml up` will now apply migrations before serving traffic.

#### 3. Known Issues & Tech Debt
* **Verification deferred to operator.** Local Docker daemon was not running during this session, so the build/run smoke could not be executed in-loop. The intended verification: `cd apps/backend && docker build -t bbms-backend:a1 . && docker run --rm -e DATABASE_URL=postgresql+psycopg2://bbms_user:bbms_password@host.docker.internal:5432/blood_bank -e JWT_SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(48))") -p 8000:8000 bbms-backend:a1` then `curl http://localhost:8000/api/v1/health` (expect `{"status":"ok"}`) and `psql … -c "select * from alembic_version;"` (expect head revision row).
* Step B1–B3 (resource limits, log rotation, localhost-bind Postgres) and Step A2 (`${VAR:?required}` for JWT/POSTGRES secrets) remain outstanding from the audit roadmap.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Run the deferred Docker build/run verification on a host with Docker Desktop running and confirm `alembic_version` populates and `/api/v1/health` returns ok.
* Step 2: Implement Step A2 — drop the `JWT_SECRET_KEY` and `POSTGRES_PASSWORD` defaults in `infra/docker-compose.prod.yml` to `${VAR:?...required}` form.
* Step 3: Implement Steps B1–B3 — `deploy.resources.limits` per service, `logging.driver=json-file` with `max-size=10m, max-file=5`, and bind Postgres to `127.0.0.1` in self-host compose.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-21 — Step A2 Implementation: Fail-Fast Secret Templating

#### 1. Architecture & Context Shifts
* `infra/docker-compose.prod.yml` no longer templates working defaults for the two true secrets. `${POSTGRES_PASSWORD:-bbms_password}` → `${POSTGRES_PASSWORD:?POSTGRES_PASSWORD required}` (in both the `postgres.environment` block and the backend `DATABASE_URL` interpolation). `${JWT_SECRET_KEY:-change-this-secret-key}` → `${JWT_SECRET_KEY:?JWT_SECRET_KEY required}`.
* Non-secret defaults (`POSTGRES_DB`, `POSTGRES_USER`, `APP_NAME`, ports, etc.) intentionally kept — only credential material was promoted to required.

#### 2. What Was Accomplished
* Patched three lines in `infra/docker-compose.prod.yml` (lines 9, 32, 33).
* Verified fail-fast: `docker compose -f docker-compose.prod.yml config` (with no `.env.prod` loaded) now exits non-zero with `required variable POSTGRES_PASSWORD is missing a value: POSTGRES_PASSWORD required` — interpolation fails before any image is built or pulled.

#### 3. Known Issues & Tech Debt
* `infra/.env.prod.example` should still be reviewed under Step B5 to ensure the example file documents `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` clearly (and to add `WEB_CONCURRENCY=2` while there).
* Steps B1–B3 (resource limits, log rotation, localhost-bind Postgres) and Step A3 (`HospitalRead`/`HospitalUpdate` schemas) remain outstanding from the audit roadmap.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Implement Step A3 — add `apps/backend/app/schemas/hospital.py` with `HospitalRead`/`HospitalUpdate` mirroring the donor schema style.
* Step 2: Implement Steps B1–B3 — `deploy.resources.limits` per service, `logging.driver=json-file` with `max-size=10m, max-file=5`, and bind Postgres to `127.0.0.1` in self-host compose.
* Step 3: Implement Step B5 — refresh `infra/.env.prod.example` to include `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, and `WEB_CONCURRENCY` with documenting comments (example file only).

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-21 — Step A3 Implementation: Hospital Pydantic IO Schemas

#### 1. Architecture & Context Shifts
* New file `apps/backend/app/schemas/hospital.py` defines `HospitalRead` (full ORM-compatible read model with `model_config = ConfigDict(from_attributes=True)`) and `HospitalUpdate` (all fields optional, `latitude`/`longitude` bounded with `ge`/`le` to mirror the DB CheckConstraints `hospitals_lat_range` and `hospitals_lng_range`).
* Schema mirrors the donor schema style — same import set, same field-style, same ConfigDict pattern. Field max-lengths (`name=200`, `city=100`, `contact_phone=30`) match the SQLAlchemy `String(N)` widths in `app/models/hospital.py`.
* `HospitalRegisterRequest` in `app/schemas/auth.py` is unchanged — registration is auth-bound and stays there; the new schemas cover the read/update half that was previously missing.

#### 2. What Was Accomplished
* Created `apps/backend/app/schemas/hospital.py` (31 lines, zero comments).
* Verified AST parse and `py_compile` clean. Pydantic runtime import was not exercised because the system Python does not have project deps; full runtime validation will happen on the next CI run / `pytest -q`.
* Closed the P2 latent leak risk: any future endpoint that returns a Hospital row can now serialize through `HospitalRead` instead of leaking the ORM object.

#### 3. Known Issues & Tech Debt
* No backend route currently consumes `HospitalRead`/`HospitalUpdate`. Wiring will land naturally with the next Hospital-facing endpoint (admin update flow, hospital profile read, etc.).
* `latitude`/`longitude` typed as `float` in both ORM and schema preserves the `Numeric(9,6) → float` round-trip noted as P3 in the audit; out of scope for this step.
* Steps B1–B3 (resource limits, log rotation, localhost-bind Postgres) and Step B5 (`.env.prod.example` refresh) remain outstanding from the audit roadmap.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Implement Steps B1–B3 — `deploy.resources.limits` per service, `logging.driver=json-file` with `max-size=10m, max-file=5`, and bind Postgres to `127.0.0.1` in self-host compose.
* Step 2: Implement Step B5 — refresh `infra/.env.prod.example` to include `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, and `WEB_CONCURRENCY` with documenting comments (example file only).
* Step 3: Run the deferred Docker build/run verification on a host with Docker Desktop running and confirm `alembic_version` populates and `/api/v1/health` returns ok.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-21 — Steps B1–B3 Implementation: Deployment Shield

#### 1. Architecture & Context Shifts
* `infra/docker-compose.prod.yml` is now hardened for a 16 GB CPU-only host:
  * **Resource limits (B1)** — `postgres: 4G/2.0 cpu`, `backend: 2G/1.5 cpu`, `frontend: 256M/0.5 cpu` via `deploy.resources.limits` (compose v2 honors this in non-swarm mode). Total ceiling ~6.25 GB, leaving ~9 GB for OS + swap headroom.
  * **Postgres tuning (B1)** — `command:` override sets `shared_buffers=1GB`, `effective_cache_size=2GB`, `work_mem=16MB`, `max_connections=50`. The 50-conn cap is intentional: `WEB_CONCURRENCY=2 × pool_size~5 × 2 services = ~20 sessions`, with headroom for migrations and maintenance.
  * **Worker concurrency (B1)** — backend env now exports `WEB_CONCURRENCY: ${WEB_CONCURRENCY:-2}`. The Step A1 entrypoint script consumes this for `uvicorn --workers`.
  * **Log rotation (B2)** — all three services pinned to `json-file` driver with `max-size=10m, max-file=5` (50 MB ceiling per service).
  * **Network isolation (B3)** — Postgres port binding now reads `${POSTGRES_BIND_HOST:-127.0.0.1}:${POSTGRES_PORT:-5432}:5432`. Default loopback-only; operator opts into LAN exposure by setting `POSTGRES_BIND_HOST=0.0.0.0` in `.env.prod`. Backend reaches Postgres via the docker network as `postgres:5432` regardless — host bind is unrelated to inter-container traffic.
* `infra/.env.prod.example` documents both `POSTGRES_BIND_HOST` (with the loopback rationale) and `WEB_CONCURRENCY` (2-worker baseline for 16 GB host).

#### 2. What Was Accomplished
* Rewrote `infra/docker-compose.prod.yml` to add `command`, `deploy.resources.limits`, `logging`, and `WEB_CONCURRENCY` blocks; switched Postgres port binding to host-ip parameterized with a 127.0.0.1 default.
* Patched `infra/.env.prod.example` with `POSTGRES_BIND_HOST` and `WEB_CONCURRENCY` lines plus documenting comments (example file only — no comments leaked into compose or app code).
* Verified via `docker compose -f docker-compose.prod.yml config`: rendered output shows `host_ip: 127.0.0.1` on Postgres, `cpus: 1.5 / memory: 2147483648` on backend, `cpus: 0.5 / memory: 268435456` on frontend, `cpus: 2.0 / memory: 4294967296` on Postgres, and the json-file logging block on all three.
* Closed P0 (no resource limits) and P1 (Postgres exposed on 0.0.0.0) findings from the gap matrix in a single compose pass.

#### 3. Known Issues & Tech Debt
* `deploy.resources.limits` is honored by `docker compose up` (v2.x) on non-swarm runtimes but is silently ignored by older `docker-compose v1`. Operators on legacy CLI must upgrade to `docker compose` (the v2 plugin) — document in `HOST_PREFLIGHT.md` (Step B4, still outstanding).
* `pool_size` in `app/database/session.py` should be sanity-checked against the new `max_connections=50` ceiling on next backend touch.
* Steps B4 (HOST_PREFLIGHT.md) and B5 (full `.env.prod.example` refresh — strip working defaults from secrets) remain outstanding.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Implement Step B4 — write `infra/HOST_PREFLIGHT.md` with swap setup (`fallocate -l 4G /swapfile` …), Docker daemon notes, expected free RAM/disk, and the single "go" command.
* Step 2: Implement Step B5 — strip the `bbms_password` and `replace-with-a-strong-secret` placeholders from `infra/.env.prod.example` so the file communicates intent without templating fake values.
* Step 3: Run the deferred Docker build/run verification on a host with Docker Desktop running and confirm `alembic_version` populates and `/api/v1/health` returns ok.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-21 — Step B4 Implementation: Host Pre-Flight Runbook

#### 1. Architecture & Context Shifts
* New doc `infra/HOST_PREFLIGHT.md` captures every operator pre-condition for a single-tenant 16 GB self-host: Docker Engine ≥ 24 with Compose v2 plugin (calls out the v1 silently-ignores-limits trap from the B1–B3 caveat), 16 GB RAM / 30 GB disk, outbound HTTPS to Docker Hub.
* Documents 4 GB swap setup (`fallocate` + `swapon` + `/etc/fstab` + `vm.swappiness=10`) sized for migration and Vite-build spikes.
* Documents `/etc/docker/daemon.json` ulimit and host-level log-driver defaults so unmanaged sidecar containers also stay bounded.
* Single-line "go" command: `cd infra && cp .env.prod.example .env.prod && $EDITOR .env.prod && docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build`.
* Smoke commands explicitly call out the three things to verify: `/api/v1/health`, `docker stats --no-stream`, and an `alembic_version` row at head.

#### 2. What Was Accomplished
* Created `infra/HOST_PREFLIGHT.md` (≈55 lines, terse). Codifies the Step A1 self-bootstrap, A2 fail-fast secrets, B1 resource limits, B2 log rotation, and B3 loopback Postgres into a single operator-facing runbook.
* Reinforced the B3 LAN-exposure warning (rotate `POSTGRES_PASSWORD` before flipping `POSTGRES_BIND_HOST` to `0.0.0.0`).

#### 3. Known Issues & Tech Debt
* `HOST_PREFLIGHT.md` assumes a Linux host. Windows/macOS Docker Desktop operators get the swap section as inert reading material; a dedicated section for Docker Desktop tuning (memory slider in Settings → Resources) is a nice-to-have but not a deploy blocker.
* Step B5 (`.env.prod.example` placeholder cleanup) and the deferred Docker build/run smoke remain outstanding.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Implement Step B5 — strip the `bbms_password` and `replace-with-a-strong-secret` placeholders from `infra/.env.prod.example` so the example file communicates required-secret intent without templating fake values.
* Step 2: Run the deferred Docker build/run verification on a host with Docker Desktop running and confirm `alembic_version` populates and `/api/v1/health` returns ok per the new `HOST_PREFLIGHT.md` smoke block.
* Step 3: Optional — sanity-check `pool_size` in `app/database/session.py` against the new Postgres `max_connections=50` ceiling.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-21 — Step B5 Implementation: Example File Hardening + Audit Steps A1–B5 Complete

#### 1. Architecture & Context Shifts
* `infra/.env.prod.example` rewritten: `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` are now empty by design with a leading "Required secrets" comment block explaining why and pointing to `python -c "import secrets;print(secrets.token_urlsafe(48))"` for the JWT secret. The file no longer templates a working fallback that an operator might ship to prod.
* Reorganized into four titled sections (Required secrets / Postgres / Backend / Frontend) for scan-ability.
* End-to-end fail-fast contract verified: `docker compose --env-file .env.prod.example -f docker-compose.prod.yml config` exits non-zero with `required variable POSTGRES_PASSWORD is missing a value: POSTGRES_PASSWORD required`. The example file proves the safety mechanism rather than working around it.

#### 2. What Was Accomplished
* Rewrote `infra/.env.prod.example` (28 lines) — empty required secrets, organized sections, terse documenting comments (example file only — no comments leaked into compose, app, or scripts).
* Closed the entire **Step A (STRICT REFACTOR)** and **Step B (DEPLOYMENT SHIELD)** blocks of the audit roadmap at `C:\Users\Muzaffar\.claude\plans\mission-execute-an-merry-walrus.md`. All compose-layer and Dockerfile-layer P0/P1/P2 findings from the gap matrix are addressed.

#### 3. Known Issues & Tech Debt
* Only the **Step C (VERIFICATION)** Docker build/run smoke remains deferred — needs a live Docker daemon. Operator can run it directly using `infra/HOST_PREFLIGHT.md` as the script.
* Optional follow-up: sanity-check `pool_size` in `app/database/session.py` against the new Postgres `max_connections=50` ceiling on the next backend touch.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Operator runs the deferred Docker build/run smoke from `infra/HOST_PREFLIGHT.md` and confirms `alembic_version` populates and `/api/v1/health` returns ok.
* Step 2: Re-trigger `release-gate.yml` and `deploy.yml` against staging/production with the hardened compose to make sure CI didn't depend on any of the templated defaults.
* Step 3: Optional — `pool_size` sanity check against `max_connections=50`; revisit P3 items from the gap matrix (frontend caller coverage for the 18 unwired endpoints, `Numeric(9,6) → float` routing precision).

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-21 — B9 Type-Honesty Fix + Phase 1/2 Closure

#### 1. Architecture & Context Shifts
* `app/models/hospital.py` now types the lat/long ORM attributes as `Decimal | None` (matching what psycopg2 actually returns for `Numeric(9, 6)`). Added `from decimal import Decimal`. The ORM now tells the truth.
* `app/api/v1/auth.py` converts incoming `payload.latitude`/`payload.longitude` (Pydantic `float | None` at the API boundary) to `Decimal(str(...))` before passing to the `Hospital` constructor. Using `Decimal(str(x))` avoids the `Decimal(float) → long-tail-binary-artefact` trap.
* `app/services/routing.py` was already correct — it explicitly `float(...)`-casts the Decimal attributes before passing them to haversine math. No change needed there.
* API contracts (`HospitalRead`, `HospitalRegisterRequest`, `RoutingCandidate`, `RoutingHospitalPoint`) remain `float` — the boundary layer where float is the right primitive for JSON.

#### 2. What Was Accomplished
* B9 closed: ORM type annotation no longer lies about the runtime type of lat/long. Full storage-layer precision (`Numeric(9, 6)` = 6 decimal places ≈ 11 cm lat resolution) is preserved end-to-end; only the haversine computation step lossily casts to `float`, which is appropriate (haversine itself has spherical-earth noise well above the Decimal → float gap).
* Verified: `py_compile` clean on both `app/models/hospital.py` and `app/api/v1/auth.py`. No tests exercise lat/long so no regression surface in the test suite.

**Phase 2 findings final mapping — all 9 closed:**
* B1 (migrations not bootstrapped in container) → closed by Phase 4 Step A1 (entrypoint script).
* B2 (no memory/CPU caps) → closed by Phase 4 Step B1 (`deploy.resources.limits`).
* B3 (worker count unmanaged) → closed by Phase 4 Step A1 + B1 (`WEB_CONCURRENCY=2`).
* B4 (JWT/Postgres secret defaults) → closed by Phase 4 Step A2 (`${VAR:?required}`).
* B5 (Postgres exposed on 0.0.0.0) → closed by Phase 4 Step B3 (`POSTGRES_BIND_HOST=127.0.0.1`).
* B6 (no swap/pre-flight) → closed by Phase 4 Step B4 (`infra/HOST_PREFLIGHT.md`).
* B7 (frontend nginx logs unbounded) → closed by Phase 4 Step B2 (json-file `max-size=10m, max-file=5`).
* B8 (Hospital lacks Pydantic schemas) → closed by Phase 4 Step A3 (`HospitalRead`/`HospitalUpdate`).
* B9 (Numeric(9,6) ↔ float roundtrip) → closed in this update.

**Phase 1 findings final mapping:**
* Stack reality (CPU-pure, pinned deps) — unchanged, still true.
* Dead logic surface (18 of 25 endpoints have no frontend caller) — logged as RBAC-coverage risk in the memory from 2026-04-21 audit entry; not a deploy blocker, intentionally left for separate follow-up.
* Schema integrity (Alembic env.py metadata complete) — confirmed, no change.

#### 3. Known Issues & Tech Debt
* Only **Phase 4 Step C (Docker build/run smoke)** remains deferred — requires a live Docker daemon. Operator can execute directly from `infra/HOST_PREFLIGHT.md`.
* Dead-endpoint surface (18 unwired backend endpoints) remains open as a future RBAC/test-coverage initiative; not a deployment blocker.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Operator runs the deferred Docker build/run smoke from `infra/HOST_PREFLIGHT.md` on a host with Docker Desktop running.
* Step 2: Re-trigger `release-gate.yml` and `deploy.yml` against staging with the hardened compose to confirm no CI step depended on the templated defaults that were removed in Step A2/B5.

---

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-21

#### 1. Architecture & Context Shifts
* **Phase 4 Step C executed end-to-end on a live Docker daemon (29.3.1, Compose v2 plugin).** Audit plan at `C:\Users\Muzaffar\.claude\plans\mission-execute-an-merry-walrus.md` is now 100% executed; nothing deferred.
* `infra/.env.prod` now exists on this machine with generated secrets (`secrets.token_urlsafe(48)` for JWT, `secrets.token_urlsafe(32)` for Postgres). File is gitignored; do not commit. Rotate before any LAN exposure.
* `infra_postgres_prod_data` volume was preserved through teardown — next `up` will skip migrations replay (entrypoint `alembic upgrade head` is idempotent).

#### 2. What Was Accomplished
* **Build:** `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build` succeeded on first try. Backend image built with A1 layers (alembic.ini + entrypoint.sh) present.
* **Bootstrap (A1 live proof):** Backend entrypoint logs show `alembic.runtime.migration` applied both revisions (`20260413_000001` initial schema → `20260418_000002` auth sessions + telemetry) before uvicorn started. Parent process + 2 workers spawned (matching `WEB_CONCURRENCY=2`).
* **Smoke — all green with evidence:**
  * `GET /api/v1/health` → `{"status":"ok"}` HTTP 200
  * `GET /api/v1/health/migration-state` → `{"aligned":true,"expected_heads":["20260418_000002"],"current_versions":["20260418_000002"]}` HTTP 200
  * `GET http://localhost:8080/` → HTTP 200 (nginx serving Vite build)
  * `scripts/deploy/smoke_check.py` → "Smoke checks passed" (frontend 200, backend-health 200, cors 200)
* **Resource limits (B1 live proof):** `docker inspect` confirms `HostConfig.Memory` and `NanoCpus` match exactly: postgres 4294967296 / 2.0 cpu, backend 2147483648 / 1.5 cpu, frontend 268435456 / 0.5 cpu. `docker stats --no-stream` at idle: postgres 66.57 MiB (1.63%), backend 160.4 MiB (7.83%), frontend 12.38 MiB (4.84%) — every container is well under its declared cap at cold start.
* **Log rotation (B2 live proof):** All three containers confirmed via `docker inspect` as `json-file` driver with `max-size=10m max-file=5` → 50 MB cap per service → ~150 MB total log ceiling across the stack.
* **Bind scope (B3 live proof):** `docker port bbms_postgres_prod` returned `5432/tcp -> 127.0.0.1:5432`. Postgres is reachable only on loopback; LAN exposure requires explicit `POSTGRES_BIND_HOST` override per `HOST_PREFLIGHT.md`.
* **Fail-fast contract (A2 live proof):** A `docker compose ps` call without `--env-file` failed with `required variable POSTGRES_PASSWORD is missing a value: POSTGRES_PASSWORD required`. Confirmed the `${VAR:?msg}` interpolation aborts the client before any container starts.
* **Teardown:** `docker compose down` removed all containers + network; `docker volume ls` confirms `infra_postgres_prod_data` survives.

#### 3. Known Issues & Tech Debt
* **Backend and frontend have no Docker healthcheck stanza** in `docker-compose.prod.yml` — they never report `(healthy)` in `docker compose ps`, only `Up`. Not a failure; an observability gap. A future enhancement could add `curl -fsS localhost:8000/api/v1/health` as the backend healthcheck so compose itself waits on readiness during `up --wait` / `depends_on: condition: service_healthy` scenarios.
* `.env.prod` is local-only and contains real secrets; it must stay gitignored. Preflight doc already warns on rotation before LAN exposure — kept.
* Dead-endpoint surface (18 unwired backend endpoints) still open as future RBAC/test-coverage initiative.

#### 4. Next Session Action Plan (Next Steps)
* Entire audit roadmap is closed. Remaining candidates (operator's choice):
  * Add healthcheck stanza to backend/frontend services so `docker compose ps` reports `(healthy)` accurately.
  * Produce an RBAC test matrix for the 18 unwired backend endpoints (P3 from the Gap Matrix).
  * Revisit the auth-persistence UX decision (sessionStorage vs localStorage) — P3, product call.
* Step 3: Plan a separate initiative for the 18 unwired endpoints — either wire frontend consumers or prune backend routes to match actual product surface.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-24 — Demo Seed Script for Admin Dataset Hydration

#### 1. Architecture & Context Shifts
* Added standalone backend seed module at `apps/backend/scripts/seed_demo_data.py` to initialize a deterministic demo dataset with strict idempotency for repeated runs.
* Seed flow now guarantees presence of admin login credentials (`admin@bloodbank.local`) without relying on API bootstrap endpoints.

#### 2. What Was Accomplished
* Implemented `python -m scripts.seed_demo_data` module entrypoint using `SessionLocal` and `get_password_hash` from `app.auth.security`.
* Added idempotent admin upsert, hospital + donor user provisioning, blood bag inventory generation, blood request generation, and degraded-state telemetry baseline insertion.
* Seed logic prevents duplicate rows by resolving existing records via stable business keys (emails, bag numbers, request numbers, event signature tuples) before create/update.

#### 3. Known Issues & Tech Debt
* `AdminDashboardPage.tsx` currently renders static snapshot cards and does not yet consume dashboard aggregate APIs, so seeded data primarily hydrates inventory/request/admin-operational flows rather than the static cards themselves.
* Staging deployment validation remains separate from local/demo seeding and still depends on configured hook secrets.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Run `python -m scripts.seed_demo_data` in backend runtime and verify admin login plus inventory/request list hydration from live endpoints.
* Step 2: If dashboard cards are to be live-driven, add backend aggregate endpoint and replace static `snapshots` constants in the admin dashboard page.
* Step 3: Extend seed script with optional cleanup/reset mode when deterministic test snapshots are needed for CI smoke environments.

### 🧠 MEMORY UPDATE
**Date/Time:** 2026-04-24 — Windows Backend Environment Repair + Seed Execution Attempt

#### 1. Architecture & Context Shifts
* Updated admin seed identity in `apps/backend/scripts/seed_demo_data.py` to the requested credentials (`saharshabattula41@gmail.com` / `<Blood_bank@123>`) while preserving existing idempotent seed behavior.
* Windows shell environment was normalized for backend local execution by setting PowerShell execution policy to `RemoteSigned` at `CurrentUser` scope.

#### 2. What Was Accomplished
* Repaired and reinstalled backend dependencies in `apps/backend/.venv` from `apps/backend/requirements.txt`.
* Verified dependency installation state through venv pip output (`Requirement already satisfied` across backend package set).
* Executed `python -m scripts.seed_demo_data` from `apps/backend` and captured full runtime trace.

#### 3. Known Issues & Tech Debt
* Seed execution is currently blocked by local PostgreSQL authentication mismatch:
  * `DATABASE_URL` from `apps/backend/.env` points to `postgresql+psycopg2://bbms_user:bbms_password@localhost:5432/blood_bank`.
  * Runtime failure: `psycopg2.OperationalError: password authentication failed for user "bbms_user"`.
* Docker CLI is unavailable on this machine (`docker` command not found), so containerized fallback seeding cannot be used in this environment without installing Docker Desktop or providing another reachable PostgreSQL target.

#### 4. Next Session Action Plan (Next Steps)
* Step 1: Provide the correct local PostgreSQL credentials (or a valid `DATABASE_URL`) and rerun `python -m scripts.seed_demo_data`.
* Step 2: If local Postgres is not intended, install Docker Desktop and run the backend container stack with known credentials before reseeding.
* Step 3: Verify admin login using `saharshabattula41@gmail.com` and `<Blood_bank@123>` after successful seed completion.
