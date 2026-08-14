# System3 Workflow Priority Policy

## Permanent standing rule

Only the following eleven GitHub Actions workflows are allowed in `.github/workflows`.

### Priority automatic workflows

1. `ci.yml` — blocking analyzer/paper safety validation for pull requests and protected branches.
2. `workflow-priority-guard.yml` — enforces this allow-list and is the only approved read-only observer for `workflow_run` and `deployment_status` events.
3. `cloud-run-auto-deploy.yml` — path-scoped Google Cloud Run deployment from `main`.
4. `gcp-stage2-ci.yml` — focused Google Cloud safety tests for relevant pull-request changes.
5. `gcp-dhan-token-fix-ci.yml` — focused Dhan token/runtime contract checks for relevant pull-request changes.
6. `frontend-runtime-smoke.yml` — focused browser runtime proof for the built dashboard.
7. `codeql-security.yml` — GitHub Advanced Security CodeQL analysis for Python and JavaScript/TypeScript on PR/main changes.
8. `security-audit.yml` — deterministic npm, pip-audit and Bandit evidence with fail-closed findings.
9. `sonarqube-audit.yml` — SonarQube/SonarQube Cloud readiness and scan adapter; missing external configuration is explicit, never fake PASS.
10. `full-cloud-audit.yml` — read-only exact-SHA Google Cloud runtime/log/TLS/latency/IAM/Scheduler audit plus exact security-artifact binding and external OpenAI/Claude consensus. It cannot mutate deployment, infrastructure, broker state or orders.

### Manual emergency workflow

11. `gcp-dhan-token-rotation.yml` — manual recovery/proof only. Daily rotation remains owned by Google Cloud Scheduler.

## Event observer rule

Only `workflow-priority-guard.yml` may use `workflow_run` or `deployment_status`.
It may observe only the ten approved workflow names listed in its event allow-list.
The observer is evidence-only: GitHub-hosted runner, read permissions, trusted `main` checkout, credential persistence disabled, no repository or deployment mutation, and no trading/order action.
It writes event metadata and a recurrence fingerprint only to the workflow summary and retained artifact.

## Scheduling authority

GitHub Actions `schedule:` remains prohibited. Runtime recurrence belongs to Google Cloud Scheduler. Code/security/cloud audits execute on every relevant `main` commit; code/security checks also execute on pull requests where configured and may be dispatched manually. Dependabot uses its own repository-native update schedule and is not a GitHub Actions workflow scheduler.

## AI and external observability rule

- External AI review is advisory-plus-consensus only; it can never override deterministic safety/runtime/security failure evidence.
- Missing OpenAI, Anthropic, Sonar, Elasticsearch, Jaeger, Grafana or PowerBI configuration is a typed BLOCKED state, never PASS.
- GCP Cloud Logging/Monitoring is the default runtime evidence authority until external adapters are explicitly configured and proven.
- Secret payloads and broker credentials must not be copied into AI prompts, GitHub artifacts, logs, dashboards or external observability stores.

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
