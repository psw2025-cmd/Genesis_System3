# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-27T20:31:10.580310Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `17`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `29`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30302664241 conclusion=failure commit=40e0b07d5a83
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30299867577 conclusion=failure commit=ade45c17c2a8
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30300299570 conclusion=failure commit=40e0b07d5a83
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30300220476 conclusion=failure commit=40b582d63480
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30300121095 conclusion=failure commit=f7fbb1fd6129
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30300057742 conclusion=failure commit=70b027225c1a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30300086570 conclusion=failure commit=bbcb101cfd58
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30300101761 conclusion=failure commit=cdb64dd9428b
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30300121109 conclusion=failure commit=f7fbb1fd6129
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30300101762 conclusion=failure commit=cdb64dd9428b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30300058022 conclusion=failure commit=70b027225c1a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30300057937 conclusion=failure commit=70b027225c1a
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30299984353 conclusion=failure commit=ade45c17c2a8
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30300001638 conclusion=failure commit=4904387b3bd8
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30299930596 conclusion=failure commit=ade45c17c2a8
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30299856740 conclusion=failure commit=ade45c17c2a8
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30299229700 conclusion=failure commit=fc08bba7b14e
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
| System3 Safe Repair Runner | 30302664241 | failure | `40e0b07d5a83` | 2026-07-27T20:30:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30302664241 |
| System3 Windows Self-Hosted Full Proof | 30299867577 | failure | `ade45c17c2a8` | 2026-07-27T19:59:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30299867577 |
| Dashboard Visible Proof Warmed | 30300299570 | failure | `40e0b07d5a83` | 2026-07-27T19:55:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30300299570 |
| System3 Backend Live Simulation Proof | 30300220476 | failure | `40b582d63480` | 2026-07-27T19:53:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30300220476 |
| Dashboard Visible Issue Tracker | 30300121095 | failure | `f7fbb1fd6129` | 2026-07-27T19:53:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30300121095 |
| Dashboard Shell Diagnostic | 30300057742 | failure | `70b027225c1a` | 2026-07-27T19:52:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30300057742 |
| Dashboard Visible Auth-Resilient Proof | 30300086570 | failure | `bbcb101cfd58` | 2026-07-27T19:52:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30300086570 |
| System3 Autopilot Proof Board | 30300101761 | failure | `cdb64dd9428b` | 2026-07-27T19:52:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30300101761 |
| System3 Experimental Solution Planner | 30300121109 | failure | `f7fbb1fd6129` | 2026-07-27T19:52:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30300121109 |
| System3 Secure Install Credential Audit | 30300101762 | failure | `cdb64dd9428b` | 2026-07-27T19:52:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30300101762 |
| Dashboard Visual Loading Postflight | 30300058022 | failure | `70b027225c1a` | 2026-07-27T19:51:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30300058022 |
| Dashboard Visual Proof Strict Gate | 30300057937 | failure | `70b027225c1a` | 2026-07-27T19:51:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30300057937 |
| Dashboard Deploy Provenance Gate | 30299984353 | failure | `ade45c17c2a8` | 2026-07-27T19:50:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30299984353 |
| System3 Render Worker Preflight | 30300001638 | failure | `4904387b3bd8` | 2026-07-27T19:50:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30300001638 |
| Dashboard Visual Production Proof | 30299930596 | failure | `ade45c17c2a8` | 2026-07-27T19:50:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30299930596 |
| Dashboard Visible Settle Proof | 30299856740 | failure | `ade45c17c2a8` | 2026-07-27T19:49:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30299856740 |
| Dashboard Visible Proof Current | 30299229700 | failure | `fc08bba7b14e` | 2026-07-27T19:41:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30299229700 |

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
