# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-29T07:55:43.047690Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30432291205 conclusion=failure commit=8268c18b8b55
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30430264048 conclusion=failure commit=705dfc2b1f90
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30431087391 conclusion=failure commit=c427dcdb223a
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30431004435 conclusion=failure commit=c427dcdb223a
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30430792027 conclusion=failure commit=705dfc2b1f90
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30430727483 conclusion=failure commit=705dfc2b1f90
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30429941372 conclusion=failure commit=705dfc2b1f90
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30424847319 conclusion=failure commit=30681c9fb89e
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30422641994 conclusion=failure commit=21176045c695
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
| System3 Broker Chain Semantic Gate | 30432291205 | failure | `8268c18b8b55` | 2026-07-29T07:37:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30432291205 |
| System3 Full Auto Truth | 30430264048 | failure | `705dfc2b1f90` | 2026-07-29T07:28:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30430264048 |
| Dashboard Visible Proof Warmed | 30431087391 | failure | `c427dcdb223a` | 2026-07-29T07:17:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30431087391 |
| System3 Backend Live Simulation Proof | 30431004435 | failure | `c427dcdb223a` | 2026-07-29T07:16:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30431004435 |
| Dashboard Deploy Provenance Gate | 30430792027 | failure | `705dfc2b1f90` | 2026-07-29T07:12:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30430792027 |
| Dashboard Visual Production Proof | 30430727483 | failure | `705dfc2b1f90` | 2026-07-29T07:12:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30430727483 |
| Dashboard Live UI Proof | 30429941372 | failure | `705dfc2b1f90` | 2026-07-29T06:58:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30429941372 |
| System3 Market Session Proof Runner | 30424847319 | failure | `30681c9fb89e` | 2026-07-29T05:25:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30424847319 |
| System3 Windows Self-Hosted Workflow Migration | 30422641994 | failure | `21176045c695` | 2026-07-29T04:35:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30422641994 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30433366458 | in_progress | 2026-07-29T07:54:09Z |
| Permanent Repo Render Safety | 30433282111 | in_progress | 2026-07-29T07:52:43Z |

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
