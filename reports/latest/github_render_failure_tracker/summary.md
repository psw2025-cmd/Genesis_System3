# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T10:31:17.876653Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29683309140 conclusion=failure commit=81e7afac487f
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29683321679 conclusion=failure commit=aa974501738f
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29683339314 conclusion=failure commit=fd4ba92d7cfe
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29683321687 conclusion=failure commit=aa974501738f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29683309144 conclusion=failure commit=81e7afac487f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29683309183 conclusion=failure commit=81e7afac487f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29682452715 conclusion=failure commit=16408d741928
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29682530593 conclusion=failure commit=16408d741928
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29682502975 conclusion=failure commit=16408d741928
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
| Dashboard Shell Diagnostic | 29683309140 | failure | `81e7afac487f` | 2026-07-19T10:28:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29683309140 |
| System3 Autopilot Proof Board | 29683321679 | failure | `aa974501738f` | 2026-07-19T10:26:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29683321679 |
| System3 Experimental Solution Planner | 29683339314 | failure | `fd4ba92d7cfe` | 2026-07-19T10:26:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29683339314 |
| System3 Secure Install Credential Audit | 29683321687 | failure | `aa974501738f` | 2026-07-19T10:26:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29683321687 |
| Dashboard Visual Proof Strict Gate | 29683309144 | failure | `81e7afac487f` | 2026-07-19T10:25:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29683309144 |
| Dashboard Visual Loading Postflight | 29683309183 | failure | `81e7afac487f` | 2026-07-19T10:25:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29683309183 |
| Dashboard Visible Auth-Resilient Proof | 29682452715 | failure | `16408d741928` | 2026-07-19T10:14:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29682452715 |
| Dashboard Visible Proof Warmed | 29682530593 | failure | `16408d741928` | 2026-07-19T10:00:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29682530593 |
| System3 Backend Live Simulation Proof | 29682502975 | failure | `16408d741928` | 2026-07-19T09:58:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29682502975 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29683406268 | in_progress | 2026-07-19T10:30:23Z |
| Dashboard Visible Issue Tracker | 29683310495 | in_progress | 2026-07-19T10:28:57Z |

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
