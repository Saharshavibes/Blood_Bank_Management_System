# Deployment Governance Matrix Evidence Appendix

## Scope
- Workflow: CD Deploy Hooks
- Branch under test: chore/deploy-lock-matrix-evidence
- Commit under test: bf2eb4922bd11e3634288833ecbd4caa2d9e383b
- Execution window: 2026-04-20

## Run Evidence

| Case | Environment | Run | Conclusion | Failed Step | Key Failed Evidence | Render Hook Step | Vercel Hook Step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| case1_missing_render_staging | staging | [24656601183](https://github.com/Saharshavibes/Blood_Bank_Management_System/actions/runs/24656601183) | failure | Resolve environment secrets | RENDER_DEPLOY_HOOK_URL_STAGING is required for staging deployments; VERCEL_DEPLOY_HOOK_URL_STAGING is required for staging deployments | skipped | skipped |
| case2_missing_vercel_staging | staging | [24656603392](https://github.com/Saharshavibes/Blood_Bank_Management_System/actions/runs/24656603392) | failure | Resolve environment secrets | RENDER_DEPLOY_HOOK_URL_STAGING is required for staging deployments; VERCEL_DEPLOY_HOOK_URL_STAGING is required for staging deployments | skipped | skipped |
| case3_missing_endpoints_staging | staging | [24656605233](https://github.com/Saharshavibes/Blood_Bank_Management_System/actions/runs/24656605233) | failure | Resolve environment secrets | BACKEND_HEALTH_URL_STAGING is required for staging deployments; BACKEND_AUTH_LOGIN_URL_STAGING is required for staging deployments; FRONTEND_URL_STAGING is required for staging deployments | skipped | skipped |
| case4_missing_multiple_staging | staging | [24656607152](https://github.com/Saharshavibes/Blood_Bank_Management_System/actions/runs/24656607152) | failure | Resolve environment secrets | RENDER_DEPLOY_HOOK_URL_STAGING is required for staging deployments; VERCEL_DEPLOY_HOOK_URL_STAGING is required for staging deployments; BACKEND_HEALTH_URL_STAGING is required for staging deployments | skipped | skipped |
| case5_missing_render_production | production | [24656609530](https://github.com/Saharshavibes/Blood_Bank_Management_System/actions/runs/24656609530) | failure | Resolve environment secrets | RENDER_DEPLOY_HOOK_URL_PRODUCTION is required for production deployments | skipped | skipped |
| case6_staging_matches_production | staging | [24656611144](https://github.com/Saharshavibes/Blood_Bank_Management_System/actions/runs/24656611144) | failure | Verify staging hook isolation | Staging deploy hooks were not resolved from staging secrets | skipped | skipped |

## Verification Outcome
- Every scenario failed before any deploy hook invocation.
- Trigger Render deploy hook and Trigger Vercel deploy hook were skipped in all six runs.
- Governance lock behavior is validated for missing-secret fail-fast and staging hook isolation checks.

## Notes
- case1_missing_render_staging and case2_missing_vercel_staging both surfaced missing hook secret errors in this repository state, which confirms strict fail-fast enforcement under incomplete staging hook configuration.
