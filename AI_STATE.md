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