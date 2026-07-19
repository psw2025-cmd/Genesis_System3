# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T15:21:56.472134Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29692135068 conclusion=failure commit=b41a11e0ece9
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29692302167 conclusion=failure commit=4ed527c558ba
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29692315545 conclusion=failure commit=26dc645fb9cf
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29692337998 conclusion=failure commit=18857011b71a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29692123622 conclusion=failure commit=b41a11e0ece9
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29692315553 conclusion=failure commit=26dc645fb9cf
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29692302186 conclusion=failure commit=4ed527c558ba
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29692302212 conclusion=failure commit=4ed527c558ba
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29691870520 conclusion=failure commit=c2d350792a6f
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
| System3 Windows Self-Hosted Full Proof | 29692135068 | failure | `b41a11e0ece9` | 2026-07-19T15:14:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29692135068 |
| Dashboard Shell Diagnostic | 29692302167 | failure | `4ed527c558ba` | 2026-07-19T15:13:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29692302167 |
| System3 Autopilot Proof Board | 29692315545 | failure | `26dc645fb9cf` | 2026-07-19T15:11:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29692315545 |
| System3 Experimental Solution Planner | 29692337998 | failure | `18857011b71a` | 2026-07-19T15:11:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29692337998 |
| Dashboard Visible Settle Proof | 29692123622 | failure | `b41a11e0ece9` | 2026-07-19T15:11:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29692123622 |
| System3 Secure Install Credential Audit | 29692315553 | failure | `26dc645fb9cf` | 2026-07-19T15:11:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29692315553 |
| Dashboard Visual Loading Postflight | 29692302186 | failure | `4ed527c558ba` | 2026-07-19T15:10:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29692302186 |
| Dashboard Visual Proof Strict Gate | 29692302212 | failure | `4ed527c558ba` | 2026-07-19T15:10:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29692302212 |
| Dashboard Visible Proof Current | 29691870520 | failure | `c2d350792a6f` | 2026-07-19T15:10:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29691870520 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29692580213 | in_progress | 2026-07-19T15:19:14Z |
| Dashboard Visible Issue Tracker | 29692311022 | in_progress | 2026-07-19T15:11:23Z |
| Dashboard Visible Auth-Resilient Proof | 29692244305 | in_progress | 2026-07-19T15:08:52Z |

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
