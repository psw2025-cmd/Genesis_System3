# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-24T15:30:42.023593Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30105395211 conclusion=failure commit=8e902312816e
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30104271324 conclusion=failure commit=3117a95e0803
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30104271809 conclusion=failure commit=3117a95e0803
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30104263045 conclusion=failure commit=7e890299463e
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30104271110 conclusion=failure commit=3117a95e0803
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30104271352 conclusion=failure commit=3117a95e0803
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30104271188 conclusion=failure commit=3117a95e0803
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30104204573 conclusion=failure commit=ea7bfa3757ec
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30103427812 conclusion=failure commit=a67f0ec0ab86
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30103317362 conclusion=failure commit=a67f0ec0ab86
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30103209859 conclusion=failure commit=d5195e593677
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30103093306 conclusion=failure commit=f5ee5fcde568
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
| System3 Safe Repair Runner | 30105395211 | failure | `8e902312816e` | 2026-07-24T15:30:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30105395211 |
| Dashboard Shell Diagnostic | 30104271324 | failure | `3117a95e0803` | 2026-07-24T15:13:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30104271324 |
| System3 Experimental Solution Planner | 30104271809 | failure | `3117a95e0803` | 2026-07-24T15:13:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30104271809 |
| Dashboard Visible Issue Tracker | 30104263045 | failure | `7e890299463e` | 2026-07-24T15:12:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30104263045 |
| System3 Secure Install Credential Audit | 30104271110 | failure | `3117a95e0803` | 2026-07-24T15:12:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30104271110 |
| Dashboard Visual Proof Strict Gate | 30104271352 | failure | `3117a95e0803` | 2026-07-24T15:12:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30104271352 |
| Dashboard Visual Loading Postflight | 30104271188 | failure | `3117a95e0803` | 2026-07-24T15:12:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30104271188 |
| System3 Autopilot Proof Board | 30104204573 | failure | `ea7bfa3757ec` | 2026-07-24T15:12:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30104204573 |
| Dashboard Visible Proof Warmed | 30103427812 | failure | `a67f0ec0ab86` | 2026-07-24T15:01:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30103427812 |
| System3 Backend Live Simulation Proof | 30103317362 | failure | `a67f0ec0ab86` | 2026-07-24T14:59:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30103317362 |
| Dashboard Visible Auth-Resilient Proof | 30103209859 | failure | `d5195e593677` | 2026-07-24T14:58:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30103209859 |
| System3 Render Worker Preflight | 30103093306 | failure | `f5ee5fcde568` | 2026-07-24T14:55:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30103093306 |

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
