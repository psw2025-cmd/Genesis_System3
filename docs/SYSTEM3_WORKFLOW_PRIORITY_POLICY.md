# System3 Workflow Priority Policy

## Permanent standing rule

Only the following eight GitHub Actions workflows are allowed in `.github/workflows`.

### Priority automatic workflows

1. `ci.yml` — blocking analyzer/paper safety validation for pull requests and protected branches.
2. `workflow-priority-guard.yml` — enforces this allow-list and remains the read-only forensic observer for deployment/workflow events.
3. `cloud-run-auto-deploy.yml` — path-scoped Google Cloud Run deployment from `main`.
4. `gcp-stage2-ci.yml` — focused Google Cloud safety tests for relevant pull-request changes.
5. `gcp-dhan-token-fix-ci.yml` — focused Dhan token/runtime contract checks for relevant pull-request changes.
6. `frontend-runtime-smoke.yml` — focused browser runtime proof for the built dashboard.
7. `gcp-market-data-ui-parity-proof.yml` — read-only post-deploy production-browser proof. It may run only after successful `Cloud Run Auto Deploy` on `main` or by explicit manual dispatch for an exact deployed SHA. It has no order, secret-mutation, repository-write, or deployment-mutation authority.

### Manual emergency workflow

8. `gcp-dhan-token-rotation.yml` — manual recovery/proof only. Daily rotation remains owned by Google Cloud Scheduler.

## Event observer rule

`workflow-priority-guard.yml` is the only forensic observer allowed to consume both `workflow_run` and `deployment_status`; it remains evidence-only.

`gcp-market-data-ui-parity-proof.yml` is the single narrowly approved exception for a `workflow_run` trigger. It may observe only successful `Cloud Run Auto Deploy` completion on `main`, then prove the exact serving SHA from the real production UI. It may not consume `deployment_status`, mutate GCP runtime, change secrets, write repository state, or call any trading/order endpoint.

The forensic observer may observe only the six existing System3 workflows named in its event allow-list. The observer is evidence-only: GitHub-hosted runner, read permissions, trusted `main` checkout, credential persistence disabled, no repository or deployment mutation, and no trading/order action. It writes event metadata and a recurrence fingerprint only to the workflow summary and retained artifact.

## Disabled workflow classes

All additional workflow files are prohibited, including Render workflows, self-hosted workflows, scheduled proof writers, legacy failure trackers, duplicate proof workflows, repair runners, experimental swarms, and unapproved ML workflows.

## Operating rules

- Run the smallest required priority workflow first.
- Never start duplicate or overlapping workflow runs.
- Use GitHub-hosted cloud runners only.
- Google Cloud is the sole runtime/deployment authority.
- Render remains retired and prohibited.
- `LIVE_TRADING_ENABLED=0`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- `AUTO_EXECUTE_TRADES=0`.
- Analyzer/paper mode remains authoritative until separate production-readiness proof is approved.
- Backend/API/CI truth is diagnostic only for market-data completeness; closure requires actual production UI proof from the serving GCP dashboard.
