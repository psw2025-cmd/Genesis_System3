# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T20:24:38.030746Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `14`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `26`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29954502723 conclusion=failure commit=4f613157f4e0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29954208086 conclusion=failure commit=dbb0bebde285
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29954532756 conclusion=failure commit=af93d003c1b6
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29954568353 conclusion=failure commit=c37d3445ebcb
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29954532803 conclusion=failure commit=af93d003c1b6
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29954502644 conclusion=failure commit=4f613157f4e0
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29954502733 conclusion=failure commit=4f613157f4e0
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=29952299551 conclusion=cancelled commit=c33a3031c05c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29952688366 conclusion=failure commit=faff22d13004
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29952271238 conclusion=failure commit=c33a3031c05c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29952608792 conclusion=failure commit=faff22d13004
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29951811228 conclusion=failure commit=ae54748415a5
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29952535379 conclusion=failure commit=faff22d13004
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=29952368668 conclusion=failure commit=f81fca93f67c
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
| Dashboard Shell Diagnostic | 29954502723 | failure | `4f613157f4e0` | 2026-07-22T20:20:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29954502723 |
| Dashboard Visible Settle Proof | 29954208086 | failure | `dbb0bebde285` | 2026-07-22T20:19:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29954208086 |
| System3 Autopilot Proof Board | 29954532756 | failure | `af93d003c1b6` | 2026-07-22T20:18:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29954532756 |
| System3 Experimental Solution Planner | 29954568353 | failure | `c37d3445ebcb` | 2026-07-22T20:18:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29954568353 |
| System3 Secure Install Credential Audit | 29954532803 | failure | `af93d003c1b6` | 2026-07-22T20:18:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29954532803 |
| Dashboard Visual Proof Strict Gate | 29954502644 | failure | `4f613157f4e0` | 2026-07-22T20:17:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29954502644 |
| Dashboard Visual Loading Postflight | 29954502733 | failure | `4f613157f4e0` | 2026-07-22T20:17:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29954502733 |
| Dashboard Visual Production Proof | 29952299551 | cancelled | `c33a3031c05c` | 2026-07-22T20:15:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29952299551 |
| Dashboard Visible Auth-Resilient Proof | 29952688366 | failure | `faff22d13004` | 2026-07-22T20:09:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29952688366 |
| System3 Windows Self-Hosted Full Proof | 29952271238 | failure | `c33a3031c05c` | 2026-07-22T19:51:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29952271238 |
| Dashboard Visible Proof Warmed | 29952608792 | failure | `faff22d13004` | 2026-07-22T19:50:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29952608792 |
| Dashboard Visible Proof Current | 29951811228 | failure | `ae54748415a5` | 2026-07-22T19:50:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29951811228 |
| System3 Backend Live Simulation Proof | 29952535379 | failure | `faff22d13004` | 2026-07-22T19:49:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29952535379 |
| Dashboard Deploy Provenance Gate | 29952368668 | failure | `f81fca93f67c` | 2026-07-22T19:47:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29952368668 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29954775367 | in_progress | 2026-07-22T20:21:58Z |
| Dashboard Visible Issue Tracker | 29954503361 | in_progress | 2026-07-22T20:21:41Z |

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
