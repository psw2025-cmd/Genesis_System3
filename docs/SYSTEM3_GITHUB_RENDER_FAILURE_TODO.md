# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-16T19:28:05.913737Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29526975506 conclusion=failure commit=c675752cc034
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29527028254 conclusion=failure commit=573e53bc7c3a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29526800930 conclusion=failure commit=d527ed7b536b
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29527071629 conclusion=failure commit=2b2432cb3ad1
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29527101548 conclusion=failure commit=74e186a3a60d
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29527071689 conclusion=failure commit=2b2432cb3ad1
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29527042625 conclusion=failure commit=fb8435095ff6
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29527030181 conclusion=failure commit=573e53bc7c3a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29526202649 conclusion=failure commit=b4433d829a26
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
| System3 Windows Self-Hosted Full Proof | 29526975506 | failure | `c675752cc034` | 2026-07-16T19:19:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29526975506 |
| Dashboard Shell Diagnostic | 29527028254 | failure | `573e53bc7c3a` | 2026-07-16T19:14:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29527028254 |
| Dashboard Visible Settle Proof | 29526800930 | failure | `d527ed7b536b` | 2026-07-16T19:14:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29526800930 |
| System3 Autopilot Proof Board | 29527071629 | failure | `2b2432cb3ad1` | 2026-07-16T19:13:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29527071629 |
| System3 Experimental Solution Planner | 29527101548 | failure | `74e186a3a60d` | 2026-07-16T19:12:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29527101548 |
| System3 Secure Install Credential Audit | 29527071689 | failure | `2b2432cb3ad1` | 2026-07-16T19:12:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29527071689 |
| Dashboard Visual Proof Strict Gate | 29527042625 | failure | `fb8435095ff6` | 2026-07-16T19:12:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29527042625 |
| Dashboard Visual Loading Postflight | 29527030181 | failure | `573e53bc7c3a` | 2026-07-16T19:11:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29527030181 |
| Dashboard Visible Proof Current | 29526202649 | failure | `b4433d829a26` | 2026-07-16T19:11:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29526202649 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29527961348 | in_progress | 2026-07-16T19:26:33Z |
| Dashboard Visible Issue Tracker | 29527036621 | in_progress | 2026-07-16T19:23:46Z |
| Dashboard Visible Auth-Resilient Proof | 29527085550 | in_progress | 2026-07-16T19:12:37Z |

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
