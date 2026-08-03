# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T05:13:28.781453Z`
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

- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30786060373 conclusion=failure commit=4aa83a7a4d2c
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30785078018 conclusion=failure commit=f660e3fc0791
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30783983185 conclusion=failure commit=d3ea26dc2fad
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30783740900 conclusion=failure commit=d3ea26dc2fad
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30784185467 conclusion=failure commit=d3ea26dc2fad
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30783663403 conclusion=failure commit=d3ea26dc2fad
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30783856816 conclusion=failure commit=d3ea26dc2fad
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30781982921 conclusion=failure commit=d3ea26dc2fad
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30781893382 conclusion=failure commit=d3ea26dc2fad
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30781728600 conclusion=failure commit=f20fa4e83fdf
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30781681375 conclusion=failure commit=f20fa4e83fdf
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
| System3 Market Session Proof Runner | 30786060373 | failure | `4aa83a7a4d2c` | 2026-08-03T05:06:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30786060373 |
| System3 Windows Self-Hosted Workflow Migration | 30785078018 | failure | `f660e3fc0791` | 2026-08-03T04:41:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30785078018 |
| System3 Full Auto Truth | 30783983185 | failure | `d3ea26dc2fad` | 2026-08-03T04:41:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30783983185 |
| System3 Latest Truth Publish | 30783740900 | failure | `d3ea26dc2fad` | 2026-08-03T04:22:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30783740900 |
| System3 Broker Chain Semantic Gate | 30784185467 | failure | `d3ea26dc2fad` | 2026-08-03T04:21:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30784185467 |
| Permanent Repo Render Safety | 30783663403 | failure | `d3ea26dc2fad` | 2026-08-03T04:20:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30783663403 |
| Dashboard Live UI Proof | 30783856816 | failure | `d3ea26dc2fad` | 2026-08-03T04:15:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30783856816 |
| Dashboard Visible Proof Warmed | 30781982921 | failure | `d3ea26dc2fad` | 2026-08-03T03:31:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30781982921 |
| System3 Backend Live Simulation Proof | 30781893382 | failure | `d3ea26dc2fad` | 2026-08-03T03:29:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30781893382 |
| Dashboard Deploy Provenance Gate | 30781728600 | failure | `f20fa4e83fdf` | 2026-08-03T03:25:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30781728600 |
| Dashboard Visual Production Proof | 30781681375 | failure | `f20fa4e83fdf` | 2026-08-03T03:24:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30781681375 |

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
