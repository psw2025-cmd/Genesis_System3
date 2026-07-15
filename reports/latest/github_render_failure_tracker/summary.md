# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-15T16:31:36.906883Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `5`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29432724605 conclusion=failure commit=46d65131743e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29432695496 conclusion=failure commit=7c3532da6756
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29432695335 conclusion=failure commit=7c3532da6756
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=29429671634 conclusion=cancelled commit=7a1db2c35378
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29429845850 conclusion=failure commit=94d0d106ba74
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29429799218 conclusion=failure commit=054701e74093
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29429828383 conclusion=failure commit=7be59d25bf01
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29430039918 conclusion=failure commit=fa95cde85898
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29429929820 conclusion=failure commit=de087090133b
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=29429758767 conclusion=failure commit=7a1db2c35378
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=29429730772 conclusion=failure commit=7a1db2c35378
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29429033045 conclusion=failure commit=068985d2822f
- [ ] Fix Render endpoint /: HTTP status 503 status=503
- [ ] Fix Render endpoint /ui/: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/health: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/state: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/paper: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 503 status=503

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Secure Install Credential Audit | 29432724605 | failure | `46d65131743e` | 2026-07-15T16:31:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29432724605 |
| Dashboard Visual Proof Strict Gate | 29432695496 | failure | `7c3532da6756` | 2026-07-15T16:30:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29432695496 |
| Dashboard Visual Loading Postflight | 29432695335 | failure | `7c3532da6756` | 2026-07-15T16:30:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29432695335 |
| Dashboard Visual Production Proof | 29429671634 | cancelled | `7a1db2c35378` | 2026-07-15T16:18:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29429671634 |
| Dashboard Visible Auth-Resilient Proof | 29429845850 | failure | `94d0d106ba74` | 2026-07-15T16:08:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29429845850 |
| Dashboard Visible Settle Proof | 29429799218 | failure | `054701e74093` | 2026-07-15T15:55:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29429799218 |
| System3 Windows Self-Hosted Full Proof | 29429828383 | failure | `7be59d25bf01` | 2026-07-15T15:55:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29429828383 |
| Dashboard Visible Proof Warmed | 29430039918 | failure | `fa95cde85898` | 2026-07-15T15:53:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29430039918 |
| System3 Backend Live Simulation Proof | 29429929820 | failure | `de087090133b` | 2026-07-15T15:51:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29429929820 |
| System3 Render Worker Preflight | 29429758767 | failure | `7a1db2c35378` | 2026-07-15T15:49:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29429758767 |
| Dashboard Deploy Provenance Gate | 29429730772 | failure | `7a1db2c35378` | 2026-07-15T15:49:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29429730772 |
| Dashboard Visible Proof Current | 29429033045 | failure | `068985d2822f` | 2026-07-15T15:45:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29429033045 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Experimental Solution Planner | 29432763919 | in_progress | 2026-07-15T16:31:35Z |
| System3 Safe Repair Runner | 29432764021 | pending | 2026-07-15T16:31:33Z |
| System3 Autopilot Proof Board | 29432724578 | in_progress | 2026-07-15T16:31:03Z |
| Dashboard Shell Diagnostic | 29432695356 | in_progress | 2026-07-15T16:30:39Z |
| Dashboard Visible Issue Tracker | 29431966118 | in_progress | 2026-07-15T16:30:34Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 503 | HTTP status 503 | `none` |
| `/ui/` | 503 | HTTP status 503 | `none` |
| `/api/health` | 503 | HTTP status 503 | `none` |
| `/api/state` | 503 | HTTP status 503 | `none` |
| `/api/deploy/info` | 503 | HTTP status 503 | `none` |
| `/api/broker/diagnose` | 503 | HTTP status 503 | `none` |
| `/api/broker/funds` | 503 | HTTP status 503 | `none` |
| `/api/broker/holdings` | 503 | HTTP status 503 | `none` |
| `/api/broker/positions/live` | 503 | HTTP status 503 | `none` |
| `/api/scanner/top_contract_gainers` | 503 | HTTP status 503 | `none` |
| `/api/paper` | 503 | HTTP status 503 | `none` |
| `/api/ml/performance` | 503 | HTTP status 503 | `none` |
