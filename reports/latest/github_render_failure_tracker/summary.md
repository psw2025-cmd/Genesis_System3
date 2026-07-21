# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-21T12:33:24.975276Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29830291559 conclusion=failure commit=9945e035cd14
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29829961121 conclusion=failure commit=0e5a259d0bf1
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29829987290 conclusion=failure commit=370ddda024f3
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29829987259 conclusion=failure commit=370ddda024f3
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29829961120 conclusion=failure commit=0e5a259d0bf1
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29829961195 conclusion=failure commit=0e5a259d0bf1
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29828145570 conclusion=failure commit=5815a2f940bf
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
| System3 Experimental Solution Planner | 29830291559 | failure | `9945e035cd14` | 2026-07-21T12:29:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29830291559 |
| Dashboard Shell Diagnostic | 29829961121 | failure | `0e5a259d0bf1` | 2026-07-21T12:27:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29829961121 |
| System3 Autopilot Proof Board | 29829987290 | failure | `370ddda024f3` | 2026-07-21T12:25:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29829987290 |
| System3 Secure Install Credential Audit | 29829987259 | failure | `370ddda024f3` | 2026-07-21T12:25:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29829987259 |
| Dashboard Visual Proof Strict Gate | 29829961120 | failure | `0e5a259d0bf1` | 2026-07-21T12:24:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29829961120 |
| Dashboard Visual Loading Postflight | 29829961195 | failure | `0e5a259d0bf1` | 2026-07-21T12:24:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29829961195 |
| Dashboard Visible Proof Warmed | 29828145570 | failure | `5815a2f940bf` | 2026-07-21T11:58:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29828145570 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29830291620 | in_progress | 2026-07-21T12:30:00Z |
| Dashboard Visible Issue Tracker | 29829976153 | in_progress | 2026-07-21T12:29:54Z |

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
