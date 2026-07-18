# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T22:17:11.674191Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29662731688 conclusion=failure commit=220d720089ab
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29662721647 conclusion=failure commit=bbb8d136cc36
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29662767993 conclusion=failure commit=778f672c296c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29662810320 conclusion=failure commit=8d378c3b85e2
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29662779041 conclusion=failure commit=947bb26f8a29
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29662794569 conclusion=failure commit=2ba836e74c3b
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29662779053 conclusion=failure commit=947bb26f8a29
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29662767967 conclusion=failure commit=778f672c296c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29662470059 conclusion=failure commit=c8216440126c
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
| System3 Windows Self-Hosted Full Proof | 29662731688 | failure | `220d720089ab` | 2026-07-18T22:10:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29662731688 |
| Dashboard Visible Settle Proof | 29662721647 | failure | `bbb8d136cc36` | 2026-07-18T22:08:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29662721647 |
| Dashboard Shell Diagnostic | 29662767993 | failure | `778f672c296c` | 2026-07-18T22:07:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29662767993 |
| Dashboard Visual Proof Strict Gate | 29662810320 | failure | `8d378c3b85e2` | 2026-07-18T22:05:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29662810320 |
| System3 Autopilot Proof Board | 29662779041 | failure | `947bb26f8a29` | 2026-07-18T22:05:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29662779041 |
| System3 Experimental Solution Planner | 29662794569 | failure | `2ba836e74c3b` | 2026-07-18T22:05:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29662794569 |
| System3 Secure Install Credential Audit | 29662779053 | failure | `947bb26f8a29` | 2026-07-18T22:04:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29662779053 |
| Dashboard Visual Loading Postflight | 29662767967 | failure | `778f672c296c` | 2026-07-18T22:04:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29662767967 |
| Dashboard Visible Proof Current | 29662470059 | failure | `c8216440126c` | 2026-07-18T22:01:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29662470059 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29663083533 | in_progress | 2026-07-18T22:15:08Z |
| Dashboard Visible Issue Tracker | 29662769852 | in_progress | 2026-07-18T22:11:01Z |
| Dashboard Visible Auth-Resilient Proof | 29662829014 | in_progress | 2026-07-18T22:06:11Z |

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
