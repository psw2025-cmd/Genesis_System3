# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-24T14:35:04.326395Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `13`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `25`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30101387936 conclusion=failure commit=b48ad869fe5e
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30100091956 conclusion=failure commit=bdc07dda9c67
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30100079515 conclusion=failure commit=1240e4132a55
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30100091960 conclusion=failure commit=bdc07dda9c67
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30100039236 conclusion=failure commit=1afaf0f8b3d7
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30100092085 conclusion=failure commit=bdc07dda9c67
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30100091890 conclusion=failure commit=bdc07dda9c67
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30100091999 conclusion=failure commit=bdc07dda9c67
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30099195929 conclusion=failure commit=e6e0ae89700c
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30099053577 conclusion=failure commit=e6e0ae89700c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30098938402 conclusion=failure commit=e6e0ae89700c
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30098817354 conclusion=failure commit=6e4ff05eb7b1
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30098769806 conclusion=failure commit=a437e062b061
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
| System3 Safe Repair Runner | 30101387936 | failure | `b48ad869fe5e` | 2026-07-24T14:34:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30101387936 |
| Dashboard Shell Diagnostic | 30100091956 | failure | `bdc07dda9c67` | 2026-07-24T14:15:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30100091956 |
| Dashboard Visible Issue Tracker | 30100079515 | failure | `1240e4132a55` | 2026-07-24T14:13:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30100079515 |
| System3 Secure Install Credential Audit | 30100091960 | failure | `bdc07dda9c67` | 2026-07-24T14:13:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30100091960 |
| System3 Autopilot Proof Board | 30100039236 | failure | `1afaf0f8b3d7` | 2026-07-24T14:13:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30100039236 |
| System3 Experimental Solution Planner | 30100092085 | failure | `bdc07dda9c67` | 2026-07-24T14:13:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30100092085 |
| Dashboard Visual Proof Strict Gate | 30100091890 | failure | `bdc07dda9c67` | 2026-07-24T14:13:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30100091890 |
| Dashboard Visual Loading Postflight | 30100091999 | failure | `bdc07dda9c67` | 2026-07-24T14:13:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30100091999 |
| Dashboard Visible Proof Warmed | 30099195929 | failure | `e6e0ae89700c` | 2026-07-24T14:01:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30099195929 |
| System3 Backend Live Simulation Proof | 30099053577 | failure | `e6e0ae89700c` | 2026-07-24T13:58:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30099053577 |
| Dashboard Visible Auth-Resilient Proof | 30098938402 | failure | `e6e0ae89700c` | 2026-07-24T13:57:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30098938402 |
| System3 Render Worker Preflight | 30098817354 | failure | `6e4ff05eb7b1` | 2026-07-24T13:55:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30098817354 |
| Dashboard Deploy Provenance Gate | 30098769806 | failure | `a437e062b061` | 2026-07-24T13:54:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30098769806 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

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
