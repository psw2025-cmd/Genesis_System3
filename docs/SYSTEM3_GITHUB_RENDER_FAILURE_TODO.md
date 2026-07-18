# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T20:16:23.125879Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `8`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `12`
TODO count: `20`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29659231528 conclusion=failure commit=f356ccb908e3
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29659243468 conclusion=failure commit=954c9284cb20
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29659265815 conclusion=failure commit=fb6522f161be
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29659243469 conclusion=failure commit=954c9284cb20
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29659049260 conclusion=failure commit=cda1435b1a4c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29659231498 conclusion=failure commit=f356ccb908e3
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29659231501 conclusion=failure commit=f356ccb908e3
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29658792648 conclusion=failure commit=b07f02c8e437
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
| Dashboard Shell Diagnostic | 29659231528 | failure | `f356ccb908e3` | 2026-07-18T20:14:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29659231528 |
| System3 Autopilot Proof Board | 29659243468 | failure | `954c9284cb20` | 2026-07-18T20:12:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29659243468 |
| System3 Experimental Solution Planner | 29659265815 | failure | `fb6522f161be` | 2026-07-18T20:12:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29659265815 |
| System3 Secure Install Credential Audit | 29659243469 | failure | `954c9284cb20` | 2026-07-18T20:12:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29659243469 |
| Dashboard Visible Settle Proof | 29659049260 | failure | `cda1435b1a4c` | 2026-07-18T20:12:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29659049260 |
| Dashboard Visual Proof Strict Gate | 29659231498 | failure | `f356ccb908e3` | 2026-07-18T20:11:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29659231498 |
| Dashboard Visual Loading Postflight | 29659231501 | failure | `f356ccb908e3` | 2026-07-18T20:11:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29659231501 |
| Dashboard Visible Proof Current | 29658792648 | failure | `b07f02c8e437` | 2026-07-18T20:10:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29658792648 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29659296303 | in_progress | 2026-07-18T20:13:56Z |
| Dashboard Visible Issue Tracker | 29659230629 | pending | 2026-07-18T20:11:40Z |
| Dashboard Visible Auth-Resilient Proof | 29659090595 | in_progress | 2026-07-18T20:07:14Z |
| System3 Windows Self-Hosted Full Proof | 29659069366 | in_progress | 2026-07-18T20:06:36Z |

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
