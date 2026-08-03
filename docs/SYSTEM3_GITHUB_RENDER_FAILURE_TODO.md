# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T23:35:26.176003Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `9`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30862677433 conclusion=failure commit=32f201c606a7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30862677442 conclusion=failure commit=32f201c606a7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=30862677483 conclusion=failure commit=32f201c606a7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Contract Check' run=30862677478 conclusion=failure commit=32f201c606a7
- [ ] Fix latest GitHub workflow 'System3 Render Worker Issue Proof' run=30862677460 conclusion=failure commit=32f201c606a7
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
| Dashboard Visual Production Proof | 30862677433 | failure | `32f201c606a7` | 2026-08-03T23:34:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30862677433 |
| Dashboard Visible Proof Warmed | 30862677442 | failure | `32f201c606a7` | 2026-08-03T23:34:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30862677442 |
| Dashboard Visible Proof Isolated | 30862677483 | failure | `32f201c606a7` | 2026-08-03T23:34:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30862677483 |
| Dashboard Visual Contract Check | 30862677478 | failure | `32f201c606a7` | 2026-08-03T23:34:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30862677478 |
| System3 Render Worker Issue Proof | 30862677460 | failure | `32f201c606a7` | 2026-08-03T23:33:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30862677460 |
| .github/workflows/options-ml-training-proof.yml | 30862676858 | failure | `32f201c606a7` | 2026-08-03T23:33:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30862676858 |
| Dashboard Deploy Provenance Gate | 30859290269 | failure | `c049242a92f7` | 2026-08-03T22:37:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30859290269 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Genesis System3 Global Safety CI | 30862753181 | in_progress | 2026-08-03T23:35:20Z |
| Dashboard Live UI Proof | 30862762886 | in_progress | 2026-08-03T23:35:19Z |
| Actions Truth Autopsy | 30862772675 | queued | 2026-08-03T23:35:18Z |
| System3 1000 Point TODO Status Updater | 30862763290 | in_progress | 2026-08-03T23:35:15Z |
| System3 Backend Live Simulation Proof | 30862760278 | in_progress | 2026-08-03T23:35:09Z |
| System3 Workflow Failure Tracker | 30862757059 | in_progress | 2026-08-03T23:35:07Z |
| Cloud Runtime Check | 30862677440 | in_progress | 2026-08-03T23:33:45Z |
| Permanent Repo Render Safety | 30862677521 | in_progress | 2026-08-03T23:33:44Z |
| System3 Latest Truth Publish | 30862677488 | in_progress | 2026-08-03T23:33:44Z |

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
