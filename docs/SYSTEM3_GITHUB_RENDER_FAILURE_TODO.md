# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-31T06:59:39.201801Z`
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

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30607610795 conclusion=failure commit=33a2a4dfcf22
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30607794788 conclusion=failure commit=33a2a4dfcf22
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30607585793 conclusion=failure commit=33a2a4dfcf22
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30607073927 conclusion=failure commit=33a2a4dfcf22
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30607000249 conclusion=failure commit=33a2a4dfcf22
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30606676231 conclusion=failure commit=3ba20579dc4c
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30606822127 conclusion=failure commit=0690fdf4a7a9
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30606770764 conclusion=failure commit=3ba20579dc4c
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
| System3 Full Auto Truth | 30607610795 | failure | `33a2a4dfcf22` | 2026-07-31T06:09:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30607610795 |
| System3 Broker Chain Semantic Gate | 30607794788 | failure | `33a2a4dfcf22` | 2026-07-31T05:48:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30607794788 |
| Dashboard Live UI Proof | 30607585793 | failure | `33a2a4dfcf22` | 2026-07-31T05:43:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30607585793 |
| Dashboard Visible Proof Warmed | 30607073927 | failure | `33a2a4dfcf22` | 2026-07-31T05:33:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30607073927 |
| System3 Backend Live Simulation Proof | 30607000249 | failure | `33a2a4dfcf22` | 2026-07-31T05:31:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30607000249 |
| System3 Market Session Proof Runner | 30606676231 | failure | `3ba20579dc4c` | 2026-07-31T05:27:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30606676231 |
| Dashboard Deploy Provenance Gate | 30606822127 | failure | `0690fdf4a7a9` | 2026-07-31T05:27:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30606822127 |
| Dashboard Visual Production Proof | 30606770764 | failure | `3ba20579dc4c` | 2026-07-31T05:26:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30606770764 |
| System3 Windows Self-Hosted Workflow Migration | 30604659882 | failure | `4474010bb446` | 2026-07-31T04:40:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30604659882 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30611208769 | in_progress | 2026-07-31T06:57:20Z |
| Permanent Repo Render Safety | 30611038208 | in_progress | 2026-07-31T06:54:03Z |

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
