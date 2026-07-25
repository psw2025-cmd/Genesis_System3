# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-25T00:32:34.763535Z`
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

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30136014648 conclusion=failure commit=e55e49cc80cd
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30135531820 conclusion=failure commit=6fd887076167
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30135683545 conclusion=failure commit=6fd887076167
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30135665863 conclusion=failure commit=6fd887076167
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30135503523 conclusion=failure commit=6fd887076167
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30135110516 conclusion=failure commit=e0d63d07cd7e
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30135012013 conclusion=failure commit=52c02d0e8f3e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30135010876 conclusion=failure commit=52c02d0e8f3e
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30135011728 conclusion=failure commit=52c02d0e8f3e
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30135011858 conclusion=failure commit=52c02d0e8f3e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30135011720 conclusion=failure commit=52c02d0e8f3e
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30134966725 conclusion=failure commit=13125be07a1f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30134427441 conclusion=failure commit=1cd5b3e3cc53
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30134364065 conclusion=failure commit=1cd5b3e3cc53
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30134272761 conclusion=failure commit=85d43aade1da
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
| System3 Safe Repair Runner | 30136014648 | failure | `e55e49cc80cd` | 2026-07-25T00:21:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30136014648 |
| System3 Windows Self-Hosted Full Proof | 30135531820 | failure | `6fd887076167` | 2026-07-25T00:15:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30135531820 |
| Dashboard Visible Auth-Resilient Proof | 30135683545 | failure | `6fd887076167` | 2026-07-25T00:12:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30135683545 |
| Dashboard Visual Proof Strict Gate | 30135665863 | failure | `6fd887076167` | 2026-07-25T00:10:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30135665863 |
| Dashboard Visible Settle Proof | 30135503523 | failure | `6fd887076167` | 2026-07-25T00:07:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30135503523 |
| Dashboard Visible Proof Current | 30135110516 | failure | `e0d63d07cd7e` | 2026-07-24T23:57:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30135110516 |
| Dashboard Shell Diagnostic | 30135012013 | failure | `52c02d0e8f3e` | 2026-07-24T23:56:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30135012013 |
| Dashboard Visible Issue Tracker | 30135010876 | failure | `52c02d0e8f3e` | 2026-07-24T23:55:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30135010876 |
| System3 Secure Install Credential Audit | 30135011728 | failure | `52c02d0e8f3e` | 2026-07-24T23:55:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30135011728 |
| System3 Experimental Solution Planner | 30135011858 | failure | `52c02d0e8f3e` | 2026-07-24T23:55:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30135011858 |
| Dashboard Visual Loading Postflight | 30135011720 | failure | `52c02d0e8f3e` | 2026-07-24T23:55:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30135011720 |
| System3 Autopilot Proof Board | 30134966725 | failure | `13125be07a1f` | 2026-07-24T23:54:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30134966725 |
| Dashboard Visible Proof Warmed | 30134427441 | failure | `1cd5b3e3cc53` | 2026-07-24T23:41:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30134427441 |
| System3 Backend Live Simulation Proof | 30134364065 | failure | `1cd5b3e3cc53` | 2026-07-24T23:40:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30134364065 |
| System3 Render Worker Preflight | 30134272761 | failure | `85d43aade1da` | 2026-07-24T23:37:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30134272761 |

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
