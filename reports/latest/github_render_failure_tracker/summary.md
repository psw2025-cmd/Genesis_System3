# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-17T18:22:55.036246Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29603360365 conclusion=failure commit=21c84c352ab5
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29603321384 conclusion=failure commit=d34ae8512f46
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29603360388 conclusion=failure commit=21c84c352ab5
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29603363218 conclusion=failure commit=21c84c352ab5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29603360412 conclusion=failure commit=21c84c352ab5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29603360408 conclusion=failure commit=21c84c352ab5
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29602642062 conclusion=failure commit=ed62e6ad3e9f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29602616881 conclusion=failure commit=ed62e6ad3e9f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29602020612 conclusion=failure commit=f9fcd73362f6
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
| Dashboard Shell Diagnostic | 29603360365 | failure | `21c84c352ab5` | 2026-07-17T18:22:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29603360365 |
| System3 Autopilot Proof Board | 29603321384 | failure | `d34ae8512f46` | 2026-07-17T18:19:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29603321384 |
| System3 Secure Install Credential Audit | 29603360388 | failure | `21c84c352ab5` | 2026-07-17T18:19:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29603360388 |
| System3 Experimental Solution Planner | 29603363218 | failure | `21c84c352ab5` | 2026-07-17T18:19:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29603363218 |
| Dashboard Visual Proof Strict Gate | 29603360412 | failure | `21c84c352ab5` | 2026-07-17T18:19:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29603360412 |
| Dashboard Visual Loading Postflight | 29603360408 | failure | `21c84c352ab5` | 2026-07-17T18:19:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29603360408 |
| System3 Windows Self-Hosted Full Proof | 29602642062 | failure | `ed62e6ad3e9f` | 2026-07-17T18:15:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29602642062 |
| Dashboard Visible Settle Proof | 29602616881 | failure | `ed62e6ad3e9f` | 2026-07-17T18:13:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29602616881 |
| Dashboard Visible Proof Current | 29602020612 | failure | `f9fcd73362f6` | 2026-07-17T18:03:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29602020612 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29603363164 | in_progress | 2026-07-17T18:19:16Z |
| Dashboard Visible Issue Tracker | 29603363145 | pending | 2026-07-17T18:19:03Z |
| Dashboard Visible Auth-Resilient Proof | 29602888938 | in_progress | 2026-07-17T18:11:25Z |

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
