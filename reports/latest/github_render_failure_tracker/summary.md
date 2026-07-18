# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T07:32:59.061566Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29635754479 conclusion=failure commit=4702879e01c0
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29635769777 conclusion=failure commit=d96cee796219
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29635783794 conclusion=failure commit=0c60556f92a2
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29635767712 conclusion=failure commit=d96cee796219
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29635754464 conclusion=failure commit=4702879e01c0
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29635754485 conclusion=failure commit=4702879e01c0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29635348073 conclusion=failure commit=a042b3405811
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29635465601 conclusion=failure commit=28f36d557d32
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29635475672 conclusion=failure commit=28f36d557d32
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29635007629 conclusion=failure commit=15cfa37ee2cf
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29634958450 conclusion=failure commit=15cfa37ee2cf
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=29634867449 conclusion=failure commit=fa2004079f58
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
| Dashboard Shell Diagnostic | 29635754479 | failure | `4702879e01c0` | 2026-07-18T07:30:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29635754479 |
| System3 Autopilot Proof Board | 29635769777 | failure | `d96cee796219` | 2026-07-18T07:28:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29635769777 |
| System3 Experimental Solution Planner | 29635783794 | failure | `0c60556f92a2` | 2026-07-18T07:28:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29635783794 |
| System3 Secure Install Credential Audit | 29635767712 | failure | `d96cee796219` | 2026-07-18T07:27:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29635767712 |
| Dashboard Visual Proof Strict Gate | 29635754464 | failure | `4702879e01c0` | 2026-07-18T07:27:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29635754464 |
| Dashboard Visual Loading Postflight | 29635754485 | failure | `4702879e01c0` | 2026-07-18T07:27:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29635754485 |
| Dashboard Visible Proof Current | 29635348073 | failure | `a042b3405811` | 2026-07-18T07:24:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29635348073 |
| Dashboard Visible Settle Proof | 29635465601 | failure | `28f36d557d32` | 2026-07-18T07:22:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29635465601 |
| System3 Windows Self-Hosted Full Proof | 29635475672 | failure | `28f36d557d32` | 2026-07-18T07:22:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29635475672 |
| Dashboard Visible Proof Warmed | 29635007629 | failure | `15cfa37ee2cf` | 2026-07-18T07:01:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29635007629 |
| System3 Backend Live Simulation Proof | 29634958450 | failure | `15cfa37ee2cf` | 2026-07-18T07:00:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29634958450 |
| Dashboard Deploy Provenance Gate | 29634867449 | failure | `fa2004079f58` | 2026-07-18T06:56:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29634867449 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29635852944 | in_progress | 2026-07-18T07:31:04Z |
| Dashboard Visible Issue Tracker | 29635765663 | pending | 2026-07-18T07:27:26Z |
| Dashboard Visible Auth-Resilient Proof | 29635537763 | in_progress | 2026-07-18T07:19:31Z |

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
