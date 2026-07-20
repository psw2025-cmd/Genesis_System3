# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T23:21:54.736425Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29786528808 conclusion=failure commit=067af116ac52
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29786496524 conclusion=failure commit=09a658ccd0e2
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29786528832 conclusion=failure commit=067af116ac52
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29786529596 conclusion=failure commit=067af116ac52
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29786528785 conclusion=failure commit=067af116ac52
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29786528795 conclusion=failure commit=067af116ac52
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29786150122 conclusion=failure commit=00878487a53e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29786121066 conclusion=failure commit=96cdc69ff792
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29785595424 conclusion=failure commit=b4879835f7ab
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
| Dashboard Shell Diagnostic | 29786528808 | failure | `067af116ac52` | 2026-07-20T23:16:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29786528808 |
| System3 Autopilot Proof Board | 29786496524 | failure | `09a658ccd0e2` | 2026-07-20T23:13:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29786496524 |
| System3 Secure Install Credential Audit | 29786528832 | failure | `067af116ac52` | 2026-07-20T23:13:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29786528832 |
| System3 Experimental Solution Planner | 29786529596 | failure | `067af116ac52` | 2026-07-20T23:13:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29786529596 |
| Dashboard Visual Proof Strict Gate | 29786528785 | failure | `067af116ac52` | 2026-07-20T23:13:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29786528785 |
| Dashboard Visual Loading Postflight | 29786528795 | failure | `067af116ac52` | 2026-07-20T23:13:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29786528795 |
| System3 Windows Self-Hosted Full Proof | 29786150122 | failure | `00878487a53e` | 2026-07-20T23:12:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29786150122 |
| Dashboard Visible Settle Proof | 29786121066 | failure | `96cdc69ff792` | 2026-07-20T23:12:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29786121066 |
| Dashboard Visible Proof Current | 29785595424 | failure | `b4879835f7ab` | 2026-07-20T23:08:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29785595424 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29786803064 | in_progress | 2026-07-20T23:19:18Z |
| Dashboard Visible Issue Tracker | 29786529626 | pending | 2026-07-20T23:13:33Z |
| Dashboard Visible Auth-Resilient Proof | 29786341888 | in_progress | 2026-07-20T23:10:05Z |

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
