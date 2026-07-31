# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-31T10:54:24.306321Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `11`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30623632307 conclusion=failure commit=b05d74b28091
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30623925331 conclusion=failure commit=b05d74b28091
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30623277177 conclusion=failure commit=9819f3da45b3
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30623157471 conclusion=failure commit=9819f3da45b3
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30623413238 conclusion=failure commit=9819f3da45b3
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30619777203 conclusion=failure commit=18570f6be834
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30619570565 conclusion=failure commit=08ab848d5553
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30619556339 conclusion=failure commit=08ab848d5553
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30619339893 conclusion=failure commit=deed8c00dd0b
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30614859571 conclusion=failure commit=f5ec086cb5fc
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30604659882 conclusion=failure commit=4474010bb446
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
| System3 Full Auto Truth | 30623632307 | failure | `b05d74b28091` | 2026-07-31T10:52:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30623632307 |
| System3 Broker Chain Semantic Gate | 30623925331 | failure | `b05d74b28091` | 2026-07-31T10:33:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30623925331 |
| System3 Latest Truth Publish | 30623277177 | failure | `9819f3da45b3` | 2026-07-31T10:31:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30623277177 |
| Permanent Repo Render Safety | 30623157471 | failure | `9819f3da45b3` | 2026-07-31T10:29:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30623157471 |
| Dashboard Live UI Proof | 30623413238 | failure | `9819f3da45b3` | 2026-07-31T10:24:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30623413238 |
| Dashboard Visible Proof Warmed | 30619777203 | failure | `18570f6be834` | 2026-07-31T09:24:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30619777203 |
| Dashboard Deploy Provenance Gate | 30619570565 | failure | `08ab848d5553` | 2026-07-31T09:20:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30619570565 |
| System3 Backend Live Simulation Proof | 30619556339 | failure | `08ab848d5553` | 2026-07-31T09:20:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30619556339 |
| Dashboard Visual Production Proof | 30619339893 | failure | `deed8c00dd0b` | 2026-07-31T09:17:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30619339893 |
| System3 Market Session Proof Runner | 30614859571 | failure | `f5ec086cb5fc` | 2026-07-31T08:05:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30614859571 |
| System3 Windows Self-Hosted Workflow Migration | 30604659882 | failure | `4474010bb446` | 2026-07-31T04:40:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30604659882 |

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
