# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-29T09:59:09.329032Z`
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

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30439724201 conclusion=failure commit=ee27c1652e71
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30440128732 conclusion=failure commit=ee27c1652e71
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30439109196 conclusion=failure commit=a97766fd4b3c
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30439040418 conclusion=failure commit=a97766fd4b3c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30438805133 conclusion=failure commit=a20c0af5fe5a
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30438846012 conclusion=failure commit=a20c0af5fe5a
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30438187348 conclusion=failure commit=a20c0af5fe5a
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30433617761 conclusion=failure commit=506c561f061c
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
| System3 Full Auto Truth | 30439724201 | failure | `ee27c1652e71` | 2026-07-29T09:52:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30439724201 |
| System3 Broker Chain Semantic Gate | 30440128732 | failure | `ee27c1652e71` | 2026-07-29T09:34:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30440128732 |
| Dashboard Visible Proof Warmed | 30439109196 | failure | `a97766fd4b3c` | 2026-07-29T09:19:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30439109196 |
| System3 Backend Live Simulation Proof | 30439040418 | failure | `a97766fd4b3c` | 2026-07-29T09:18:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30439040418 |
| Dashboard Visual Production Proof | 30438805133 | failure | `a20c0af5fe5a` | 2026-07-29T09:15:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30438805133 |
| Dashboard Deploy Provenance Gate | 30438846012 | failure | `a20c0af5fe5a` | 2026-07-29T09:15:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30438846012 |
| Dashboard Live UI Proof | 30438187348 | failure | `a20c0af5fe5a` | 2026-07-29T09:06:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30438187348 |
| System3 Market Session Proof Runner | 30433617761 | failure | `506c561f061c` | 2026-07-29T08:01:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30433617761 |
| System3 Windows Self-Hosted Workflow Migration | 30422641994 | failure | `21176045c695` | 2026-07-29T04:35:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30422641994 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30441644246 | in_progress | 2026-07-29T09:56:11Z |
| Permanent Repo Render Safety | 30441313605 | in_progress | 2026-07-29T09:51:17Z |

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
