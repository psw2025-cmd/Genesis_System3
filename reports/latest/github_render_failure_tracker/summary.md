# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T01:34:14.944472Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `16`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `28`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30183010205 conclusion=failure commit=57174e32732b
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30182068907 conclusion=failure commit=dc6262df0031
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30182154875 conclusion=failure commit=46c15886be26
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30182126904 conclusion=failure commit=89cc968bd48a
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30182144687 conclusion=failure commit=9b23f6893fe0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30182144531 conclusion=failure commit=9b23f6893fe0
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30182164947 conclusion=failure commit=21711d79a083
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30182144694 conclusion=failure commit=9b23f6893fe0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30182113817 conclusion=failure commit=da549c8ddc2b
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30182128587 conclusion=failure commit=89cc968bd48a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30182126864 conclusion=failure commit=89cc968bd48a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30182126874 conclusion=failure commit=89cc968bd48a
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30182092465 conclusion=failure commit=dc6262df0031
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30182079800 conclusion=failure commit=dc6262df0031
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30182064367 conclusion=failure commit=dc6262df0031
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30182011819 conclusion=failure commit=d1c7929465a0
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
| System3 Safe Repair Runner | 30183010205 | failure | `57174e32732b` | 2026-07-26T01:33:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30183010205 |
| System3 Windows Self-Hosted Full Proof | 30182068907 | failure | `dc6262df0031` | 2026-07-26T01:05:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182068907 |
| Dashboard Visible Issue Tracker | 30182154875 | failure | `46c15886be26` | 2026-07-26T01:01:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182154875 |
| Dashboard Shell Diagnostic | 30182126904 | failure | `89cc968bd48a` | 2026-07-26T01:01:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182126904 |
| System3 Autopilot Proof Board | 30182144687 | failure | `9b23f6893fe0` | 2026-07-26T01:01:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182144687 |
| Dashboard Visible Proof Warmed | 30182144531 | failure | `9b23f6893fe0` | 2026-07-26T01:01:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182144531 |
| System3 Experimental Solution Planner | 30182164947 | failure | `21711d79a083` | 2026-07-26T01:01:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182164947 |
| System3 Secure Install Credential Audit | 30182144694 | failure | `9b23f6893fe0` | 2026-07-26T01:00:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182144694 |
| Dashboard Visible Auth-Resilient Proof | 30182113817 | failure | `da549c8ddc2b` | 2026-07-26T01:00:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182113817 |
| System3 Backend Live Simulation Proof | 30182128587 | failure | `89cc968bd48a` | 2026-07-26T01:00:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182128587 |
| Dashboard Visual Loading Postflight | 30182126864 | failure | `89cc968bd48a` | 2026-07-26T01:00:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182126864 |
| Dashboard Visual Proof Strict Gate | 30182126874 | failure | `89cc968bd48a` | 2026-07-26T01:00:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182126874 |
| Dashboard Deploy Provenance Gate | 30182092465 | failure | `dc6262df0031` | 2026-07-26T00:59:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182092465 |
| Dashboard Visual Production Proof | 30182079800 | failure | `dc6262df0031` | 2026-07-26T00:59:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182079800 |
| Dashboard Visible Settle Proof | 30182064367 | failure | `dc6262df0031` | 2026-07-26T00:58:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182064367 |
| Dashboard Visible Proof Current | 30182011819 | failure | `d1c7929465a0` | 2026-07-26T00:56:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30182011819 |

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
