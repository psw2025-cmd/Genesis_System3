# System3 Workflow Priority Policy

## Permanent standing rule

Only the following seven GitHub Actions workflows are allowed in `.github/workflows`.

### Priority automatic workflows

1. `ci.yml` — blocking analyzer/paper safety validation for pull requests and protected branches.
2. `workflow-priority-guard.yml` — enforces this allow-list and is the only approved read-only observer for `workflow_run` and `deployment_status` events.
3. `cloud-run-auto-deploy.yml` — path-scoped Google Cloud Run deployment from `main`.
4. `gcp-stage2-ci.yml` — focused Google Cloud safety tests for relevant pull-request changes.
5. `gcp-dhan-token-fix-ci.yml` — focused Dhan token/runtime contract checks for relevant pull-request changes.
6. `frontend-runtime-smoke.yml` — focused browser runtime proof for the built dashboard.

### Manual emergency workflow

7. `gcp-dhan-token-rotation.yml` — manual recovery/proof only. Daily rotation remains owned by Google Cloud Scheduler.

## Event observer rule

Only `workflow-priority-guard.yml` may use `workflow_run` or `deployment_status`.
It may observe only the six existing System3 workflows named in its event allow-list.
The observer is evidence-only: GitHub-hosted runner, read permissions, trusted `main` checkout, credential persistence disabled, no repository or deployment mutation, and no trading/order action.
It writes event metadata and a recurrence fingerprint only to the workflow summary and retained artifact.

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
