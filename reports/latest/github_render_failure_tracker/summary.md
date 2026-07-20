# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T20:30:57.066900Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29775985505 conclusion=failure commit=5a2fdfc98b95
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29776014652 conclusion=failure commit=526b0c5703b5
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29776062373 conclusion=failure commit=ff4cdb5d3efb
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29776010374 conclusion=failure commit=526b0c5703b5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29775985547 conclusion=failure commit=5a2fdfc98b95
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29775985409 conclusion=failure commit=5a2fdfc98b95
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29773853651 conclusion=failure commit=f60ca979e1d1
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29773927076 conclusion=failure commit=f60ca979e1d1
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29773889251 conclusion=failure commit=f60ca979e1d1
- [ ] Fix Render endpoint /: HTTP status 502 status=502
- [ ] Fix Render endpoint /ui/: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/health: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/state: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/paper: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 502 status=502

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Shell Diagnostic | 29775985505 | failure | `5a2fdfc98b95` | 2026-07-20T20:27:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29775985505 |
| System3 Autopilot Proof Board | 29776014652 | failure | `526b0c5703b5` | 2026-07-20T20:26:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29776014652 |
| System3 Experimental Solution Planner | 29776062373 | failure | `ff4cdb5d3efb` | 2026-07-20T20:25:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29776062373 |
| System3 Secure Install Credential Audit | 29776010374 | failure | `526b0c5703b5` | 2026-07-20T20:25:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29776010374 |
| Dashboard Visual Loading Postflight | 29775985547 | failure | `5a2fdfc98b95` | 2026-07-20T20:24:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29775985547 |
| Dashboard Visual Proof Strict Gate | 29775985409 | failure | `5a2fdfc98b95` | 2026-07-20T20:24:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29775985409 |
| Dashboard Visible Auth-Resilient Proof | 29773853651 | failure | `f60ca979e1d1` | 2026-07-20T20:12:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29773853651 |
| Dashboard Visible Proof Warmed | 29773927076 | failure | `f60ca979e1d1` | 2026-07-20T19:55:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29773927076 |
| System3 Backend Live Simulation Proof | 29773889251 | failure | `f60ca979e1d1` | 2026-07-20T19:54:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29773889251 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29775992597 | in_progress | 2026-07-20T20:29:00Z |
| System3 Safe Repair Runner | 29776142195 | in_progress | 2026-07-20T20:27:15Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 502 | HTTP status 502 | `none` |
| `/ui/` | 502 | HTTP status 502 | `none` |
| `/api/health` | 502 | HTTP status 502 | `none` |
| `/api/state` | 502 | HTTP status 502 | `none` |
| `/api/deploy/info` | 502 | HTTP status 502 | `none` |
| `/api/broker/diagnose` | 502 | HTTP status 502 | `none` |
| `/api/broker/funds` | 502 | HTTP status 502 | `none` |
| `/api/broker/holdings` | 502 | HTTP status 502 | `none` |
| `/api/broker/positions/live` | 502 | HTTP status 502 | `none` |
| `/api/scanner/top_contract_gainers` | 502 | HTTP status 502 | `none` |
| `/api/paper` | 502 | HTTP status 502 | `none` |
| `/api/ml/performance` | 502 | HTTP status 502 | `none` |
