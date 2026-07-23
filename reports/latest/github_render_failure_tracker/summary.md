# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T17:31:08.649448Z`
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

- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30028868755 conclusion=failure commit=6225074fbc03
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30028823685 conclusion=failure commit=2c70a6a57058
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30029034315 conclusion=failure commit=546802581ff0
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30028868706 conclusion=failure commit=6225074fbc03
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30028823579 conclusion=failure commit=2c70a6a57058
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30028823546 conclusion=failure commit=2c70a6a57058
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30027808842 conclusion=failure commit=936c94bdfae9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30026870971 conclusion=failure commit=4e1e912ef8c2
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30026782827 conclusion=failure commit=4e1e912ef8c2
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
| System3 Autopilot Proof Board | 30028868755 | failure | `6225074fbc03` | 2026-07-23T17:22:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30028868755 |
| Dashboard Shell Diagnostic | 30028823685 | failure | `2c70a6a57058` | 2026-07-23T17:21:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30028823685 |
| System3 Experimental Solution Planner | 30029034315 | failure | `546802581ff0` | 2026-07-23T17:21:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30029034315 |
| System3 Secure Install Credential Audit | 30028868706 | failure | `6225074fbc03` | 2026-07-23T17:19:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30028868706 |
| Dashboard Visual Loading Postflight | 30028823579 | failure | `2c70a6a57058` | 2026-07-23T17:18:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30028823579 |
| Dashboard Visual Proof Strict Gate | 30028823546 | failure | `2c70a6a57058` | 2026-07-23T17:18:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30028823546 |
| Dashboard Visible Proof Current | 30027808842 | failure | `936c94bdfae9` | 2026-07-23T17:15:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30027808842 |
| Dashboard Visible Proof Warmed | 30026870971 | failure | `4e1e912ef8c2` | 2026-07-23T16:51:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30026870971 |
| System3 Backend Live Simulation Proof | 30026782827 | failure | `4e1e912ef8c2` | 2026-07-23T16:50:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30026782827 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 30029523268 | in_progress | 2026-07-23T17:28:40Z |
| Dashboard Visible Issue Tracker | 30029034253 | in_progress | 2026-07-23T17:25:38Z |

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
