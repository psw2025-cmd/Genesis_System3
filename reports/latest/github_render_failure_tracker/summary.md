# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-16T20:19:28.264897Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `13`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `25`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29531048225 conclusion=failure commit=70cbf2025756
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29531084356 conclusion=failure commit=90452fcbb0bd
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29531129024 conclusion=failure commit=61a5d13ba28a
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29530705858 conclusion=failure commit=fb747d092273
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29531084392 conclusion=failure commit=90452fcbb0bd
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29530669055 conclusion=failure commit=fb747d092273
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29531048343 conclusion=failure commit=70cbf2025756
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29531048209 conclusion=failure commit=70cbf2025756
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=29528908467 conclusion=cancelled commit=ba365a8533fc
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29530180005 conclusion=failure commit=ec63a4e8285a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29529143891 conclusion=failure commit=3546db27e1bd
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29529109300 conclusion=failure commit=3546db27e1bd
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=29528942876 conclusion=failure commit=ba365a8533fc
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
| Dashboard Shell Diagnostic | 29531048225 | failure | `70cbf2025756` | 2026-07-16T20:15:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29531048225 |
| System3 Autopilot Proof Board | 29531084356 | failure | `90452fcbb0bd` | 2026-07-16T20:13:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29531084356 |
| System3 Experimental Solution Planner | 29531129024 | failure | `61a5d13ba28a` | 2026-07-16T20:13:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29531129024 |
| System3 Windows Self-Hosted Full Proof | 29530705858 | failure | `fb747d092273` | 2026-07-16T20:13:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29530705858 |
| System3 Secure Install Credential Audit | 29531084392 | failure | `90452fcbb0bd` | 2026-07-16T20:12:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29531084392 |
| Dashboard Visible Settle Proof | 29530669055 | failure | `fb747d092273` | 2026-07-16T20:12:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29530669055 |
| Dashboard Visual Loading Postflight | 29531048343 | failure | `70cbf2025756` | 2026-07-16T20:12:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29531048343 |
| Dashboard Visual Proof Strict Gate | 29531048209 | failure | `70cbf2025756` | 2026-07-16T20:12:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29531048209 |
| Dashboard Visual Production Proof | 29528908467 | cancelled | `ba365a8533fc` | 2026-07-16T20:10:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29528908467 |
| Dashboard Visible Proof Current | 29530180005 | failure | `ec63a4e8285a` | 2026-07-16T20:05:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29530180005 |
| Dashboard Visible Proof Warmed | 29529143891 | failure | `3546db27e1bd` | 2026-07-16T19:44:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29529143891 |
| System3 Backend Live Simulation Proof | 29529109300 | failure | `3546db27e1bd` | 2026-07-16T19:43:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29529109300 |
| Dashboard Deploy Provenance Gate | 29528942876 | failure | `ba365a8533fc` | 2026-07-16T19:41:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29528942876 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29531050769 | queued | 2026-07-16T20:19:27Z |
| System3 Safe Repair Runner | 29531344155 | in_progress | 2026-07-16T20:16:40Z |
| Dashboard Visible Auth-Resilient Proof | 29530875976 | in_progress | 2026-07-16T20:09:24Z |

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
