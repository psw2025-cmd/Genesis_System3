# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-28T10:50:41.631800Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30350494050 conclusion=failure commit=65d96ec930d4
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30351155034 conclusion=failure commit=65d96ec930d4
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30350112599 conclusion=failure commit=34ed26faecc0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30349914009 conclusion=failure commit=34ed26faecc0
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30349924422 conclusion=failure commit=34ed26faecc0
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30349679482 conclusion=failure commit=d47bd2d3e66f
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30349655071 conclusion=failure commit=d47bd2d3e66f
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30348832285 conclusion=failure commit=d47bd2d3e66f
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30340234238 conclusion=failure commit=584d0d1f6f52
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
| System3 Full Auto Truth | 30350494050 | failure | `65d96ec930d4` | 2026-07-28T10:47:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30350494050 |
| System3 Broker Chain Semantic Gate | 30351155034 | failure | `65d96ec930d4` | 2026-07-28T10:32:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30351155034 |
| Permanent Repo Render Safety | 30350112599 | failure | `34ed26faecc0` | 2026-07-28T10:26:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30350112599 |
| Dashboard Visible Proof Warmed | 30349914009 | failure | `34ed26faecc0` | 2026-07-28T10:14:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30349914009 |
| System3 Backend Live Simulation Proof | 30349924422 | failure | `34ed26faecc0` | 2026-07-28T10:14:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30349924422 |
| Dashboard Visual Production Proof | 30349679482 | failure | `d47bd2d3e66f` | 2026-07-28T10:11:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30349679482 |
| Dashboard Deploy Provenance Gate | 30349655071 | failure | `d47bd2d3e66f` | 2026-07-28T10:10:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30349655071 |
| Dashboard Live UI Proof | 30348832285 | failure | `d47bd2d3e66f` | 2026-07-28T09:58:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30348832285 |
| System3 Market Session Proof Runner | 30340234238 | failure | `584d0d1f6f52` | 2026-07-28T07:58:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30340234238 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30352260724 | in_progress | 2026-07-28T10:49:00Z |

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
