# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T12:43:58.266612Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=29742689526 conclusion=failure commit=61ba46347eb8
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29742689537 conclusion=failure commit=61ba46347eb8
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29742689554 conclusion=failure commit=61ba46347eb8
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29742689484 conclusion=failure commit=61ba46347eb8
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29742689534 conclusion=failure commit=61ba46347eb8
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29742689464 conclusion=failure commit=61ba46347eb8
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29742257351 conclusion=failure commit=4939415f0212
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29742265080 conclusion=failure commit=4939415f0212
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29742020497 conclusion=failure commit=4939415f0212
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29741894542 conclusion=failure commit=bc9e4983bdea
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29741100812 conclusion=failure commit=da5ef780bcd5
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=29740889587 conclusion=failure commit=acd3f10a2d7f
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
| System3 Safe Repair Runner | 29742689526 | failure | `61ba46347eb8` | 2026-07-20T12:42:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29742689526 |
| Dashboard Shell Diagnostic | 29742689537 | failure | `61ba46347eb8` | 2026-07-20T12:36:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29742689537 |
| System3 Secure Install Credential Audit | 29742689554 | failure | `61ba46347eb8` | 2026-07-20T12:34:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29742689554 |
| System3 Experimental Solution Planner | 29742689484 | failure | `61ba46347eb8` | 2026-07-20T12:34:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29742689484 |
| Dashboard Visual Loading Postflight | 29742689534 | failure | `61ba46347eb8` | 2026-07-20T12:34:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29742689534 |
| Dashboard Visual Proof Strict Gate | 29742689464 | failure | `61ba46347eb8` | 2026-07-20T12:34:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29742689464 |
| Dashboard Visible Settle Proof | 29742257351 | failure | `4939415f0212` | 2026-07-20T12:33:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29742257351 |
| System3 Windows Self-Hosted Full Proof | 29742265080 | failure | `4939415f0212` | 2026-07-20T12:32:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29742265080 |
| Dashboard Visible Proof Current | 29742020497 | failure | `4939415f0212` | 2026-07-20T12:29:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29742020497 |
| System3 Autopilot Proof Board | 29741894542 | failure | `bc9e4983bdea` | 2026-07-20T12:22:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29741894542 |
| Dashboard Visible Proof Warmed | 29741100812 | failure | `da5ef780bcd5` | 2026-07-20T12:09:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29741100812 |
| Dashboard Deploy Provenance Gate | 29740889587 | failure | `acd3f10a2d7f` | 2026-07-20T12:06:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29740889587 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29742018743 | in_progress | 2026-07-20T12:33:53Z |
| Dashboard Visible Auth-Resilient Proof | 29742611838 | in_progress | 2026-07-20T12:32:45Z |

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
