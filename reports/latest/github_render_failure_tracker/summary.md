# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T13:30:41.040278Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29645600279 conclusion=failure commit=4cc74a873d81
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29645697950 conclusion=failure commit=500f591c56a7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29645586700 conclusion=failure commit=4cc74a873d81
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29645718429 conclusion=failure commit=36e1e6f86b41
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29645697942 conclusion=failure commit=500f591c56a7
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29645671457 conclusion=failure commit=8c38b24de94e
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29645698078 conclusion=failure commit=500f591c56a7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29645697932 conclusion=failure commit=500f591c56a7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29645247584 conclusion=failure commit=c57400dc38d0
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
| System3 Windows Self-Hosted Full Proof | 29645600279 | failure | `4cc74a873d81` | 2026-07-18T13:15:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29645600279 |
| Dashboard Shell Diagnostic | 29645697950 | failure | `500f591c56a7` | 2026-07-18T13:14:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29645697950 |
| Dashboard Visible Settle Proof | 29645586700 | failure | `4cc74a873d81` | 2026-07-18T13:14:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29645586700 |
| Dashboard Visual Proof Strict Gate | 29645718429 | failure | `36e1e6f86b41` | 2026-07-18T13:12:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29645718429 |
| System3 Secure Install Credential Audit | 29645697942 | failure | `500f591c56a7` | 2026-07-18T13:11:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29645697942 |
| System3 Autopilot Proof Board | 29645671457 | failure | `8c38b24de94e` | 2026-07-18T13:11:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29645671457 |
| System3 Experimental Solution Planner | 29645698078 | failure | `500f591c56a7` | 2026-07-18T13:11:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29645698078 |
| Dashboard Visual Loading Postflight | 29645697932 | failure | `500f591c56a7` | 2026-07-18T13:11:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29645697932 |
| Dashboard Visible Proof Current | 29645247584 | failure | `c57400dc38d0` | 2026-07-18T13:09:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29645247584 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29646184715 | in_progress | 2026-07-18T13:27:48Z |
| Dashboard Visible Issue Tracker | 29645698059 | in_progress | 2026-07-18T13:22:00Z |
| Dashboard Visible Auth-Resilient Proof | 29645733485 | in_progress | 2026-07-18T13:12:47Z |

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
