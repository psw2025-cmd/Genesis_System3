# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-27T18:33:02.980811Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `13`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `25`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30293838192 conclusion=failure commit=e8cba517e073
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30292991891 conclusion=failure commit=e8cba517e073
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30292837448 conclusion=failure commit=e8cba517e073
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30292416595 conclusion=failure commit=403a1960e622
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30292261590 conclusion=failure commit=a71662502703
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30292250239 conclusion=failure commit=e4a0f5de201b
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30292261826 conclusion=failure commit=a71662502703
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30292204674 conclusion=failure commit=0dfc7126519c
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30292260402 conclusion=failure commit=a71662502703
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30292262141 conclusion=failure commit=a71662502703
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30292261495 conclusion=failure commit=a71662502703
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30291385371 conclusion=failure commit=31b4a19c6e15
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30291290520 conclusion=failure commit=4afcb5f96807
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
| System3 Safe Repair Runner | 30293838192 | failure | `e8cba517e073` | 2026-07-27T18:29:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30293838192 |
| Dashboard Visible Auth-Resilient Proof | 30292991891 | failure | `e8cba517e073` | 2026-07-27T18:17:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30292991891 |
| Dashboard Visible Settle Proof | 30292837448 | failure | `e8cba517e073` | 2026-07-27T18:14:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30292837448 |
| Dashboard Visible Proof Current | 30292416595 | failure | `403a1960e622` | 2026-07-27T18:08:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30292416595 |
| Dashboard Shell Diagnostic | 30292261590 | failure | `a71662502703` | 2026-07-27T18:08:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30292261590 |
| Dashboard Visible Issue Tracker | 30292250239 | failure | `e4a0f5de201b` | 2026-07-27T18:06:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30292250239 |
| System3 Secure Install Credential Audit | 30292261826 | failure | `a71662502703` | 2026-07-27T18:06:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30292261826 |
| System3 Autopilot Proof Board | 30292204674 | failure | `0dfc7126519c` | 2026-07-27T18:06:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30292204674 |
| System3 Experimental Solution Planner | 30292260402 | failure | `a71662502703` | 2026-07-27T18:06:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30292260402 |
| Dashboard Visual Proof Strict Gate | 30292262141 | failure | `a71662502703` | 2026-07-27T18:06:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30292262141 |
| Dashboard Visual Loading Postflight | 30292261495 | failure | `a71662502703` | 2026-07-27T18:06:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30292261495 |
| Dashboard Visible Proof Warmed | 30291385371 | failure | `31b4a19c6e15` | 2026-07-27T17:55:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30291385371 |
| System3 Backend Live Simulation Proof | 30291290520 | failure | `4afcb5f96807` | 2026-07-27T17:53:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30291290520 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Windows Self-Hosted Full Proof | 30292858318 | in_progress | 2026-07-27T18:14:27Z |

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
