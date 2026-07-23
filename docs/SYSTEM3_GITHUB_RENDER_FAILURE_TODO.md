# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T15:39:46.970575Z`
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

- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30021136081 conclusion=failure commit=77140933fb50
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30020130952 conclusion=failure commit=ee8cd7b6e860
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30020705407 conclusion=failure commit=98e613f56200
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30020804168 conclusion=failure commit=afdad7866da5
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30020804172 conclusion=failure commit=afdad7866da5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30020704926 conclusion=failure commit=98e613f56200
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30020705810 conclusion=failure commit=98e613f56200
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30018713378 conclusion=failure commit=5ec036e0a4a1
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30018575008 conclusion=failure commit=5ec036e0a4a1
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
| System3 Experimental Solution Planner | 30021136081 | failure | `77140933fb50` | 2026-07-23T15:34:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30021136081 |
| Dashboard Visible Proof Current | 30020130952 | failure | `ee8cd7b6e860` | 2026-07-23T15:33:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30020130952 |
| Dashboard Shell Diagnostic | 30020705407 | failure | `98e613f56200` | 2026-07-23T15:31:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30020705407 |
| System3 Autopilot Proof Board | 30020804168 | failure | `afdad7866da5` | 2026-07-23T15:30:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30020804168 |
| System3 Secure Install Credential Audit | 30020804172 | failure | `afdad7866da5` | 2026-07-23T15:30:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30020804172 |
| Dashboard Visual Loading Postflight | 30020704926 | failure | `98e613f56200` | 2026-07-23T15:28:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30020704926 |
| Dashboard Visual Proof Strict Gate | 30020705810 | failure | `98e613f56200` | 2026-07-23T15:28:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30020705810 |
| Dashboard Visible Proof Warmed | 30018713378 | failure | `5ec036e0a4a1` | 2026-07-23T15:04:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30018713378 |
| System3 Backend Live Simulation Proof | 30018575008 | failure | `5ec036e0a4a1` | 2026-07-23T15:01:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30018575008 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 30021312320 | in_progress | 2026-07-23T15:36:55Z |
| Dashboard Visible Issue Tracker | 30021136593 | pending | 2026-07-23T15:34:02Z |

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
