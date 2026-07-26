# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T09:40:58.435386Z`
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

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30196804392 conclusion=failure commit=aec5baf2cb55
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30196476822 conclusion=failure commit=100bf9a74634
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30196551829 conclusion=failure commit=100bf9a74634
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30196531380 conclusion=failure commit=100bf9a74634
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30196267552 conclusion=failure commit=821d303140c8
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30196306044 conclusion=failure commit=00a394ce1e0b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30196282061 conclusion=failure commit=f6afb09c700f
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30196282063 conclusion=failure commit=f6afb09c700f
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30196267551 conclusion=failure commit=821d303140c8
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30196245874 conclusion=failure commit=8440890c5265
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30196267830 conclusion=failure commit=821d303140c8
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30195809997 conclusion=failure commit=532fa2e424fc
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30195776570 conclusion=failure commit=28cc7efd86c9
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
| System3 Safe Repair Runner | 30196804392 | failure | `aec5baf2cb55` | 2026-07-26T09:40:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30196804392 |
| System3 Windows Self-Hosted Full Proof | 30196476822 | failure | `100bf9a74634` | 2026-07-26T09:37:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30196476822 |
| Dashboard Visible Auth-Resilient Proof | 30196551829 | failure | `100bf9a74634` | 2026-07-26T09:30:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30196551829 |
| Dashboard Visual Proof Strict Gate | 30196531380 | failure | `100bf9a74634` | 2026-07-26T09:29:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30196531380 |
| Dashboard Shell Diagnostic | 30196267552 | failure | `821d303140c8` | 2026-07-26T09:22:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30196267552 |
| Dashboard Visible Proof Current | 30196306044 | failure | `00a394ce1e0b` | 2026-07-26T09:21:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30196306044 |
| Dashboard Visible Issue Tracker | 30196282061 | failure | `f6afb09c700f` | 2026-07-26T09:21:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30196282061 |
| System3 Experimental Solution Planner | 30196282063 | failure | `f6afb09c700f` | 2026-07-26T09:20:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30196282063 |
| System3 Secure Install Credential Audit | 30196267551 | failure | `821d303140c8` | 2026-07-26T09:20:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30196267551 |
| System3 Autopilot Proof Board | 30196245874 | failure | `8440890c5265` | 2026-07-26T09:20:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30196245874 |
| Dashboard Visual Loading Postflight | 30196267830 | failure | `821d303140c8` | 2026-07-26T09:20:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30196267830 |
| Dashboard Visible Proof Warmed | 30195809997 | failure | `532fa2e424fc` | 2026-07-26T09:05:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30195809997 |
| System3 Backend Live Simulation Proof | 30195776570 | failure | `28cc7efd86c9` | 2026-07-26T09:04:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30195776570 |

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
