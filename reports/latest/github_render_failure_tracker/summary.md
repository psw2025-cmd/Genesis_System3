# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T11:28:25.707678Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30199644840 conclusion=failure commit=ff644f8f5ddd
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30199745837 conclusion=failure commit=ff644f8f5ddd
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30199727003 conclusion=failure commit=ff644f8f5ddd
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30199486340 conclusion=failure commit=9d2a51ef7ff5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30199492614 conclusion=failure commit=5d33f9fea814
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30199478314 conclusion=failure commit=7fdc26c4fe15
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30199486330 conclusion=failure commit=9d2a51ef7ff5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30199486335 conclusion=failure commit=9d2a51ef7ff5
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30199486348 conclusion=failure commit=9d2a51ef7ff5
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30199457944 conclusion=failure commit=f716e32f8f58
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30199090242 conclusion=failure commit=6ce517a674cf
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30199070601 conclusion=failure commit=d695cc1ba55a
- [ ] Fix Render endpoint /: HTTP status 0 status=0
- [ ] Fix Render endpoint /ui/: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/health: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/paper: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Windows Self-Hosted Full Proof | 30199644840 | failure | `ff644f8f5ddd` | 2026-07-26T11:20:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199644840 |
| Dashboard Visible Auth-Resilient Proof | 30199745837 | failure | `ff644f8f5ddd` | 2026-07-26T11:15:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199745837 |
| Dashboard Visual Proof Strict Gate | 30199727003 | failure | `ff644f8f5ddd` | 2026-07-26T11:13:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199727003 |
| Dashboard Shell Diagnostic | 30199486340 | failure | `9d2a51ef7ff5` | 2026-07-26T11:07:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199486340 |
| Dashboard Visible Proof Current | 30199492614 | failure | `5d33f9fea814` | 2026-07-26T11:06:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199492614 |
| Dashboard Visible Issue Tracker | 30199478314 | failure | `7fdc26c4fe15` | 2026-07-26T11:06:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199478314 |
| System3 Secure Install Credential Audit | 30199486330 | failure | `9d2a51ef7ff5` | 2026-07-26T11:06:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199486330 |
| Dashboard Visual Loading Postflight | 30199486335 | failure | `9d2a51ef7ff5` | 2026-07-26T11:06:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199486335 |
| System3 Experimental Solution Planner | 30199486348 | failure | `9d2a51ef7ff5` | 2026-07-26T11:06:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199486348 |
| System3 Autopilot Proof Board | 30199457944 | failure | `f716e32f8f58` | 2026-07-26T11:05:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199457944 |
| Dashboard Visible Proof Warmed | 30199090242 | failure | `6ce517a674cf` | 2026-07-26T10:54:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199090242 |
| System3 Backend Live Simulation Proof | 30199070601 | failure | `d695cc1ba55a` | 2026-07-26T10:53:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30199070601 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 30200129893 | in_progress | 2026-07-26T11:26:41Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 0 | HTTP status 0 | `none` |
| `/ui/` | 0 | HTTP status 0 | `none` |
| `/api/health` | 0 | HTTP status 0 | `none` |
| `/api/state` | 0 | HTTP status 0 | `none` |
| `/api/deploy/info` | 0 | HTTP status 0 | `none` |
| `/api/broker/diagnose` | 0 | HTTP status 0 | `none` |
| `/api/broker/funds` | 0 | HTTP status 0 | `none` |
| `/api/broker/holdings` | 0 | HTTP status 0 | `none` |
| `/api/broker/positions/live` | 0 | HTTP status 0 | `none` |
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
| `/api/paper` | 0 | HTTP status 0 | `none` |
| `/api/ml/performance` | 0 | HTTP status 0 | `none` |
