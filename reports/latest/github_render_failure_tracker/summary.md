# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T14:46:03.383234Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30015661542 conclusion=failure commit=2764878f8d03
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30016229406 conclusion=failure commit=c13e1efe5070
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30016173304 conclusion=failure commit=d207211aa060
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30016230668 conclusion=failure commit=c13e1efe5070
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30016230742 conclusion=failure commit=c13e1efe5070
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30016229538 conclusion=failure commit=c13e1efe5070
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30016229481 conclusion=failure commit=c13e1efe5070
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30013902328 conclusion=failure commit=c01fb1deb930
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30013715372 conclusion=failure commit=c01fb1deb930
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
| Dashboard Visible Proof Current | 30015661542 | failure | `2764878f8d03` | 2026-07-23T14:42:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30015661542 |
| Dashboard Shell Diagnostic | 30016229406 | failure | `c13e1efe5070` | 2026-07-23T14:36:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30016229406 |
| System3 Autopilot Proof Board | 30016173304 | failure | `d207211aa060` | 2026-07-23T14:31:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30016173304 |
| System3 Secure Install Credential Audit | 30016230668 | failure | `c13e1efe5070` | 2026-07-23T14:31:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30016230668 |
| System3 Experimental Solution Planner | 30016230742 | failure | `c13e1efe5070` | 2026-07-23T14:31:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30016230742 |
| Dashboard Visual Loading Postflight | 30016229538 | failure | `c13e1efe5070` | 2026-07-23T14:31:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30016229538 |
| Dashboard Visual Proof Strict Gate | 30016229481 | failure | `c13e1efe5070` | 2026-07-23T14:31:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30016229481 |
| Dashboard Visible Proof Warmed | 30013902328 | failure | `c01fb1deb930` | 2026-07-23T14:02:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30013902328 |
| System3 Backend Live Simulation Proof | 30013715372 | failure | `c01fb1deb930` | 2026-07-23T13:59:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30013715372 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 30017081791 | in_progress | 2026-07-23T14:42:43Z |
| Dashboard Visible Issue Tracker | 30016230588 | in_progress | 2026-07-23T14:42:13Z |

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
