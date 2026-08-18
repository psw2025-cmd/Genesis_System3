# System3 Workflow Priority Policy

## Permanent standing rule

Only the following fourteen GitHub Actions workflows are allowed in `.github/workflows`.

### Priority automatic workflows

1. `ci.yml` — blocking analyzer/paper safety validation for pull requests and protected branches.
2. `workflow-priority-guard.yml` — enforces this allow-list and is the approved read-only forensic observer for `workflow_run` and `deployment_status` events. After each approved production-relevant workflow completion it also refreshes the canonical preflight workflow/issue/artifact snapshot from trusted `main`; it does not create a second control-plane authority.
3. `cloud-run-auto-deploy.yml` — path-scoped Google Cloud Run deployment from `main`; also reusable only by the approved IAM repair workflow.
4. `gcp-authority-repair.yml` — bounded IAM-drift repair after a failed `Cloud Run Auto Deploy` on `main`; primary/fallback keyless repair identities, declared-baseline convergence only, no GitHub write token, no Dhan job execution, and one reusable deploy only when actual IAM drift changed.
5. `gcp-stage2-ci.yml` — focused Google Cloud safety tests for relevant pull-request changes.
6. `gcp-dhan-token-fix-ci.yml` — focused Dhan token/runtime contract checks for relevant pull-request changes.
7. `frontend-runtime-smoke.yml` — focused browser runtime proof for the built dashboard.
8. `codeql-security.yml` — GitHub Advanced Security CodeQL analysis for Python and JavaScript/TypeScript on PR/main changes.
9. `security-audit.yml` — deterministic npm, pip-audit and Bandit evidence with fail-closed findings.
10. `sonarqube-audit.yml` — SonarQube/SonarQube Cloud readiness and scan adapter; missing external configuration is explicit, never fake PASS.
11. `full-cloud-audit.yml` — read-only exact-SHA Google Cloud runtime/log/TLS/latency/IAM/Scheduler audit plus exact security-artifact binding and external OpenAI/Claude consensus. It cannot mutate deployment, infrastructure, broker state or orders.
12. `system3-preflight-control-plane.yml` — canonical read-only workflow/issue/artifact current-state snapshot on every `main` push plus manual dispatch. The same snapshot code is reused by Workflow Priority Guard after approved workflow completions. Snapshot artifacts are retained for 30 days. It has no GitHub Actions schedule trigger and does not replace mandatory agent-side fresh preflight before production transitions.
13. `repo-clean-forensic-toolkit.yml` — report-only repository/storage cleanup evidence. It scans every current tracked file on relevant PR/main changes or manual dispatch, inventories duplicate/reference/import evidence and Actions storage metadata, and performs full Git-history blob analysis on non-PR runs. It never deletes files/artifacts, rewrites history, or touches broker/trading/IAM state.

### Manual emergency workflow

14. `gcp-dhan-token-rotation.yml` — manual recovery/proof only. Daily rotation remains owned by Google Cloud Scheduler.

## Event workflow rules

`workflow-priority-guard.yml` may use `workflow_run` and `deployment_status` only as an evidence-only observer. It may observe only the approved workflow names listed in its event allow-list. It uses a GitHub-hosted runner, read permissions, trusted `main` checkout, credential persistence disabled, and performs no repository/deployment/trading mutation. For every observed workflow completion it refreshes `scripts/system3_preflight_control_plane.py` from trusted `main` and uploads the resulting canonical snapshot; failure events additionally retain their immutable event-forensic artifact.

`gcp-authority-repair.yml` is the sole additional workflow allowed to use `workflow_run`. Its source must be exactly `Cloud Run Auto Deploy`; automatic repair is restricted to failed runs whose `head_branch` is `main`. It may also support `workflow_dispatch` for bounded recovery. It must not use `deployment_status`, `push`, `pull_request`, GitHub `actions: write`/`contents: write`, Dhan/Cloud Run job execution, or arbitrary IAM mutation code outside the repository-declared baseline reconciler. Its only deployment continuation is one reusable invocation of `cloud-run-auto-deploy.yml` when the reconciler reports actual IAM changes.

No other workflow may use `workflow_run` or `deployment_status`.

## Scheduling authority

GitHub Actions `schedule:` remains prohibited. Runtime recurrence belongs to Google Cloud Scheduler. Code/security/cloud audits execute on every relevant `main` commit; code/security checks also execute on pull requests where configured and may be dispatched manually. Dependabot uses its own repository-native update schedule and is not a GitHub Actions workflow scheduler.

The canonical preflight workflow itself runs on `main` push and manual dispatch only. Event-driven refresh is performed inside the already-approved Workflow Priority Guard after relevant workflow completions, so no duplicate scheduled or event control-plane workflow is introduced. Fresh preflight before a production transition remains an agent operating-contract obligation.

The repo-clean forensic toolkit likewise has no GitHub cron. Its persistent discoverability is governed by `AGENTS.md`; agents run it on demand for cleanup/storage work, while its own relevant PR/main changes prove the scanner itself.

## AI and external observability rule

- External AI review is advisory-plus-consensus only; it can never override deterministic safety/runtime/security failure evidence.
- Missing OpenAI, Anthropic, Sonar, Elasticsearch, Jaeger, Grafana or PowerBI configuration is a typed BLOCKED state, never PASS.
- GCP Cloud Logging/Monitoring is the default runtime evidence authority until external adapters are explicitly configured and proven.
- Secret payloads and broker credentials must not be copied into AI prompts, GitHub artifacts, logs, dashboards or external observability stores.

## Disabled workflow classes

All additional workflow files are prohibited, including Render workflows, self-hosted workflows, scheduled proof writers, legacy failure trackers, duplicate proof workflows, unapproved repair runners, experimental swarms, and unapproved ML workflows.

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
