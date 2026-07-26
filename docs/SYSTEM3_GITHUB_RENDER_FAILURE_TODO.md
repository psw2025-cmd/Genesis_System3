# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T19:27:35.920521Z`
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

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30216804028 conclusion=failure commit=5a2333134816
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30216203384 conclusion=failure commit=cde4f747d9c5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30216364485 conclusion=failure commit=cde4f747d9c5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30216333554 conclusion=failure commit=cde4f747d9c5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30216197480 conclusion=failure commit=cde4f747d9c5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30215814357 conclusion=failure commit=2904cf9a15c2
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30215737476 conclusion=failure commit=9b366a10bc6a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30215725871 conclusion=failure commit=55eda85c56d6
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30215737441 conclusion=failure commit=9b366a10bc6a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30215737473 conclusion=failure commit=9b366a10bc6a
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30215737465 conclusion=failure commit=9b366a10bc6a
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30215704581 conclusion=failure commit=fbf1cd9759e5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30215215674 conclusion=failure commit=cb4d0459a837
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30215177328 conclusion=failure commit=3882355a7613
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
| System3 Safe Repair Runner | 30216804028 | failure | `5a2333134816` | 2026-07-26T19:27:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30216804028 |
| System3 Windows Self-Hosted Full Proof | 30216203384 | failure | `cde4f747d9c5` | 2026-07-26T19:15:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30216203384 |
| Dashboard Visible Auth-Resilient Proof | 30216364485 | failure | `cde4f747d9c5` | 2026-07-26T19:13:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30216364485 |
| Dashboard Visual Proof Strict Gate | 30216333554 | failure | `cde4f747d9c5` | 2026-07-26T19:11:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30216333554 |
| Dashboard Visible Settle Proof | 30216197480 | failure | `cde4f747d9c5` | 2026-07-26T19:08:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30216197480 |
| Dashboard Visible Proof Current | 30215814357 | failure | `2904cf9a15c2` | 2026-07-26T18:57:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30215814357 |
| Dashboard Shell Diagnostic | 30215737476 | failure | `9b366a10bc6a` | 2026-07-26T18:56:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30215737476 |
| Dashboard Visible Issue Tracker | 30215725871 | failure | `55eda85c56d6` | 2026-07-26T18:55:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30215725871 |
| System3 Secure Install Credential Audit | 30215737441 | failure | `9b366a10bc6a` | 2026-07-26T18:55:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30215737441 |
| Dashboard Visual Loading Postflight | 30215737473 | failure | `9b366a10bc6a` | 2026-07-26T18:55:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30215737473 |
| System3 Experimental Solution Planner | 30215737465 | failure | `9b366a10bc6a` | 2026-07-26T18:55:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30215737465 |
| System3 Autopilot Proof Board | 30215704581 | failure | `fbf1cd9759e5` | 2026-07-26T18:55:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30215704581 |
| Dashboard Visible Proof Warmed | 30215215674 | failure | `cb4d0459a837` | 2026-07-26T18:41:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30215215674 |
| System3 Backend Live Simulation Proof | 30215177328 | failure | `3882355a7613` | 2026-07-26T18:39:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30215177328 |

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
