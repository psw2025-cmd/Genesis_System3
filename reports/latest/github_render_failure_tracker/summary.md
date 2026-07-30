# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-30T06:54:07.310081Z`
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

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30519393371 conclusion=failure commit=ea70905bc2ec
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30519841542 conclusion=failure commit=bb75741b33ef
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30519053994 conclusion=failure commit=ea70905bc2ec
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30519275067 conclusion=failure commit=ea70905bc2ec
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30516345500 conclusion=failure commit=6faed4d499a7
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30516312769 conclusion=failure commit=6faed4d499a7
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30516178810 conclusion=failure commit=6ce1ffeb8b9f
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30516247111 conclusion=failure commit=7202c3b42d45
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30516232754 conclusion=failure commit=7ea222070c2b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30516201360 conclusion=failure commit=6ce1ffeb8b9f
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30514055102 conclusion=failure commit=275458e986fa
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
| System3 Full Auto Truth | 30519393371 | failure | `ea70905bc2ec` | 2026-07-30T06:47:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30519393371 |
| System3 Broker Chain Semantic Gate | 30519841542 | failure | `bb75741b33ef` | 2026-07-30T06:31:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30519841542 |
| Permanent Repo Render Safety | 30519053994 | failure | `ea70905bc2ec` | 2026-07-30T06:25:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30519053994 |
| Dashboard Live UI Proof | 30519275067 | failure | `ea70905bc2ec` | 2026-07-30T06:21:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30519275067 |
| Dashboard Visible Proof Warmed | 30516345500 | failure | `6faed4d499a7` | 2026-07-30T05:21:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30516345500 |
| System3 Backend Live Simulation Proof | 30516312769 | failure | `6faed4d499a7` | 2026-07-30T05:20:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30516312769 |
| System3 Market Session Proof Runner | 30516178810 | failure | `6ce1ffeb8b9f` | 2026-07-30T05:20:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30516178810 |
| System3 Render Worker Preflight | 30516247111 | failure | `7202c3b42d45` | 2026-07-30T05:18:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30516247111 |
| Dashboard Deploy Provenance Gate | 30516232754 | failure | `7ea222070c2b` | 2026-07-30T05:18:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30516232754 |
| Dashboard Visual Production Proof | 30516201360 | failure | `6ce1ffeb8b9f` | 2026-07-30T05:18:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30516201360 |
| System3 Windows Self-Hosted Workflow Migration | 30514055102 | failure | `275458e986fa` | 2026-07-30T04:31:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30514055102 |

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
