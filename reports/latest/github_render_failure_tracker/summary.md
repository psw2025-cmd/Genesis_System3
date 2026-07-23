# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T21:24:18.196601Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30045751915 conclusion=failure commit=a05ef22e1a9a
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30045751681 conclusion=failure commit=a05ef22e1a9a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30045752127 conclusion=failure commit=a05ef22e1a9a
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30045751741 conclusion=failure commit=a05ef22e1a9a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30045751683 conclusion=failure commit=a05ef22e1a9a
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30045687411 conclusion=failure commit=2af9020e4d41
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30044885497 conclusion=failure commit=feb6cb4b1d7c
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30044917174 conclusion=failure commit=feb6cb4b1d7c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30044177123 conclusion=failure commit=d1a0f002c200
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
| Dashboard Shell Diagnostic | 30045751915 | failure | `a05ef22e1a9a` | 2026-07-23T21:23:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30045751915 |
| System3 Secure Install Credential Audit | 30045751681 | failure | `a05ef22e1a9a` | 2026-07-23T21:20:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30045751681 |
| Dashboard Visual Loading Postflight | 30045752127 | failure | `a05ef22e1a9a` | 2026-07-23T21:20:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30045752127 |
| System3 Experimental Solution Planner | 30045751741 | failure | `a05ef22e1a9a` | 2026-07-23T21:20:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30045751741 |
| Dashboard Visual Proof Strict Gate | 30045751683 | failure | `a05ef22e1a9a` | 2026-07-23T21:20:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30045751683 |
| System3 Autopilot Proof Board | 30045687411 | failure | `2af9020e4d41` | 2026-07-23T21:20:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30045687411 |
| Dashboard Visible Settle Proof | 30044885497 | failure | `feb6cb4b1d7c` | 2026-07-23T21:13:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30044885497 |
| System3 Windows Self-Hosted Full Proof | 30044917174 | failure | `feb6cb4b1d7c` | 2026-07-23T21:12:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30044917174 |
| Dashboard Visible Proof Current | 30044177123 | failure | `d1a0f002c200` | 2026-07-23T21:08:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30044177123 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 30045838684 | in_progress | 2026-07-23T21:22:04Z |
| Dashboard Visible Issue Tracker | 30045747509 | pending | 2026-07-23T21:20:04Z |
| Dashboard Visible Auth-Resilient Proof | 30045190084 | in_progress | 2026-07-23T21:11:36Z |

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
