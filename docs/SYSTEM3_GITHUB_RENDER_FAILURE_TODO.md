# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-24T13:32:17.019584Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `11`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30097080607 conclusion=failure commit=fa76ccf5bbce
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30095974717 conclusion=failure commit=e526e6b7e9dc
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30095974513 conclusion=failure commit=e526e6b7e9dc
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30095974740 conclusion=failure commit=e526e6b7e9dc
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30095974582 conclusion=failure commit=e526e6b7e9dc
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30095974462 conclusion=failure commit=e526e6b7e9dc
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30095929110 conclusion=failure commit=0b83d37d827f
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30095363001 conclusion=failure commit=3f4b7e558f4f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30094542165 conclusion=failure commit=092afeeed1de
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30094473726 conclusion=failure commit=b95c59264e59
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30094406015 conclusion=failure commit=62f63e801b98
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
| System3 Safe Repair Runner | 30097080607 | failure | `fa76ccf5bbce` | 2026-07-24T13:31:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30097080607 |
| Dashboard Shell Diagnostic | 30095974717 | failure | `e526e6b7e9dc` | 2026-07-24T13:14:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30095974717 |
| System3 Secure Install Credential Audit | 30095974513 | failure | `e526e6b7e9dc` | 2026-07-24T13:12:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30095974513 |
| Dashboard Visual Proof Strict Gate | 30095974740 | failure | `e526e6b7e9dc` | 2026-07-24T13:12:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30095974740 |
| Dashboard Visual Loading Postflight | 30095974582 | failure | `e526e6b7e9dc` | 2026-07-24T13:12:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30095974582 |
| System3 Experimental Solution Planner | 30095974462 | failure | `e526e6b7e9dc` | 2026-07-24T13:12:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30095974462 |
| Dashboard Visible Issue Tracker | 30095929110 | failure | `0b83d37d827f` | 2026-07-24T13:12:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30095929110 |
| System3 Autopilot Proof Board | 30095363001 | failure | `3f4b7e558f4f` | 2026-07-24T13:03:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30095363001 |
| Dashboard Visible Proof Warmed | 30094542165 | failure | `092afeeed1de` | 2026-07-24T12:51:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30094542165 |
| System3 Backend Live Simulation Proof | 30094473726 | failure | `b95c59264e59` | 2026-07-24T12:49:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30094473726 |
| Dashboard Visible Auth-Resilient Proof | 30094406015 | failure | `62f63e801b98` | 2026-07-24T12:49:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30094406015 |

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
