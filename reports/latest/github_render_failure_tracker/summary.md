# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T17:29:51.779978Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29941763025 conclusion=failure commit=5e1fb0e7348a
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29941790012 conclusion=failure commit=3764bfb40a79
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29941826970 conclusion=failure commit=4f648d66c2e4
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29941789700 conclusion=failure commit=3764bfb40a79
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29941762970 conclusion=failure commit=5e1fb0e7348a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29941763003 conclusion=failure commit=5e1fb0e7348a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29939667629 conclusion=failure commit=f4898609c270
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29939840535 conclusion=failure commit=f4898609c270
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29939752184 conclusion=failure commit=f4898609c270
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
| Dashboard Shell Diagnostic | 29941763025 | failure | `5e1fb0e7348a` | 2026-07-22T17:21:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29941763025 |
| System3 Autopilot Proof Board | 29941790012 | failure | `3764bfb40a79` | 2026-07-22T17:19:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29941790012 |
| System3 Experimental Solution Planner | 29941826970 | failure | `4f648d66c2e4` | 2026-07-22T17:19:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29941826970 |
| System3 Secure Install Credential Audit | 29941789700 | failure | `3764bfb40a79` | 2026-07-22T17:18:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29941789700 |
| Dashboard Visual Loading Postflight | 29941762970 | failure | `5e1fb0e7348a` | 2026-07-22T17:18:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29941762970 |
| Dashboard Visual Proof Strict Gate | 29941763003 | failure | `5e1fb0e7348a` | 2026-07-22T17:18:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29941763003 |
| Dashboard Visible Auth-Resilient Proof | 29939667629 | failure | `f4898609c270` | 2026-07-22T17:07:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29939667629 |
| Dashboard Visible Proof Warmed | 29939840535 | failure | `f4898609c270` | 2026-07-22T16:52:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29939840535 |
| System3 Backend Live Simulation Proof | 29939752184 | failure | `f4898609c270` | 2026-07-22T16:50:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29939752184 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29942384251 | in_progress | 2026-07-22T17:27:44Z |
| Dashboard Visible Issue Tracker | 29941768379 | in_progress | 2026-07-22T17:23:27Z |

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
