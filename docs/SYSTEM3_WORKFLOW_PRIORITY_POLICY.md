# System3 Workflow Priority Policy

## Permanent standing rule

Only the following GitHub Actions workflows are allowed in `.github/workflows`.

### Priority automatic workflows

1. `ci.yml` — blocking analyzer/paper safety validation for pull requests and protected branches.
2. `workflow-priority-guard.yml` — enforces this allow-list whenever workflow policy changes.
3. `cloud-run-auto-deploy.yml` — path-scoped Google Cloud Run deployment from `main`.
4. `gcp-stage2-ci.yml` — focused Google Cloud safety tests for relevant pull-request changes.
5. `gcp-dhan-token-fix-ci.yml` — focused Dhan token/runtime contract checks for relevant pull-request changes.

### Manual emergency workflow

6. `gcp-dhan-token-rotation.yml` — manual recovery/proof only. Daily rotation remains owned by Google Cloud Scheduler.

## Disabled workflow classes

All other workflows are prohibited from the active workflow directory, including:

- Render-related workflows
- self-hosted or laptop-runner workflows
- scheduled proof and report writers
- workflow-failure trackers and TODO writers
- duplicate dashboard visual-proof workflows
- experimental planners, swarms, repair runners and normalizers
- ML training/proof workflows that are not explicitly promoted to priority

Git history preserves removed workflow files. Restoration requires a reviewed pull request that updates this policy and passes `workflow-priority-guard.yml`.

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
