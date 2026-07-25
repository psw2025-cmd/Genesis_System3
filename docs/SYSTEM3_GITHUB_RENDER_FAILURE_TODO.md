# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-25T23:19:52.939169Z`
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

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30179130674 conclusion=failure commit=a2dd4f55439f
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30178775149 conclusion=failure commit=37cb5126e4f7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30178857427 conclusion=failure commit=37cb5126e4f7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30178846555 conclusion=failure commit=37cb5126e4f7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30178758277 conclusion=failure commit=37cb5126e4f7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30178490514 conclusion=failure commit=9130892098ee
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30178370326 conclusion=failure commit=9e8c936e86fa
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30178364722 conclusion=failure commit=4b0094d1c748
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30178370339 conclusion=failure commit=9e8c936e86fa
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30178370304 conclusion=failure commit=9e8c936e86fa
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30178370333 conclusion=failure commit=9e8c936e86fa
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30178340972 conclusion=failure commit=5a8e20311758
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30177948259 conclusion=failure commit=bf6fcfe62d45
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30177921108 conclusion=failure commit=bf6fcfe62d45
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30177842919 conclusion=failure commit=83ee81172aeb
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
| System3 Safe Repair Runner | 30179130674 | failure | `a2dd4f55439f` | 2026-07-25T23:19:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30179130674 |
| System3 Windows Self-Hosted Full Proof | 30178775149 | failure | `37cb5126e4f7` | 2026-07-25T23:14:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30178775149 |
| Dashboard Visible Auth-Resilient Proof | 30178857427 | failure | `37cb5126e4f7` | 2026-07-25T23:09:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30178857427 |
| Dashboard Visual Proof Strict Gate | 30178846555 | failure | `37cb5126e4f7` | 2026-07-25T23:07:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30178846555 |
| Dashboard Visible Settle Proof | 30178758277 | failure | `37cb5126e4f7` | 2026-07-25T23:06:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30178758277 |
| Dashboard Visible Proof Current | 30178490514 | failure | `9130892098ee` | 2026-07-25T22:56:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30178490514 |
| Dashboard Shell Diagnostic | 30178370326 | failure | `9e8c936e86fa` | 2026-07-25T22:53:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30178370326 |
| Dashboard Visible Issue Tracker | 30178364722 | failure | `4b0094d1c748` | 2026-07-25T22:52:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30178364722 |
| System3 Secure Install Credential Audit | 30178370339 | failure | `9e8c936e86fa` | 2026-07-25T22:52:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30178370339 |
| System3 Experimental Solution Planner | 30178370304 | failure | `9e8c936e86fa` | 2026-07-25T22:51:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30178370304 |
| Dashboard Visual Loading Postflight | 30178370333 | failure | `9e8c936e86fa` | 2026-07-25T22:51:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30178370333 |
| System3 Autopilot Proof Board | 30178340972 | failure | `5a8e20311758` | 2026-07-25T22:51:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30178340972 |
| Dashboard Visible Proof Warmed | 30177948259 | failure | `bf6fcfe62d45` | 2026-07-25T22:39:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30177948259 |
| System3 Backend Live Simulation Proof | 30177921108 | failure | `bf6fcfe62d45` | 2026-07-25T22:37:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30177921108 |
| System3 Render Worker Preflight | 30177842919 | failure | `83ee81172aeb` | 2026-07-25T22:35:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30177842919 |

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
