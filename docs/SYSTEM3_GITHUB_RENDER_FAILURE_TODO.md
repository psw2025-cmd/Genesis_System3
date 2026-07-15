# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-15T23:20:38.695631Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29457567781 conclusion=failure commit=63f9e8e4d270
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29457495321 conclusion=failure commit=ff651d1959c8
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29457517977 conclusion=failure commit=1a47179637de
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29457555470 conclusion=failure commit=47249cc50912
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29457641666 conclusion=failure commit=3d97bba4a0bb
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29457004355 conclusion=failure commit=53e37d625918
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29457574719 conclusion=failure commit=60b19937089d
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29457600082 conclusion=failure commit=999c71c3c3d3
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29457574717 conclusion=failure commit=60b19937089d
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29457555522 conclusion=failure commit=47249cc50912
- [ ] Fix Render endpoint /: HTTP status 503 status=503
- [ ] Fix Render endpoint /ui/: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/health: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/state: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/paper: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 503 status=503

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Visible Issue Tracker | 29457567781 | failure | `63f9e8e4d270` | 2026-07-15T23:19:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29457567781 |
| Dashboard Visible Settle Proof | 29457495321 | failure | `ff651d1959c8` | 2026-07-15T23:11:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29457495321 |
| System3 Windows Self-Hosted Full Proof | 29457517977 | failure | `1a47179637de` | 2026-07-15T23:11:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29457517977 |
| Dashboard Shell Diagnostic | 29457555470 | failure | `47249cc50912` | 2026-07-15T23:09:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29457555470 |
| Dashboard Visual Proof Strict Gate | 29457641666 | failure | `3d97bba4a0bb` | 2026-07-15T23:08:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29457641666 |
| Dashboard Visible Proof Current | 29457004355 | failure | `53e37d625918` | 2026-07-15T23:08:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29457004355 |
| System3 Autopilot Proof Board | 29457574719 | failure | `60b19937089d` | 2026-07-15T23:08:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29457574719 |
| System3 Experimental Solution Planner | 29457600082 | failure | `999c71c3c3d3` | 2026-07-15T23:07:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29457600082 |
| System3 Secure Install Credential Audit | 29457574717 | failure | `60b19937089d` | 2026-07-15T23:07:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29457574717 |
| Dashboard Visual Loading Postflight | 29457555522 | failure | `47249cc50912` | 2026-07-15T23:06:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29457555522 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29458092686 | in_progress | 2026-07-15T23:17:35Z |
| Dashboard Visible Auth-Resilient Proof | 29457671804 | in_progress | 2026-07-15T23:09:13Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 503 | HTTP status 503 | `none` |
| `/ui/` | 503 | HTTP status 503 | `none` |
| `/api/health` | 503 | HTTP status 503 | `none` |
| `/api/state` | 503 | HTTP status 503 | `none` |
| `/api/deploy/info` | 503 | HTTP status 503 | `none` |
| `/api/broker/diagnose` | 503 | HTTP status 503 | `none` |
| `/api/broker/funds` | 503 | HTTP status 503 | `none` |
| `/api/broker/holdings` | 503 | HTTP status 503 | `none` |
| `/api/broker/positions/live` | 503 | HTTP status 503 | `none` |
| `/api/scanner/top_contract_gainers` | 503 | HTTP status 503 | `none` |
| `/api/paper` | 503 | HTTP status 503 | `none` |
| `/api/ml/performance` | 503 | HTTP status 503 | `none` |
