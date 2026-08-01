# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-01T13:30:52.354390Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30700134310 conclusion=failure commit=8605fdf41cb3
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30700097486 conclusion=failure commit=8605fdf41cb3
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30700034186 conclusion=failure commit=0c1fe21dd813
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30700023234 conclusion=failure commit=0c1fe21dd813
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30699996413 conclusion=failure commit=0c1fe21dd813
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
| Dashboard Visible Proof Warmed | 30700134310 | failure | `8605fdf41cb3` | 2026-08-01T12:40:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30700134310 |
| System3 Backend Live Simulation Proof | 30700097486 | failure | `8605fdf41cb3` | 2026-08-01T12:38:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30700097486 |
| System3 Render Worker Preflight | 30700034186 | failure | `0c1fe21dd813` | 2026-08-01T12:36:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30700034186 |
| Dashboard Deploy Provenance Gate | 30700023234 | failure | `0c1fe21dd813` | 2026-08-01T12:36:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30700023234 |
| Dashboard Visual Production Proof | 30699996413 | failure | `0c1fe21dd813` | 2026-08-01T12:36:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30699996413 |

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
