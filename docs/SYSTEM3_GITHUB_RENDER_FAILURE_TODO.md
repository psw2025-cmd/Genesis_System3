# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-25T16:19:20.359440Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `15`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `27`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30165275557 conclusion=failure commit=fbf05f491766
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30164975090 conclusion=failure commit=d599baffbb8e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30165111792 conclusion=failure commit=d599baffbb8e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30165141349 conclusion=failure commit=d599baffbb8e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30164960831 conclusion=failure commit=d599baffbb8e
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30164642686 conclusion=failure commit=ce7e43dc0c5f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30164631679 conclusion=failure commit=3116f15444eb
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30164642687 conclusion=failure commit=ce7e43dc0c5f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30164635165 conclusion=failure commit=1038a552f0ee
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30164642703 conclusion=failure commit=ce7e43dc0c5f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30164642694 conclusion=failure commit=ce7e43dc0c5f
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30164608490 conclusion=failure commit=a550fbb3dc70
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30164199306 conclusion=failure commit=894b2eefb05f
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30164174857 conclusion=failure commit=894b2eefb05f
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30164096608 conclusion=failure commit=8c35b16b2d85
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
| System3 Safe Repair Runner | 30165275557 | failure | `fbf05f491766` | 2026-07-25T16:18:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30165275557 |
| System3 Windows Self-Hosted Full Proof | 30164975090 | failure | `d599baffbb8e` | 2026-07-25T16:15:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164975090 |
| Dashboard Visible Auth-Resilient Proof | 30165111792 | failure | `d599baffbb8e` | 2026-07-25T16:12:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30165111792 |
| Dashboard Visual Proof Strict Gate | 30165141349 | failure | `d599baffbb8e` | 2026-07-25T16:12:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30165141349 |
| Dashboard Visible Settle Proof | 30164960831 | failure | `d599baffbb8e` | 2026-07-25T16:06:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164960831 |
| Dashboard Shell Diagnostic | 30164642686 | failure | `ce7e43dc0c5f` | 2026-07-25T15:59:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164642686 |
| Dashboard Visible Issue Tracker | 30164631679 | failure | `3116f15444eb` | 2026-07-25T15:57:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164631679 |
| System3 Secure Install Credential Audit | 30164642687 | failure | `ce7e43dc0c5f` | 2026-07-25T15:57:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164642687 |
| Dashboard Visible Proof Current | 30164635165 | failure | `1038a552f0ee` | 2026-07-25T15:57:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164635165 |
| System3 Experimental Solution Planner | 30164642703 | failure | `ce7e43dc0c5f` | 2026-07-25T15:57:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164642703 |
| Dashboard Visual Loading Postflight | 30164642694 | failure | `ce7e43dc0c5f` | 2026-07-25T15:57:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164642694 |
| System3 Autopilot Proof Board | 30164608490 | failure | `a550fbb3dc70` | 2026-07-25T15:57:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164608490 |
| Dashboard Visible Proof Warmed | 30164199306 | failure | `894b2eefb05f` | 2026-07-25T15:44:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164199306 |
| System3 Backend Live Simulation Proof | 30164174857 | failure | `894b2eefb05f` | 2026-07-25T15:43:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164174857 |
| System3 Render Worker Preflight | 30164096608 | failure | `8c35b16b2d85` | 2026-07-25T15:40:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30164096608 |

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
