# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T21:25:01.346859Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29957992153 conclusion=failure commit=147ef53ffd29
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29958320868 conclusion=failure commit=82656aa1f597
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29957999626 conclusion=failure commit=147ef53ffd29
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29958362354 conclusion=failure commit=1a3608ed81d5
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29958302787 conclusion=failure commit=82656aa1f597
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29958320619 conclusion=failure commit=82656aa1f597
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29958321025 conclusion=failure commit=82656aa1f597
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29958321112 conclusion=failure commit=82656aa1f597
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29957240607 conclusion=failure commit=ba74ee9f6825
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
| System3 Windows Self-Hosted Full Proof | 29957992153 | failure | `147ef53ffd29` | 2026-07-22T21:16:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29957992153 |
| Dashboard Shell Diagnostic | 29958320868 | failure | `82656aa1f597` | 2026-07-22T21:16:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29958320868 |
| Dashboard Visible Settle Proof | 29957999626 | failure | `147ef53ffd29` | 2026-07-22T21:14:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29957999626 |
| System3 Experimental Solution Planner | 29958362354 | failure | `1a3608ed81d5` | 2026-07-22T21:13:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29958362354 |
| System3 Autopilot Proof Board | 29958302787 | failure | `82656aa1f597` | 2026-07-22T21:13:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29958302787 |
| System3 Secure Install Credential Audit | 29958320619 | failure | `82656aa1f597` | 2026-07-22T21:13:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29958320619 |
| Dashboard Visual Loading Postflight | 29958321025 | failure | `82656aa1f597` | 2026-07-22T21:13:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29958321025 |
| Dashboard Visual Proof Strict Gate | 29958321112 | failure | `82656aa1f597` | 2026-07-22T21:13:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29958321112 |
| Dashboard Visible Proof Current | 29957240607 | failure | `ba74ee9f6825` | 2026-07-22T21:09:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29957240607 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29958362424 | in_progress | 2026-07-22T21:23:25Z |
| System3 Safe Repair Runner | 29958912567 | in_progress | 2026-07-22T21:22:10Z |
| Dashboard Visible Auth-Resilient Proof | 29958275178 | in_progress | 2026-07-22T21:12:17Z |

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
