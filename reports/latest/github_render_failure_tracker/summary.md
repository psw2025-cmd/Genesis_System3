# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T23:21:30.345040Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29965488240 conclusion=failure commit=a0383367a3d8
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29965136652 conclusion=failure commit=8e133f3be199
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29965497748 conclusion=failure commit=2da560ddb755
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29965488276 conclusion=failure commit=a0383367a3d8
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29965456703 conclusion=failure commit=e5e368da4aa8
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29965488250 conclusion=failure commit=a0383367a3d8
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29965488267 conclusion=failure commit=a0383367a3d8
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29965104689 conclusion=failure commit=1fa4c5802482
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29964547672 conclusion=failure commit=8d4bf64412af
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
| Dashboard Shell Diagnostic | 29965488240 | failure | `a0383367a3d8` | 2026-07-22T23:17:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29965488240 |
| System3 Windows Self-Hosted Full Proof | 29965136652 | failure | `8e133f3be199` | 2026-07-22T23:14:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29965136652 |
| System3 Experimental Solution Planner | 29965497748 | failure | `2da560ddb755` | 2026-07-22T23:14:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29965497748 |
| System3 Secure Install Credential Audit | 29965488276 | failure | `a0383367a3d8` | 2026-07-22T23:14:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29965488276 |
| System3 Autopilot Proof Board | 29965456703 | failure | `e5e368da4aa8` | 2026-07-22T23:14:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29965456703 |
| Dashboard Visual Loading Postflight | 29965488250 | failure | `a0383367a3d8` | 2026-07-22T23:14:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29965488250 |
| Dashboard Visual Proof Strict Gate | 29965488267 | failure | `a0383367a3d8` | 2026-07-22T23:14:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29965488267 |
| Dashboard Visible Settle Proof | 29965104689 | failure | `1fa4c5802482` | 2026-07-22T23:12:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29965104689 |
| Dashboard Visible Proof Current | 29964547672 | failure | `8d4bf64412af` | 2026-07-22T23:08:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29964547672 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29965713656 | in_progress | 2026-07-22T23:19:02Z |
| Dashboard Visible Issue Tracker | 29965497768 | pending | 2026-07-22T23:14:18Z |
| Dashboard Visible Auth-Resilient Proof | 29965328851 | in_progress | 2026-07-22T23:11:05Z |

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
