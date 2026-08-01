# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-01T18:20:28.108135Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `4`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `16`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30710849216 conclusion=failure commit=7f550d9f8322
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30710793183 conclusion=failure commit=7f550d9f8322
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30710696282 conclusion=failure commit=0e048894f0d3
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30710664921 conclusion=failure commit=0e048894f0d3
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
| Dashboard Visible Proof Warmed | 30710849216 | failure | `7f550d9f8322` | 2026-08-01T17:41:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30710849216 |
| System3 Backend Live Simulation Proof | 30710793183 | failure | `7f550d9f8322` | 2026-08-01T17:39:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30710793183 |
| Dashboard Deploy Provenance Gate | 30710696282 | failure | `0e048894f0d3` | 2026-08-01T17:37:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30710696282 |
| Dashboard Visual Production Proof | 30710664921 | failure | `0e048894f0d3` | 2026-08-01T17:36:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30710664921 |

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
