# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T17:22:06.174550Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `11`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29696476998 conclusion=failure commit=b6012cf03e69
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29696487775 conclusion=failure commit=501f7d8bace7
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29696508919 conclusion=failure commit=7d80bcdb7e57
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29696172854 conclusion=failure commit=0939409194cb
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29696487591 conclusion=failure commit=501f7d8bace7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Settle Normalizer' run=29696477020 conclusion=failure commit=b6012cf03e69
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29696476991 conclusion=failure commit=b6012cf03e69
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29696477016 conclusion=failure commit=b6012cf03e69
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29696154820 conclusion=failure commit=0939409194cb
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=29696074687 conclusion=failure commit=afcaafedd569
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29695830780 conclusion=failure commit=532c85d81e49
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
| Dashboard Shell Diagnostic | 29696476998 | failure | `b6012cf03e69` | 2026-07-19T17:18:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29696476998 |
| System3 Autopilot Proof Board | 29696487775 | failure | `501f7d8bace7` | 2026-07-19T17:16:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29696487775 |
| System3 Experimental Solution Planner | 29696508919 | failure | `7d80bcdb7e57` | 2026-07-19T17:16:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29696508919 |
| System3 Windows Self-Hosted Full Proof | 29696172854 | failure | `0939409194cb` | 2026-07-19T17:16:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29696172854 |
| System3 Secure Install Credential Audit | 29696487591 | failure | `501f7d8bace7` | 2026-07-19T17:16:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29696487591 |
| Dashboard Visual Settle Normalizer | 29696477020 | failure | `b6012cf03e69` | 2026-07-19T17:15:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29696477020 |
| Dashboard Visual Loading Postflight | 29696476991 | failure | `b6012cf03e69` | 2026-07-19T17:15:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29696476991 |
| Dashboard Visual Proof Strict Gate | 29696477016 | failure | `b6012cf03e69` | 2026-07-19T17:15:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29696477016 |
| Dashboard Visible Settle Proof | 29696154820 | failure | `0939409194cb` | 2026-07-19T17:12:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29696154820 |
| System3 Workflow Failure Tracker | 29696074687 | failure | `afcaafedd569` | 2026-07-19T17:03:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29696074687 |
| Dashboard Visible Proof Current | 29695830780 | failure | `532c85d81e49` | 2026-07-19T17:02:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29695830780 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29696590160 | in_progress | 2026-07-19T17:19:53Z |
| Dashboard Visible Issue Tracker | 29696116649 | in_progress | 2026-07-19T17:15:40Z |
| Dashboard Visible Auth-Resilient Proof | 29696282259 | in_progress | 2026-07-19T17:10:00Z |

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
