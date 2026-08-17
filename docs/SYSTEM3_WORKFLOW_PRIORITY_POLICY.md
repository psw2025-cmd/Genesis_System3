# System3 Workflow Priority Policy

## Permanent standing rule

Only the following thirteen GitHub Actions workflows are allowed in `.github/workflows`.

### Priority automatic workflows

1. `ci.yml` — blocking analyzer/paper safety validation for pull requests and protected branches.
2. `workflow-priority-guard.yml` — enforces this allow-list and is the approved read-only forensic observer for `workflow_run` and `deployment_status` events.
3. `cloud-run-auto-deploy.yml` — path-scoped Google Cloud Run deployment from `main`; also reusable only by the approved IAM repair workflow.
4. `gcp-authority-repair.yml` — bounded IAM-drift repair after a failed `Cloud Run Auto Deploy` on `main`; primary/fallback keyless repair identities, declared-baseline convergence only, no GitHub write token, no Dhan job execution, and one reusable deploy only when actual IAM drift changed.
5. `gcp-stage2-ci.yml` — focused Google Cloud safety tests for relevant pull-request changes.
6. `gcp-dhan-token-fix-ci.yml` — focused Dhan token/runtime contract checks for relevant pull-request changes.
7. `frontend-runtime-smoke.yml` — focused browser runtime proof for the built dashboard.
8. `codeql-security.yml` — GitHub Advanced Security CodeQL analysis for Python and JavaScript/TypeScript on PR/main changes.
9. `security-audit.yml` — deterministic npm, pip-audit and Bandit evidence with fail-closed findings.
10. `sonarqube-audit.yml` — SonarQube/SonarQube Cloud readiness and scan adapter; missing external configuration is explicit, never fake PASS.
11. `full-cloud-audit.yml` — read-only exact-SHA Google Cloud runtime/log/TLS/latency/IAM/Scheduler audit plus exact security-artifact binding and external OpenAI/Claude consensus. It cannot mutate deployment, infrastructure, broker state or orders.
12. `system3-preflight-control-plane.yml` — read-only workflow/issue/artifact current-state snapshot on every `main` push plus manual dispatch. It has no schedule trigger and does not replace mandatory agent-side preflight before production transitions.

### Manual emergency workflow

13. `gcp-dhan-token-rotation.yml` — manual recovery/proof only. Daily rotation remains owned by Google Cloud Scheduler.

## Event workflow rules

`workflow-priority-guard.yml` may use `workflow_run` and `deployment_status` only as an evidence-only observer. It may observe only the approved workflow names listed in its event allow-list. It uses a GitHub-hosted runner, read permissions, trusted `main` checkout, credential persistence disabled, and performs no repository/deployment/trading mutation.

`gcp-authority-repair.yml` is the sole additional workflow allowed to use `workflow_run`. Its source must be exactly `Cloud Run Auto Deploy`; automatic repair is restricted to failed runs whose `head_branch` is `main`. It may also support `workflow_dispatch` for bounded recovery. It must not use `deployment_status`, `push`, `pull_request`, GitHub `actions: write`/`contents: write`, Dhan/Cloud Run job execution, or arbitrary IAM mutation code outside the repository-declared baseline reconciler. Its only deployment continuation is one reusable invocation of `cloud-run-auto-deploy.yml` when the reconciler reports actual IAM changes.

No other workflow may use `workflow_run` or `deployment_status`.

## Scheduling authority

GitHub Actions `schedule:` remains prohibited. Runtime recurrence belongs to Google Cloud Scheduler. Code/security/cloud audits execute on every relevant `main` commit; code/security checks also execute on pull requests where configured and may be dispatched manually. Dependabot uses its own repository-native update schedule and is not a GitHub Actions workflow scheduler.

The preflight control plane follows this rule: its GitHub workflow runs on `main` push and manual dispatch only. Fresh preflight before a production transition is an agent operating-contract obligation, not a GitHub cron.

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
