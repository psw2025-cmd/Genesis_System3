# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-16T17:30:36.027532Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `14`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `12`
TODO count: `26`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29518909967 conclusion=failure commit=ed70cf20abff
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29518878023 conclusion=failure commit=ed70cf20abff
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29519089158 conclusion=failure commit=faa5538b3fae
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29519124544 conclusion=failure commit=c9f276c0b7e8
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29519175290 conclusion=failure commit=63da42f8b14c
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29519120742 conclusion=failure commit=620923889d2f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29519090429 conclusion=failure commit=faa5538b3fae
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29519089605 conclusion=failure commit=faa5538b3fae
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=29516850169 conclusion=cancelled commit=cfa6f9012722
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29517095223 conclusion=failure commit=209300a1c52c
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29517018419 conclusion=failure commit=209300a1c52c
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=29516907082 conclusion=failure commit=cfa6f9012722
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=29516873416 conclusion=failure commit=cfa6f9012722
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29516339318 conclusion=failure commit=e05184d4248c
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
| System3 Windows Self-Hosted Full Proof | 29518909967 | failure | `ed70cf20abff` | 2026-07-16T17:19:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29518909967 |
| Dashboard Visible Settle Proof | 29518878023 | failure | `ed70cf20abff` | 2026-07-16T17:19:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29518878023 |
| Dashboard Shell Diagnostic | 29519089158 | failure | `faa5538b3fae` | 2026-07-16T17:19:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29519089158 |
| System3 Autopilot Proof Board | 29519124544 | failure | `c9f276c0b7e8` | 2026-07-16T17:17:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29519124544 |
| System3 Experimental Solution Planner | 29519175290 | failure | `63da42f8b14c` | 2026-07-16T17:17:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29519175290 |
| System3 Secure Install Credential Audit | 29519120742 | failure | `620923889d2f` | 2026-07-16T17:17:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29519120742 |
| Dashboard Visual Loading Postflight | 29519090429 | failure | `faa5538b3fae` | 2026-07-16T17:16:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29519090429 |
| Dashboard Visual Proof Strict Gate | 29519089605 | failure | `faa5538b3fae` | 2026-07-16T17:16:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29519089605 |
| Dashboard Visual Production Proof | 29516850169 | cancelled | `cfa6f9012722` | 2026-07-16T17:14:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29516850169 |
| Dashboard Visible Proof Warmed | 29517095223 | failure | `209300a1c52c` | 2026-07-16T16:48:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29517095223 |
| System3 Backend Live Simulation Proof | 29517018419 | failure | `209300a1c52c` | 2026-07-16T16:47:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29517018419 |
| System3 Render Worker Preflight | 29516907082 | failure | `cfa6f9012722` | 2026-07-16T16:45:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29516907082 |
| Dashboard Deploy Provenance Gate | 29516873416 | failure | `cfa6f9012722` | 2026-07-16T16:45:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29516873416 |
| Dashboard Visible Proof Current | 29516339318 | failure | `e05184d4248c` | 2026-07-16T16:43:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29516339318 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Workflow Failure Tracker | 29520053856 | queued | 2026-07-16T17:30:34Z |
| System3 Safe Repair Runner | 29519838622 | in_progress | 2026-07-16T17:27:31Z |
| Dashboard Visible Issue Tracker | 29519095016 | in_progress | 2026-07-16T17:19:31Z |
| Dashboard Visible Auth-Resilient Proof | 29519228498 | in_progress | 2026-07-16T17:18:30Z |

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
