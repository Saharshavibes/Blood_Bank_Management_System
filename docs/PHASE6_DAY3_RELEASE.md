# Phase 6 Day 3: Release Hardening Runbook

## 1) Release objective

Create a repeatable go-live process with strict quality gates, deployment verification, and rollback steps.

## 2) Automated gates

### CI gate

- Workflow: .github/workflows/ci.yml
- Validates backend compile/tests/migrations and frontend typecheck/build.

### Deploy gate

- Workflow: .github/workflows/deploy.yml
- Triggers deploy hooks and verifies live endpoints.
- Production deploy requires deploy hooks and endpoint URLs.

### Release gate

- Workflow: .github/workflows/release-gate.yml
- Runs backend and frontend quality gates, then verifies backend migration-state alignment before deployment smoke checks.
- Supports `staging` and `production` targets.

## 3) Required GitHub secrets

Production:

- RENDER_DEPLOY_HOOK_URL_PRODUCTION
- VERCEL_DEPLOY_HOOK_URL_PRODUCTION
- BACKEND_HEALTH_URL_PRODUCTION
- BACKEND_AUTH_LOGIN_URL_PRODUCTION
- FRONTEND_URL_PRODUCTION

Staging:

- RENDER_DEPLOY_HOOK_URL_STAGING
- VERCEL_DEPLOY_HOOK_URL_STAGING
- BACKEND_HEALTH_URL_STAGING
- BACKEND_AUTH_LOGIN_URL_STAGING
- FRONTEND_URL_STAGING

Legacy fallback secrets are no longer supported by the workflows.

## 4) Go-live sequence

1. Confirm CI is green on the release commit.
2. Run Release Gate workflow for staging.
3. Run Deploy workflow for staging and verify smoke checks.
4. Run Release Gate workflow for production.
5. Run Deploy workflow for production.
6. Execute manual sanity checks from product flows.

## 5) Manual sanity checks

1. Open frontend URL and confirm the login page renders.
2. Submit invalid credentials and confirm a controlled auth failure.
3. Login with a valid role account and verify role redirect.
4. Confirm health endpoint returns status=ok.
5. Confirm at least one protected API call succeeds from UI.

## 6) Rollback playbook

### Frontend rollback (Vercel)

1. Open Vercel project deployments.
2. Promote the last known good deployment.
3. Re-run smoke checks against the promoted URL.

### Backend rollback (Render)

1. Open Render service deploy history.
2. Roll back to the last healthy deployment.
3. Verify /api/v1/health and login failure-path smoke checks.

### Database rollback

1. Restore from the latest managed backup snapshot if data integrity is at risk.
2. If rollback needs schema reversal, apply controlled Alembic downgrade only after backup confirmation.
3. Re-run backend health and core API smoke checks.

## 7) Incident triage checklist

1. Freeze new deployments.
2. Identify failing layer: frontend, backend, database, or network.
3. Capture error details and timestamps from platform logs.
4. Execute rollback if customer-facing impact is high.
5. Record root cause and remediation tasks before re-release.
