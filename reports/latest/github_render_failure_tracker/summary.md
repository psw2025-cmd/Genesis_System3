# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T15:36:44.276844Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29755501137 conclusion=failure commit=67a2f415cbbd
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29755540353 conclusion=failure commit=c0d72e0028c6
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29755595198 conclusion=failure commit=59dc9255665b
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29755062050 conclusion=failure commit=4d42a8e7459b
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29755540358 conclusion=failure commit=c0d72e0028c6
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29754649058 conclusion=failure commit=f8ca77f2a8c8
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29755500330 conclusion=failure commit=67a2f415cbbd
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29755500344 conclusion=failure commit=67a2f415cbbd
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29755031557 conclusion=failure commit=4d42a8e7459b
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=29755373439 conclusion=failure commit=43471cb2e517
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
| Dashboard Shell Diagnostic | 29755501137 | failure | `67a2f415cbbd` | 2026-07-20T15:34:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29755501137 |
| System3 Autopilot Proof Board | 29755540353 | failure | `c0d72e0028c6` | 2026-07-20T15:32:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29755540353 |
| System3 Experimental Solution Planner | 29755595198 | failure | `59dc9255665b` | 2026-07-20T15:32:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29755595198 |
| System3 Windows Self-Hosted Full Proof | 29755062050 | failure | `4d42a8e7459b` | 2026-07-20T15:31:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29755062050 |
| System3 Secure Install Credential Audit | 29755540358 | failure | `c0d72e0028c6` | 2026-07-20T15:31:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29755540358 |
| Dashboard Visible Proof Current | 29754649058 | failure | `f8ca77f2a8c8` | 2026-07-20T15:31:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29754649058 |
| Dashboard Visual Proof Strict Gate | 29755500330 | failure | `67a2f415cbbd` | 2026-07-20T15:31:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29755500330 |
| Dashboard Visual Loading Postflight | 29755500344 | failure | `67a2f415cbbd` | 2026-07-20T15:30:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29755500344 |
| Dashboard Visible Settle Proof | 29755031557 | failure | `4d42a8e7459b` | 2026-07-20T15:30:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29755031557 |
| System3 Workflow Failure Tracker | 29755373439 | failure | `43471cb2e517` | 2026-07-20T15:29:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29755373439 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29755731008 | in_progress | 2026-07-20T15:34:41Z |
| Dashboard Visible Issue Tracker | 29755499042 | pending | 2026-07-20T15:30:50Z |
| Dashboard Visible Auth-Resilient Proof | 29755282979 | in_progress | 2026-07-20T15:28:00Z |

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
