# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-31T03:04:10.921569Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `5`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `17`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30597951375 conclusion=failure commit=e58ad205a463
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30597865913 conclusion=failure commit=e58ad205a463
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30597677188 conclusion=failure commit=28d44fa0c637
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=30597664449 conclusion=failure commit=18e43363ef25
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30597627729 conclusion=failure commit=18e43363ef25
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
| Dashboard Visible Proof Warmed | 30597951375 | failure | `e58ad205a463` | 2026-07-31T02:03:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30597951375 |
| System3 Backend Live Simulation Proof | 30597865913 | failure | `e58ad205a463` | 2026-07-31T02:01:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30597865913 |
| Dashboard Deploy Provenance Gate | 30597677188 | failure | `28d44fa0c637` | 2026-07-31T01:57:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30597677188 |
| System3 Workflow Failure Tracker | 30597664449 | failure | `18e43363ef25` | 2026-07-31T01:56:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30597664449 |
| Dashboard Visual Production Proof | 30597627729 | failure | `18e43363ef25` | 2026-07-31T01:56:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30597627729 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

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
