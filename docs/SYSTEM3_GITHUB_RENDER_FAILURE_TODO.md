# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-25T20:20:01.053206Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `14`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `26`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30173261615 conclusion=failure commit=dd469f6adef5
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30172990624 conclusion=failure commit=63205ea72301
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30173154416 conclusion=failure commit=63205ea72301
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30173121753 conclusion=failure commit=63205ea72301
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30172977651 conclusion=failure commit=63205ea72301
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30172797694 conclusion=failure commit=c6b08f309df7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30172791109 conclusion=failure commit=59cbe0663c93
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30172797716 conclusion=failure commit=c6b08f309df7
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30172797709 conclusion=failure commit=c6b08f309df7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30172797698 conclusion=failure commit=c6b08f309df7
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30172770360 conclusion=failure commit=6e2209204c7a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30172762610 conclusion=failure commit=a668857af276
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30172237968 conclusion=failure commit=263e9dbd5098
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30172190714 conclusion=failure commit=263e9dbd5098
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
| System3 Safe Repair Runner | 30173261615 | failure | `dd469f6adef5` | 2026-07-25T20:19:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30173261615 |
| System3 Windows Self-Hosted Full Proof | 30172990624 | failure | `63205ea72301` | 2026-07-25T20:17:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30172990624 |
| Dashboard Visual Proof Strict Gate | 30173154416 | failure | `63205ea72301` | 2026-07-25T20:13:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30173154416 |
| Dashboard Visible Auth-Resilient Proof | 30173121753 | failure | `63205ea72301` | 2026-07-25T20:13:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30173121753 |
| Dashboard Visible Settle Proof | 30172977651 | failure | `63205ea72301` | 2026-07-25T20:08:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30172977651 |
| Dashboard Shell Diagnostic | 30172797694 | failure | `c6b08f309df7` | 2026-07-25T20:04:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30172797694 |
| Dashboard Visible Issue Tracker | 30172791109 | failure | `59cbe0663c93` | 2026-07-25T20:03:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30172791109 |
| System3 Secure Install Credential Audit | 30172797716 | failure | `c6b08f309df7` | 2026-07-25T20:02:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30172797716 |
| System3 Experimental Solution Planner | 30172797709 | failure | `c6b08f309df7` | 2026-07-25T20:02:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30172797709 |
| Dashboard Visual Loading Postflight | 30172797698 | failure | `c6b08f309df7` | 2026-07-25T20:02:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30172797698 |
| System3 Autopilot Proof Board | 30172770360 | failure | `6e2209204c7a` | 2026-07-25T20:02:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30172770360 |
| Dashboard Visible Proof Current | 30172762610 | failure | `a668857af276` | 2026-07-25T20:02:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30172762610 |
| Dashboard Visible Proof Warmed | 30172237968 | failure | `263e9dbd5098` | 2026-07-25T19:46:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30172237968 |
| System3 Backend Live Simulation Proof | 30172190714 | failure | `263e9dbd5098` | 2026-07-25T19:44:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30172190714 |

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
