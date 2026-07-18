# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T15:20:55.109575Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `8`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `12`
TODO count: `20`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29649759711 conclusion=failure commit=a4cf2c2ef1d4
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29649781895 conclusion=failure commit=160709cb28cc
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29649759706 conclusion=failure commit=a4cf2c2ef1d4
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29649746280 conclusion=failure commit=d38a6df60535
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29649746274 conclusion=failure commit=d38a6df60535
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29649289969 conclusion=failure commit=529670fa091c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29649276711 conclusion=failure commit=529670fa091c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29648950555 conclusion=failure commit=258a9ce6a826
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
| System3 Autopilot Proof Board | 29649759711 | failure | `a4cf2c2ef1d4` | 2026-07-18T15:20:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29649759711 |
| System3 Experimental Solution Planner | 29649781895 | failure | `160709cb28cc` | 2026-07-18T15:20:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29649781895 |
| System3 Secure Install Credential Audit | 29649759706 | failure | `a4cf2c2ef1d4` | 2026-07-18T15:19:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29649759706 |
| Dashboard Visual Proof Strict Gate | 29649746280 | failure | `d38a6df60535` | 2026-07-18T15:19:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29649746280 |
| Dashboard Visual Loading Postflight | 29649746274 | failure | `d38a6df60535` | 2026-07-18T15:19:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29649746274 |
| System3 Windows Self-Hosted Full Proof | 29649289969 | failure | `529670fa091c` | 2026-07-18T15:12:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29649289969 |
| Dashboard Visible Settle Proof | 29649276711 | failure | `529670fa091c` | 2026-07-18T15:11:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29649276711 |
| Dashboard Visible Proof Current | 29648950555 | failure | `258a9ce6a826` | 2026-07-18T15:07:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29648950555 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29649781861 | in_progress | 2026-07-18T15:20:32Z |
| Dashboard Shell Diagnostic | 29649746263 | in_progress | 2026-07-18T15:19:17Z |
| Dashboard Visible Issue Tracker | 29649401128 | in_progress | 2026-07-18T15:19:15Z |
| Dashboard Visible Auth-Resilient Proof | 29649405955 | in_progress | 2026-07-18T15:08:50Z |

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
