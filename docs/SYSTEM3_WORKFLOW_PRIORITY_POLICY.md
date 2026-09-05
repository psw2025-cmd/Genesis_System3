# System3 Workflow Priority Policy

## Permanent standing rule

Only the following eleven GitHub Actions workflows are allowed in `.github/workflows`.

### Priority automatic workflows

1. `ci.yml` — blocking analyzer/paper safety validation for pull requests and protected branches.
2. `workflow-priority-guard.yml` — enforces this allow-list and is the approved read-only forensic observer for `workflow_run` and `deployment_status` events.
3. `frontend-runtime-smoke.yml` — focused browser runtime proof for the built dashboard.
4. `codeql-security.yml` — GitHub Advanced Security CodeQL analysis for Python and JavaScript/TypeScript on PR/main changes.
5. `security-audit.yml` — deterministic npm, pip-audit and Bandit evidence with fail-closed findings.
6. `sonarqube-audit.yml` — SonarQube/SonarQube Cloud readiness and scan adapter; missing external configuration is explicit, never fake PASS.
7. `system3-preflight-control-plane.yml` — canonical read-only workflow/issue/artifact current-state snapshot on every `main` push plus manual dispatch.
8. `repo-clean-forensic-toolkit.yml` — report-only repository/storage cleanup evidence.
9. `command-center-access.yml` — validates `ACCESS_POLICY.yaml`, runs Command Center smoke, appends audit log.
10. `live-proof-center.yml` — read-only public dashboard/API forensic MRI for multi-agent access.
11. `system3-runbook-audit.yml` — persistent autonomous runbook validation.

### Retired workflows (GCP Exit Complete)

All Google Cloud Platform workflows (`cloud-run-auto-deploy.yml`, `gcp-authority-repair.yml`, `gcp-live-ui-semantic-proof.yml`, `gcp-stage2-ci.yml`, `gcp-dhan-token-fix-ci.yml`, `full-cloud-audit.yml`, `gcp-dhan-token-rotation.yml`) are permanently retired under RUHI_RULE_V2.3.

## Event workflow rules

`workflow-priority-guard.yml` may use `workflow_run` and `deployment_status` only as an evidence-only observer. It may observe only the approved workflow names listed in its event allow-list.

## Scheduling authority

GitHub Actions `schedule:` remains prohibited. Runtime recurrence belongs to the local laptop Windows Service.

## Operating rules

- Run the smallest required priority workflow first.
- Never start duplicate or overlapping workflow runs.
- Use GitHub-hosted cloud runners only.
- Local Self-Hosted Laptop is the sole runtime/deployment authority (`http://127.0.0.1:8000`).
- Google Cloud Platform and Render remain retired and prohibited.
- `LIVE_TRADING_ENABLED=0`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- `AUTO_EXECUTE_TRADES=0`.
- Analyzer/paper mode remains authoritative until separate production-readiness proof is approved.
