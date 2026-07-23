# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T13:33:47.463919Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30010723933 conclusion=failure commit=5b50feb03a1f
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30010758439 conclusion=failure commit=f2432de36471
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30010801311 conclusion=failure commit=9d808f4af3be
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30010758418 conclusion=failure commit=f2432de36471
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30009875147 conclusion=failure commit=d1996aaa516f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30010724499 conclusion=failure commit=5b50feb03a1f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30010724123 conclusion=failure commit=5b50feb03a1f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30008700158 conclusion=failure commit=1ee1cb23e2e6
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30008623016 conclusion=failure commit=1ee1cb23e2e6
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
| Dashboard Shell Diagnostic | 30010723933 | failure | `5b50feb03a1f` | 2026-07-23T13:22:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30010723933 |
| System3 Autopilot Proof Board | 30010758439 | failure | `f2432de36471` | 2026-07-23T13:21:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30010758439 |
| System3 Experimental Solution Planner | 30010801311 | failure | `9d808f4af3be` | 2026-07-23T13:20:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30010801311 |
| System3 Secure Install Credential Audit | 30010758418 | failure | `f2432de36471` | 2026-07-23T13:20:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30010758418 |
| Dashboard Visible Proof Current | 30009875147 | failure | `d1996aaa516f` | 2026-07-23T13:20:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30009875147 |
| Dashboard Visual Loading Postflight | 30010724499 | failure | `5b50feb03a1f` | 2026-07-23T13:19:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30010724499 |
| Dashboard Visual Proof Strict Gate | 30010724123 | failure | `5b50feb03a1f` | 2026-07-23T13:19:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30010724123 |
| Dashboard Visible Proof Warmed | 30008700158 | failure | `1ee1cb23e2e6` | 2026-07-23T12:52:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30008700158 |
| System3 Backend Live Simulation Proof | 30008623016 | failure | `1ee1cb23e2e6` | 2026-07-23T12:50:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30008623016 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 30011476796 | in_progress | 2026-07-23T13:30:14Z |
| Dashboard Visible Issue Tracker | 30010724779 | in_progress | 2026-07-23T13:27:00Z |

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
