# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-24T03:32:16.077284Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `4`
GitHub workflows currently queued/in progress: `27`
Render failed endpoints: `12`
TODO count: `16`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30064456692 conclusion=failure commit=f5e5a2e3cbce
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30064406048 conclusion=failure commit=60dfc9321f73
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30064405997 conclusion=failure commit=60dfc9321f73
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30064300969 conclusion=failure commit=ee1b9eed7405
- [ ] Fix Render endpoint /: HTTP status 0 status=0
- [ ] Fix Render endpoint /ui/: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/health: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/paper: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| .github/workflows/options-ml-training-proof.yml | 30064456692 | failure | `f5e5a2e3cbce` | 2026-07-24T03:31:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30064456692 |
| Dashboard Visual Loading Postflight | 30064406048 | failure | `60dfc9321f73` | 2026-07-24T03:30:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30064406048 |
| Dashboard Visual Proof Strict Gate | 30064405997 | failure | `60dfc9321f73` | 2026-07-24T03:30:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30064405997 |
| System3 Backend Live Simulation Proof | 30064300969 | failure | `ee1b9eed7405` | 2026-07-24T03:28:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30064300969 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Actions Truth Autopsy | 30064471496 | queued | 2026-07-24T03:32:15Z |
| System3 Latest Truth Publish | 30064457233 | in_progress | 2026-07-24T03:32:15Z |
| Cloud Runtime Check | 30064457178 | queued | 2026-07-24T03:32:13Z |
| Render Deploy Commit Proof | 30064457165 | in_progress | 2026-07-24T03:32:10Z |
| System3 Render Worker Issue Proof | 30064457188 | in_progress | 2026-07-24T03:32:09Z |
| Dashboard Visible Proof Isolated | 30064457154 | in_progress | 2026-07-24T03:32:09Z |
| System3 Parallel Root-Cause Audit | 30064457205 | queued | 2026-07-24T03:32:08Z |
| System3 Render Worker Preflight | 30064457246 | in_progress | 2026-07-24T03:32:07Z |
| System3 Broker Chain Semantic Gate | 30064457181 | in_progress | 2026-07-24T03:32:07Z |
| Dashboard Deploy Provenance Gate | 30064457171 | in_progress | 2026-07-24T03:32:07Z |
| Dashboard Visible Settle Proof | 30064457161 | in_progress | 2026-07-24T03:32:06Z |
| System3 Windows Self-Hosted Full Proof | 30064457176 | in_progress | 2026-07-24T03:32:00Z |
| System3 Secure Install Credential Audit | 30064457159 | in_progress | 2026-07-24T03:31:59Z |
| Dashboard Live UI Proof | 30064457153 | in_progress | 2026-07-24T03:31:59Z |
| Dashboard Visible Proof Warmed | 30064457128 | in_progress | 2026-07-24T03:31:59Z |
| Permanent Repo Render Safety | 30064457220 | in_progress | 2026-07-24T03:31:58Z |
| System3 Autopilot Proof Board | 30064457150 | in_progress | 2026-07-24T03:31:58Z |
| System3 Safe Repair Runner | 30064457212 | pending | 2026-07-24T03:31:56Z |
| Dashboard Visual Production Proof | 30064457206 | pending | 2026-07-24T03:31:56Z |
| Dashboard Visible Issue Tracker | 30064457170 | pending | 2026-07-24T03:31:56Z |
| Dashboard Visible Auth-Resilient Proof | 30064457149 | pending | 2026-07-24T03:31:56Z |
| System3 Render Worker Env Audit | 30064457232 | queued | 2026-07-24T03:31:55Z |
| System3 Experimental Solution Planner | 30064457174 | queued | 2026-07-24T03:31:55Z |
| Genesis System3 Global Safety CI | 30064457172 | queued | 2026-07-24T03:31:55Z |
| Dashboard Visible Proof Current | 30064457157 | queued | 2026-07-24T03:31:55Z |
| Dashboard Visual Contract Check | 30064457155 | queued | 2026-07-24T03:31:55Z |
| Dashboard Shell Diagnostic | 30064406052 | in_progress | 2026-07-24T03:30:59Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 0 | HTTP status 0 | `none` |
| `/ui/` | 0 | HTTP status 0 | `none` |
| `/api/health` | 0 | HTTP status 0 | `none` |
| `/api/state` | 0 | HTTP status 0 | `none` |
| `/api/deploy/info` | 0 | HTTP status 0 | `none` |
| `/api/broker/diagnose` | 0 | HTTP status 0 | `none` |
| `/api/broker/funds` | 0 | HTTP status 0 | `none` |
| `/api/broker/holdings` | 0 | HTTP status 0 | `none` |
| `/api/broker/positions/live` | 0 | HTTP status 0 | `none` |
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
| `/api/paper` | 0 | HTTP status 0 | `none` |
| `/api/ml/performance` | 0 | HTTP status 0 | `none` |
