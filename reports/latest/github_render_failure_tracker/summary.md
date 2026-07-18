# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T19:25:33.648802Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29657477098 conclusion=failure commit=47dfd1773732
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29657490226 conclusion=failure commit=02ff57b04dcd
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29657509431 conclusion=failure commit=8b8388dccce8
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29657490211 conclusion=failure commit=02ff57b04dcd
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29657194792 conclusion=failure commit=bcec269e13ae
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29657477109 conclusion=failure commit=47dfd1773732
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29657477103 conclusion=failure commit=47dfd1773732
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29657179394 conclusion=failure commit=bcec269e13ae
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29656837089 conclusion=failure commit=b5ec389c3727
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
| Dashboard Shell Diagnostic | 29657477098 | failure | `47dfd1773732` | 2026-07-18T19:19:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29657477098 |
| System3 Autopilot Proof Board | 29657490226 | failure | `02ff57b04dcd` | 2026-07-18T19:17:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29657490226 |
| System3 Experimental Solution Planner | 29657509431 | failure | `8b8388dccce8` | 2026-07-18T19:17:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29657509431 |
| System3 Secure Install Credential Audit | 29657490211 | failure | `02ff57b04dcd` | 2026-07-18T19:17:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29657490211 |
| System3 Windows Self-Hosted Full Proof | 29657194792 | failure | `bcec269e13ae` | 2026-07-18T19:16:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29657194792 |
| Dashboard Visual Loading Postflight | 29657477109 | failure | `47dfd1773732` | 2026-07-18T19:16:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29657477109 |
| Dashboard Visual Proof Strict Gate | 29657477103 | failure | `47dfd1773732` | 2026-07-18T19:16:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29657477103 |
| Dashboard Visible Settle Proof | 29657179394 | failure | `bcec269e13ae` | 2026-07-18T19:13:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29657179394 |
| Dashboard Visible Proof Current | 29656837089 | failure | `b5ec389c3727` | 2026-07-18T19:02:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29656837089 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29657682432 | in_progress | 2026-07-18T19:23:25Z |
| Dashboard Visible Issue Tracker | 29657132710 | in_progress | 2026-07-18T19:16:29Z |
| Dashboard Visible Auth-Resilient Proof | 29657328384 | in_progress | 2026-07-18T19:11:50Z |

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
