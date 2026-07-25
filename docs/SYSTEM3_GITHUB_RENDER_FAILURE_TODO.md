# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-25T13:31:27.267759Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `14`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `26`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30159792694 conclusion=failure commit=1dbba01ef243
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30159193514 conclusion=failure commit=b57333049043
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30159337081 conclusion=failure commit=b57333049043
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30159307572 conclusion=failure commit=b57333049043
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30159183229 conclusion=failure commit=b57333049043
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30158867459 conclusion=failure commit=74247f921813
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30158856992 conclusion=failure commit=d36bbf176bb5
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30158867454 conclusion=failure commit=74247f921813
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30158867449 conclusion=failure commit=74247f921813
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30158867439 conclusion=failure commit=74247f921813
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30158848922 conclusion=failure commit=4d851c718c31
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30158836724 conclusion=failure commit=4d851c718c31
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30158372158 conclusion=failure commit=6f72f3a0331f
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30158336026 conclusion=failure commit=6f72f3a0331f
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
| System3 Safe Repair Runner | 30159792694 | failure | `1dbba01ef243` | 2026-07-25T13:30:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30159792694 |
| System3 Windows Self-Hosted Full Proof | 30159193514 | failure | `b57333049043` | 2026-07-25T13:16:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30159193514 |
| Dashboard Visible Auth-Resilient Proof | 30159337081 | failure | `b57333049043` | 2026-07-25T13:15:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30159337081 |
| Dashboard Visual Proof Strict Gate | 30159307572 | failure | `b57333049043` | 2026-07-25T13:12:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30159307572 |
| Dashboard Visible Settle Proof | 30159183229 | failure | `b57333049043` | 2026-07-25T13:09:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30159183229 |
| Dashboard Shell Diagnostic | 30158867459 | failure | `74247f921813` | 2026-07-25T12:59:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30158867459 |
| Dashboard Visible Issue Tracker | 30158856992 | failure | `d36bbf176bb5` | 2026-07-25T12:58:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30158856992 |
| System3 Secure Install Credential Audit | 30158867454 | failure | `74247f921813` | 2026-07-25T12:58:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30158867454 |
| System3 Experimental Solution Planner | 30158867449 | failure | `74247f921813` | 2026-07-25T12:58:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30158867449 |
| Dashboard Visual Loading Postflight | 30158867439 | failure | `74247f921813` | 2026-07-25T12:58:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30158867439 |
| Dashboard Visible Proof Current | 30158848922 | failure | `4d851c718c31` | 2026-07-25T12:58:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30158848922 |
| System3 Autopilot Proof Board | 30158836724 | failure | `4d851c718c31` | 2026-07-25T12:58:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30158836724 |
| Dashboard Visible Proof Warmed | 30158372158 | failure | `6f72f3a0331f` | 2026-07-25T12:42:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30158372158 |
| System3 Backend Live Simulation Proof | 30158336026 | failure | `6f72f3a0331f` | 2026-07-25T12:40:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30158336026 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Workflow Failure Tracker | 30159892698 | queued | 2026-07-25T13:31:26Z |

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
