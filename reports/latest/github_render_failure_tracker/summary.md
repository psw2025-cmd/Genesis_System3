# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T19:32:37.715580Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29771932041 conclusion=failure commit=5af50968ba54
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29771956209 conclusion=failure commit=846cf48039bd
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29771999234 conclusion=failure commit=d3e1820599ec
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29771956221 conclusion=failure commit=846cf48039bd
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29771931979 conclusion=failure commit=5af50968ba54
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29771931887 conclusion=failure commit=5af50968ba54
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29769917014 conclusion=failure commit=f5e96fee7725
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29770148444 conclusion=failure commit=f5e96fee7725
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29770037926 conclusion=failure commit=f5e96fee7725
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
| Dashboard Shell Diagnostic | 29771932041 | failure | `5af50968ba54` | 2026-07-20T19:28:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29771932041 |
| System3 Autopilot Proof Board | 29771956209 | failure | `846cf48039bd` | 2026-07-20T19:26:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29771956209 |
| System3 Experimental Solution Planner | 29771999234 | failure | `d3e1820599ec` | 2026-07-20T19:26:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29771999234 |
| System3 Secure Install Credential Audit | 29771956221 | failure | `846cf48039bd` | 2026-07-20T19:26:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29771956221 |
| Dashboard Visual Loading Postflight | 29771931979 | failure | `5af50968ba54` | 2026-07-20T19:25:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29771931979 |
| Dashboard Visual Proof Strict Gate | 29771931887 | failure | `5af50968ba54` | 2026-07-20T19:25:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29771931887 |
| Dashboard Visible Auth-Resilient Proof | 29769917014 | failure | `f5e96fee7725` | 2026-07-20T19:15:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29769917014 |
| Dashboard Visible Proof Warmed | 29770148444 | failure | `f5e96fee7725` | 2026-07-20T19:00:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29770148444 |
| System3 Backend Live Simulation Proof | 29770037926 | failure | `f5e96fee7725` | 2026-07-20T18:59:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29770037926 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29772247730 | in_progress | 2026-07-20T19:30:50Z |
| Dashboard Visible Issue Tracker | 29771931603 | pending | 2026-07-20T19:25:34Z |

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
