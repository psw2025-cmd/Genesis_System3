# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-29T06:55:27.978241Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30428734659 conclusion=failure commit=e47e51cec233
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30425495353 conclusion=failure commit=90922c9a581c
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30425453462 conclusion=failure commit=90922c9a581c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30425225556 conclusion=failure commit=90922c9a581c
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30425167133 conclusion=failure commit=90922c9a581c
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30425022292 conclusion=failure commit=adc441ea55d3
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30424989935 conclusion=failure commit=c5d22f4c93b2
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30424847319 conclusion=failure commit=30681c9fb89e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30424945631 conclusion=failure commit=30681c9fb89e
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
| System3 Broker Chain Semantic Gate | 30428734659 | failure | `e47e51cec233` | 2026-07-29T06:37:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30428734659 |
| System3 Full Auto Truth | 30425495353 | failure | `90922c9a581c` | 2026-07-29T05:59:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30425495353 |
| Dashboard Live UI Proof | 30425453462 | failure | `90922c9a581c` | 2026-07-29T05:34:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30425453462 |
| Dashboard Visible Proof Warmed | 30425225556 | failure | `90922c9a581c` | 2026-07-29T05:30:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30425225556 |
| System3 Backend Live Simulation Proof | 30425167133 | failure | `90922c9a581c` | 2026-07-29T05:28:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30425167133 |
| System3 Render Worker Preflight | 30425022292 | failure | `adc441ea55d3` | 2026-07-29T05:25:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30425022292 |
| Dashboard Deploy Provenance Gate | 30424989935 | failure | `c5d22f4c93b2` | 2026-07-29T05:25:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30424989935 |
| System3 Market Session Proof Runner | 30424847319 | failure | `30681c9fb89e` | 2026-07-29T05:25:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30424847319 |
| Dashboard Visual Production Proof | 30424945631 | failure | `30681c9fb89e` | 2026-07-29T05:24:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30424945631 |
| System3 Windows Self-Hosted Workflow Migration | 30422641994 | failure | `21176045c695` | 2026-07-29T04:35:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30422641994 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30429619719 | in_progress | 2026-07-29T06:52:42Z |
| Permanent Repo Render Safety | 30429429276 | in_progress | 2026-07-29T06:49:20Z |

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
