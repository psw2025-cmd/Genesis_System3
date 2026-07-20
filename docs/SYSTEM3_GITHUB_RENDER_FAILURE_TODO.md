# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T17:38:34.384828Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `8`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `20`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29763074490 conclusion=failure commit=da4d236b68ba
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29763236062 conclusion=failure commit=b3bd5289caab
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29762386974 conclusion=failure commit=e170a629dfde
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29762700774 conclusion=failure commit=e786f7df9cda
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29763114212 conclusion=failure commit=3b43148d6ef6
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29763129486 conclusion=failure commit=9ac5023fbb9d
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29763074690 conclusion=failure commit=da4d236b68ba
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29763074622 conclusion=failure commit=da4d236b68ba
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
| Dashboard Shell Diagnostic | 29763074490 | failure | `da4d236b68ba` | 2026-07-20T17:20:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29763074490 |
| System3 Autopilot Proof Board | 29763236062 | failure | `b3bd5289caab` | 2026-07-20T17:20:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29763236062 |
| Dashboard Visible Proof Current | 29762386974 | failure | `e170a629dfde` | 2026-07-20T17:18:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29762386974 |
| System3 Windows Self-Hosted Full Proof | 29762700774 | failure | `e786f7df9cda` | 2026-07-20T17:18:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29762700774 |
| System3 Secure Install Credential Audit | 29763114212 | failure | `3b43148d6ef6` | 2026-07-20T17:18:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29763114212 |
| System3 Experimental Solution Planner | 29763129486 | failure | `9ac5023fbb9d` | 2026-07-20T17:18:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29763129486 |
| Dashboard Visual Loading Postflight | 29763074690 | failure | `da4d236b68ba` | 2026-07-20T17:17:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29763074690 |
| Dashboard Visual Proof Strict Gate | 29763074622 | failure | `da4d236b68ba` | 2026-07-20T17:17:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29763074622 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29764253428 | in_progress | 2026-07-20T17:35:50Z |
| Dashboard Visible Issue Tracker | 29763091691 | in_progress | 2026-07-20T17:26:07Z |

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
