# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-30T23:22:39.995479Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30588072051 conclusion=failure commit=a0c1385329d0
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30587992881 conclusion=failure commit=a0c1385329d0
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30587816299 conclusion=failure commit=792da6aa2a8a
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30587875938 conclusion=failure commit=792da6aa2a8a
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30587853895 conclusion=failure commit=792da6aa2a8a
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
| Dashboard Visible Proof Warmed | 30588072051 | failure | `a0c1385329d0` | 2026-07-30T22:43:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30588072051 |
| System3 Backend Live Simulation Proof | 30587992881 | failure | `a0c1385329d0` | 2026-07-30T22:43:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30587992881 |
| Dashboard Visual Production Proof | 30587816299 | failure | `792da6aa2a8a` | 2026-07-30T22:39:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30587816299 |
| System3 Render Worker Preflight | 30587875938 | failure | `792da6aa2a8a` | 2026-07-30T22:39:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30587875938 |
| Dashboard Deploy Provenance Gate | 30587853895 | failure | `792da6aa2a8a` | 2026-07-30T22:39:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30587853895 |

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
