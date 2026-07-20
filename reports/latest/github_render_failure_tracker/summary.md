# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T00:32:18.445267Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `11`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29708985551 conclusion=failure commit=e2f14c66f20e
- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=29709315822 conclusion=failure commit=be85b588e2e7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29709020020 conclusion=failure commit=b92243ea8ac8
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29709292119 conclusion=failure commit=2929ce384cc4
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29709301930 conclusion=failure commit=4be8f4dd8368
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29709315844 conclusion=failure commit=be85b588e2e7
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29709301942 conclusion=failure commit=4be8f4dd8368
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29709292110 conclusion=failure commit=2929ce384cc4
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29709292135 conclusion=failure commit=2929ce384cc4
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29708931523 conclusion=failure commit=addb21aa3e0b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29708709036 conclusion=failure commit=3648e83b855e
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
| Dashboard Visible Issue Tracker | 29708985551 | failure | `e2f14c66f20e` | 2026-07-20T00:29:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29708985551 |
| System3 Safe Repair Runner | 29709315822 | failure | `be85b588e2e7` | 2026-07-20T00:27:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29709315822 |
| Dashboard Visible Auth-Resilient Proof | 29709020020 | failure | `b92243ea8ac8` | 2026-07-20T00:26:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29709020020 |
| Dashboard Shell Diagnostic | 29709292119 | failure | `2929ce384cc4` | 2026-07-20T00:20:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29709292119 |
| System3 Autopilot Proof Board | 29709301930 | failure | `4be8f4dd8368` | 2026-07-20T00:18:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29709301930 |
| System3 Experimental Solution Planner | 29709315844 | failure | `be85b588e2e7` | 2026-07-20T00:18:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29709315844 |
| System3 Secure Install Credential Audit | 29709301942 | failure | `4be8f4dd8368` | 2026-07-20T00:18:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29709301942 |
| Dashboard Visual Proof Strict Gate | 29709292110 | failure | `2929ce384cc4` | 2026-07-20T00:17:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29709292110 |
| Dashboard Visual Loading Postflight | 29709292135 | failure | `2929ce384cc4` | 2026-07-20T00:17:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29709292135 |
| Dashboard Visible Settle Proof | 29708931523 | failure | `addb21aa3e0b` | 2026-07-20T00:11:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29708931523 |
| Dashboard Visible Proof Current | 29708709036 | failure | `3648e83b855e` | 2026-07-20T00:07:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29708709036 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Windows Self-Hosted Full Proof | 29708944888 | queued | 2026-07-20T00:05:16Z |

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
