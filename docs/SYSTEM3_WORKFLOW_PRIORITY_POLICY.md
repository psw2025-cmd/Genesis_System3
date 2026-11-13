# System3 Workflow Priority Policy

## Permanent standing rule

Only the following twelve GitHub Actions workflows are allowed in `.github/workflows`.

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
12. `cloud-verify.yml` — GitHub-hosted, read-only WIF Cloud Run environment inspection, Dhan GET orders, and clearly labeled synthetic PAPER replay evidence, plus **the sole narrowly scoped exception**: commit-addressed audit-results publication to Google Cloud Storage with no-clobber and SHA-256 readback; no deploy or broker POST.

### Retired workflows (GCP Exit Complete)

All previously retired Google Cloud Platform deployment and mutation workflows (`cloud-run-auto-deploy.yml`, `gcp-authority-repair.yml`, `gcp-live-ui-semantic-proof.yml`, `gcp-stage2-ci.yml`, `gcp-dhan-token-fix-ci.yml`, `full-cloud-audit.yml`, `gcp-dhan-token-rotation.yml`) remain retired under RUHI_RULE_V2.3. The new `cloud-verify.yml` is a narrowly scoped, read-only verification exception requested by the owner; it has no deploy or infrastructure mutation steps other than an explicitly permitted append-only audit-object creation step in the approved reports bucket.

## Event workflow rules

`workflow-priority-guard.yml` may use `workflow_run` and `deployment_status` only as an evidence-only observer. It may observe only the approved workflow names listed in its event allow-list.

## Scheduling authority

GitHub Actions `schedule:` remains prohibited. Runtime recurrence belongs to the local laptop Windows Service.

## Operating rules

- Run the smallest required priority workflow first.
- Never start duplicate or overlapping workflow runs.
- Use GitHub-hosted cloud runners only.
- The owner requests GitHub-hosted cloud-only verification; the offline laptop is not required for `cloud-verify.yml`. This does not authorize a production deployment.
- Google Cloud deployment and general infrastructure mutation and Render remain prohibited by this workflow policy. `cloud-verify.yml` may also write only versioned, no-clobber `genesis-audits/<merge-sha>/` evidence objects in the dedicated reports bucket, with hash readback. This is evidence publication, never Cloud Run deployment or broker mutation.
- `LIVE_TRADING_ENABLED=0`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- `AUTO_EXECUTE_TRADES=0`.
- Analyzer/paper mode remains authoritative until separate production-readiness proof is approved.
