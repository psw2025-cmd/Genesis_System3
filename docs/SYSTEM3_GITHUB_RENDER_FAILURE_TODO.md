# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T12:24:28.174739Z`
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

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30201810766 conclusion=failure commit=55bd4dd29202
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30201484183 conclusion=failure commit=8a5eece4eca9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30201623302 conclusion=failure commit=8a5eece4eca9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30201442528 conclusion=failure commit=8a5eece4eca9
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30200997518 conclusion=failure commit=373b21eb9748
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30200981526 conclusion=failure commit=10b55f40169a
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30200997513 conclusion=failure commit=373b21eb9748
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30200997499 conclusion=failure commit=373b21eb9748
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30200997488 conclusion=failure commit=373b21eb9748
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30200997510 conclusion=failure commit=373b21eb9748
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30200957759 conclusion=failure commit=b0fe3006cc39
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30200741474 conclusion=failure commit=ddf315593576
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30200703815 conclusion=failure commit=a795d671f48c
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
| System3 Safe Repair Runner | 30201810766 | failure | `55bd4dd29202` | 2026-07-26T12:21:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30201810766 |
| System3 Windows Self-Hosted Full Proof | 30201484183 | failure | `8a5eece4eca9` | 2026-07-26T12:16:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30201484183 |
| Dashboard Visible Auth-Resilient Proof | 30201623302 | failure | `8a5eece4eca9` | 2026-07-26T12:14:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30201623302 |
| Dashboard Visible Settle Proof | 30201442528 | failure | `8a5eece4eca9` | 2026-07-26T12:07:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30201442528 |
| Dashboard Shell Diagnostic | 30200997518 | failure | `373b21eb9748` | 2026-07-26T11:55:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30200997518 |
| Dashboard Visible Issue Tracker | 30200981526 | failure | `10b55f40169a` | 2026-07-26T11:54:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30200981526 |
| System3 Secure Install Credential Audit | 30200997513 | failure | `373b21eb9748` | 2026-07-26T11:54:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30200997513 |
| Dashboard Visual Loading Postflight | 30200997499 | failure | `373b21eb9748` | 2026-07-26T11:53:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30200997499 |
| Dashboard Visual Proof Strict Gate | 30200997488 | failure | `373b21eb9748` | 2026-07-26T11:53:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30200997488 |
| System3 Experimental Solution Planner | 30200997510 | failure | `373b21eb9748` | 2026-07-26T11:53:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30200997510 |
| System3 Autopilot Proof Board | 30200957759 | failure | `b0fe3006cc39` | 2026-07-26T11:53:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30200957759 |
| Dashboard Visible Proof Warmed | 30200741474 | failure | `ddf315593576` | 2026-07-26T11:46:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30200741474 |
| System3 Backend Live Simulation Proof | 30200703815 | failure | `a795d671f48c` | 2026-07-26T11:44:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30200703815 |

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
