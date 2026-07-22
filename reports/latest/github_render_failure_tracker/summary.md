# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T18:26:35.576589Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `14`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `26`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29945914408 conclusion=failure commit=37ad0779fcc7
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29945635573 conclusion=failure commit=45f55241be06
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29945583767 conclusion=failure commit=45f55241be06
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29945946355 conclusion=failure commit=ab614221a4ea
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29945987055 conclusion=failure commit=62e1bed7ba5a
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29945946005 conclusion=failure commit=ab614221a4ea
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29945914337 conclusion=failure commit=37ad0779fcc7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29945914376 conclusion=failure commit=37ad0779fcc7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=29943611276 conclusion=cancelled commit=736f04f4f46b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29945064120 conclusion=failure commit=06c610f8bf30
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29943867788 conclusion=failure commit=2d1f042e10a4
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29943779288 conclusion=failure commit=2d1f042e10a4
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=29943656099 conclusion=failure commit=736f04f4f46b
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=29943624567 conclusion=failure commit=736f04f4f46b
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
| Dashboard Shell Diagnostic | 29945914408 | failure | `37ad0779fcc7` | 2026-07-22T18:21:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29945914408 |
| System3 Windows Self-Hosted Full Proof | 29945635573 | failure | `45f55241be06` | 2026-07-22T18:19:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29945635573 |
| Dashboard Visible Settle Proof | 29945583767 | failure | `45f55241be06` | 2026-07-22T18:17:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29945583767 |
| System3 Autopilot Proof Board | 29945946355 | failure | `ab614221a4ea` | 2026-07-22T18:17:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29945946355 |
| System3 Experimental Solution Planner | 29945987055 | failure | `62e1bed7ba5a` | 2026-07-22T18:17:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29945987055 |
| System3 Secure Install Credential Audit | 29945946005 | failure | `ab614221a4ea` | 2026-07-22T18:16:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29945946005 |
| Dashboard Visual Loading Postflight | 29945914337 | failure | `37ad0779fcc7` | 2026-07-22T18:16:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29945914337 |
| Dashboard Visual Proof Strict Gate | 29945914376 | failure | `37ad0779fcc7` | 2026-07-22T18:16:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29945914376 |
| Dashboard Visual Production Proof | 29943611276 | cancelled | `736f04f4f46b` | 2026-07-22T18:14:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29943611276 |
| Dashboard Visible Proof Current | 29945064120 | failure | `06c610f8bf30` | 2026-07-22T18:10:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29945064120 |
| Dashboard Visible Proof Warmed | 29943867788 | failure | `2d1f042e10a4` | 2026-07-22T17:48:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29943867788 |
| System3 Backend Live Simulation Proof | 29943779288 | failure | `2d1f042e10a4` | 2026-07-22T17:46:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29943779288 |
| System3 Render Worker Preflight | 29943656099 | failure | `736f04f4f46b` | 2026-07-22T17:45:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29943656099 |
| Dashboard Deploy Provenance Gate | 29943624567 | failure | `736f04f4f46b` | 2026-07-22T17:44:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29943624567 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29945921471 | in_progress | 2026-07-22T18:25:27Z |
| System3 Safe Repair Runner | 29946330278 | in_progress | 2026-07-22T18:22:27Z |
| Dashboard Visible Auth-Resilient Proof | 29945908090 | in_progress | 2026-07-22T18:15:53Z |

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
