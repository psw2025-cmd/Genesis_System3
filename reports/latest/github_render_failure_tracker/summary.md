# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-31T05:10:40.632069Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30605717470 conclusion=failure commit=e2d3e8cb78de
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30604659882 conclusion=failure commit=4474010bb446
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30603549277 conclusion=failure commit=82efd511f721
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30603803078 conclusion=failure commit=53cc2bd42da5
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30603270038 conclusion=failure commit=82efd511f721
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30603411777 conclusion=failure commit=82efd511f721
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30601762879 conclusion=failure commit=82efd511f721
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30601666131 conclusion=failure commit=82efd511f721
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30601496951 conclusion=failure commit=b8662e40dc34
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30601445239 conclusion=failure commit=b8662e40dc34
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
| System3 Market Session Proof Runner | 30605717470 | failure | `e2d3e8cb78de` | 2026-07-31T05:06:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30605717470 |
| System3 Windows Self-Hosted Workflow Migration | 30604659882 | failure | `4474010bb446` | 2026-07-31T04:40:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30604659882 |
| System3 Full Auto Truth | 30603549277 | failure | `82efd511f721` | 2026-07-31T04:37:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30603549277 |
| System3 Broker Chain Semantic Gate | 30603803078 | failure | `53cc2bd42da5` | 2026-07-31T04:18:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30603803078 |
| Permanent Repo Render Safety | 30603270038 | failure | `82efd511f721` | 2026-07-31T04:15:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30603270038 |
| Dashboard Live UI Proof | 30603411777 | failure | `82efd511f721` | 2026-07-31T04:10:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30603411777 |
| Dashboard Visible Proof Warmed | 30601762879 | failure | `82efd511f721` | 2026-07-31T03:31:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30601762879 |
| System3 Backend Live Simulation Proof | 30601666131 | failure | `82efd511f721` | 2026-07-31T03:29:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30601666131 |
| Dashboard Deploy Provenance Gate | 30601496951 | failure | `b8662e40dc34` | 2026-07-31T03:25:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30601496951 |
| Dashboard Visual Production Proof | 30601445239 | failure | `b8662e40dc34` | 2026-07-31T03:24:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30601445239 |

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
