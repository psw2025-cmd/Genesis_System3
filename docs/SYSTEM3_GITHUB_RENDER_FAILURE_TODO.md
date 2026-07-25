# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-25T19:26:52.782962Z`
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

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30171529694 conclusion=failure commit=5472a0c95892
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30171001408 conclusion=failure commit=40f1147044b5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30171134148 conclusion=failure commit=40f1147044b5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30171111304 conclusion=failure commit=40f1147044b5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30170978070 conclusion=failure commit=40f1147044b5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30170634766 conclusion=failure commit=a699dd7f4133
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30170498079 conclusion=failure commit=55f9fdbacc37
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30170495431 conclusion=failure commit=8f7c5aea4398
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30170498069 conclusion=failure commit=55f9fdbacc37
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30170476087 conclusion=failure commit=c1e80cfce258
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30170498062 conclusion=failure commit=55f9fdbacc37
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30170498088 conclusion=failure commit=55f9fdbacc37
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30170056716 conclusion=failure commit=ac7f009733bb
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30170017257 conclusion=failure commit=ac7f009733bb
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30169934416 conclusion=failure commit=7862bebbeceb
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
| System3 Safe Repair Runner | 30171529694 | failure | `5472a0c95892` | 2026-07-25T19:26:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30171529694 |
| System3 Windows Self-Hosted Full Proof | 30171001408 | failure | `40f1147044b5` | 2026-07-25T19:17:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30171001408 |
| Dashboard Visible Auth-Resilient Proof | 30171134148 | failure | `40f1147044b5` | 2026-07-25T19:13:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30171134148 |
| Dashboard Visual Proof Strict Gate | 30171111304 | failure | `40f1147044b5` | 2026-07-25T19:11:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30171111304 |
| Dashboard Visible Settle Proof | 30170978070 | failure | `40f1147044b5` | 2026-07-25T19:07:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30170978070 |
| Dashboard Visible Proof Current | 30170634766 | failure | `a699dd7f4133` | 2026-07-25T19:00:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30170634766 |
| Dashboard Shell Diagnostic | 30170498079 | failure | `55f9fdbacc37` | 2026-07-25T18:54:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30170498079 |
| Dashboard Visible Issue Tracker | 30170495431 | failure | `8f7c5aea4398` | 2026-07-25T18:53:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30170495431 |
| System3 Secure Install Credential Audit | 30170498069 | failure | `55f9fdbacc37` | 2026-07-25T18:53:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30170498069 |
| System3 Autopilot Proof Board | 30170476087 | failure | `c1e80cfce258` | 2026-07-25T18:53:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30170476087 |
| System3 Experimental Solution Planner | 30170498062 | failure | `55f9fdbacc37` | 2026-07-25T18:52:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30170498062 |
| Dashboard Visual Loading Postflight | 30170498088 | failure | `55f9fdbacc37` | 2026-07-25T18:52:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30170498088 |
| Dashboard Visible Proof Warmed | 30170056716 | failure | `ac7f009733bb` | 2026-07-25T18:40:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30170056716 |
| System3 Backend Live Simulation Proof | 30170017257 | failure | `ac7f009733bb` | 2026-07-25T18:38:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30170017257 |
| System3 Render Worker Preflight | 30169934416 | failure | `7862bebbeceb` | 2026-07-25T18:35:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30169934416 |

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
