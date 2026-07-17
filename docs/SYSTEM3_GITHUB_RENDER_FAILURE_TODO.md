# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-17T22:16:38.483819Z`
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

- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29617341677 conclusion=failure commit=f72ed8eb6cb3
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29617300829 conclusion=failure commit=1a47bb934e1c
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29617299482 conclusion=failure commit=1a47bb934e1c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29617282060 conclusion=failure commit=78c26814b964
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29617282197 conclusion=failure commit=78c26814b964
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29616688290 conclusion=failure commit=07612bb86510
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29616672888 conclusion=failure commit=c9516d7d9f7b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29616253931 conclusion=failure commit=d1b47bc511a1
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
| System3 Experimental Solution Planner | 29617341677 | failure | `f72ed8eb6cb3` | 2026-07-17T22:15:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29617341677 |
| System3 Autopilot Proof Board | 29617300829 | failure | `1a47bb934e1c` | 2026-07-17T22:15:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29617300829 |
| System3 Secure Install Credential Audit | 29617299482 | failure | `1a47bb934e1c` | 2026-07-17T22:15:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29617299482 |
| Dashboard Visual Loading Postflight | 29617282060 | failure | `78c26814b964` | 2026-07-17T22:14:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29617282060 |
| Dashboard Visual Proof Strict Gate | 29617282197 | failure | `78c26814b964` | 2026-07-17T22:14:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29617282197 |
| System3 Windows Self-Hosted Full Proof | 29616688290 | failure | `07612bb86510` | 2026-07-17T22:09:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29616688290 |
| Dashboard Visible Settle Proof | 29616672888 | failure | `c9516d7d9f7b` | 2026-07-17T22:09:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29616672888 |
| Dashboard Visible Proof Current | 29616253931 | failure | `d1b47bc511a1` | 2026-07-17T22:07:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29616253931 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29617341655 | in_progress | 2026-07-17T22:16:21Z |
| Dashboard Shell Diagnostic | 29617282039 | in_progress | 2026-07-17T22:14:45Z |
| Dashboard Visible Issue Tracker | 29616717898 | in_progress | 2026-07-17T22:14:42Z |
| Dashboard Visible Auth-Resilient Proof | 29616819772 | in_progress | 2026-07-17T22:05:47Z |

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
