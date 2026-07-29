# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-29T21:19:21.700816Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30489195816 conclusion=failure commit=3e1580fe9a00
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30489102829 conclusion=failure commit=0dc37221cb4d
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30488929346 conclusion=failure commit=143e70198f6d
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30488962794 conclusion=failure commit=143e70198f6d
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
| Dashboard Visible Proof Warmed | 30489195816 | failure | `3e1580fe9a00` | 2026-07-29T20:38:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30489195816 |
| System3 Backend Live Simulation Proof | 30489102829 | failure | `0dc37221cb4d` | 2026-07-29T20:36:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30489102829 |
| Dashboard Visual Production Proof | 30488929346 | failure | `143e70198f6d` | 2026-07-29T20:34:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30488929346 |
| Dashboard Deploy Provenance Gate | 30488962794 | failure | `143e70198f6d` | 2026-07-29T20:34:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30488962794 |

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
