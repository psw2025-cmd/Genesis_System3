# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-21T19:31:06.083794Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29861502215 conclusion=failure commit=1533ca4a3d84
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29861600030 conclusion=failure commit=0d9e440b38c6
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29861541762 conclusion=failure commit=d533351fc894
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29861532558 conclusion=failure commit=d533351fc894
- [ ] Fix latest GitHub workflow 'Dashboard Visual Settle Normalizer' run=29861502264 conclusion=failure commit=1533ca4a3d84
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29861502251 conclusion=failure commit=1533ca4a3d84
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29861502280 conclusion=failure commit=1533ca4a3d84
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29860586512 conclusion=failure commit=dbce6aa53c24
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29860525799 conclusion=failure commit=7a8d50cf82f7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29858753882 conclusion=failure commit=32aef9d3367f
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
| Dashboard Shell Diagnostic | 29861502215 | failure | `1533ca4a3d84` | 2026-07-21T19:29:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29861502215 |
| System3 Experimental Solution Planner | 29861600030 | failure | `0d9e440b38c6` | 2026-07-21T19:27:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29861600030 |
| System3 Autopilot Proof Board | 29861541762 | failure | `d533351fc894` | 2026-07-21T19:27:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29861541762 |
| System3 Secure Install Credential Audit | 29861532558 | failure | `d533351fc894` | 2026-07-21T19:27:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29861532558 |
| Dashboard Visual Settle Normalizer | 29861502264 | failure | `1533ca4a3d84` | 2026-07-21T19:26:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29861502264 |
| Dashboard Visual Loading Postflight | 29861502251 | failure | `1533ca4a3d84` | 2026-07-21T19:26:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29861502251 |
| Dashboard Visual Proof Strict Gate | 29861502280 | failure | `1533ca4a3d84` | 2026-07-21T19:26:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29861502280 |
| System3 Windows Self-Hosted Full Proof | 29860586512 | failure | `dbce6aa53c24` | 2026-07-21T19:19:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29860586512 |
| Dashboard Visible Settle Proof | 29860525799 | failure | `7a8d50cf82f7` | 2026-07-21T19:18:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29860525799 |
| Dashboard Visible Proof Warmed | 29858753882 | failure | `32aef9d3367f` | 2026-07-21T18:48:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29858753882 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29861630797 | in_progress | 2026-07-21T19:28:18Z |
| Dashboard Visible Issue Tracker | 29860741655 | in_progress | 2026-07-21T19:26:12Z |
| Dashboard Visible Auth-Resilient Proof | 29860960407 | in_progress | 2026-07-21T19:18:37Z |

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
