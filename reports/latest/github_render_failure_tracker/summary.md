# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T23:33:49.581096Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `2`
GitHub workflows currently queued/in progress: `15`
Render failed endpoints: `12`
TODO count: `14`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30862676858 conclusion=failure commit=32f201c606a7
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30859290269 conclusion=failure commit=c049242a92f7
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
| .github/workflows/options-ml-training-proof.yml | 30862676858 | failure | `32f201c606a7` | 2026-08-03T23:33:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30862676858 |
| Dashboard Deploy Provenance Gate | 30859290269 | failure | `c049242a92f7` | 2026-08-03T22:37:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30859290269 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Proof Warmed | 30862677442 | in_progress | 2026-08-03T23:33:48Z |
| Dashboard Visible Proof Isolated | 30862677483 | in_progress | 2026-08-03T23:33:46Z |
| Genesis System3 Global Safety CI | 30862677494 | in_progress | 2026-08-03T23:33:45Z |
| Cloud Runtime Check | 30862677440 | in_progress | 2026-08-03T23:33:45Z |
| Permanent Repo Render Safety | 30862677521 | in_progress | 2026-08-03T23:33:44Z |
| System3 Backend Live Simulation Proof | 30862677497 | in_progress | 2026-08-03T23:33:44Z |
| System3 Latest Truth Publish | 30862677488 | in_progress | 2026-08-03T23:33:44Z |
| Dashboard Visual Contract Check | 30862677478 | in_progress | 2026-08-03T23:33:44Z |
| System3 Render Worker Preflight | 30862677490 | in_progress | 2026-08-03T23:33:43Z |
| System3 Workflow Failure Tracker | 30862677472 | in_progress | 2026-08-03T23:33:43Z |
| System3 Render Worker Issue Proof | 30862677460 | in_progress | 2026-08-03T23:33:43Z |
| System3 Render Worker Env Audit | 30862677486 | queued | 2026-08-03T23:33:41Z |
| System3 Parallel Root-Cause Audit | 30862677482 | queued | 2026-08-03T23:33:41Z |
| Dashboard Live UI Proof | 30862677452 | queued | 2026-08-03T23:33:41Z |
| Dashboard Visual Production Proof | 30862677433 | queued | 2026-08-03T23:33:41Z |

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
