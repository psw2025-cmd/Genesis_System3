# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-21T08:54:30.876064Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `5`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29815371419 conclusion=failure commit=e8265e5b9882
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29815401009 conclusion=failure commit=09dc3b69ae59
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29815439048 conclusion=failure commit=eaa673edea4f
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29815400957 conclusion=failure commit=09dc3b69ae59
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29815371337 conclusion=failure commit=e8265e5b9882
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29815371308 conclusion=failure commit=e8265e5b9882
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=29814649955 conclusion=failure commit=e0384fab291d
- [ ] Fix Render endpoint /: HTTP status 502 status=502
- [ ] Fix Render endpoint /ui/: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/health: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/state: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/paper: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 502 status=502

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Shell Diagnostic | 29815371419 | failure | `e8265e5b9882` | 2026-07-21T08:46:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29815371419 |
| System3 Autopilot Proof Board | 29815401009 | failure | `09dc3b69ae59` | 2026-07-21T08:44:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29815401009 |
| System3 Experimental Solution Planner | 29815439048 | failure | `eaa673edea4f` | 2026-07-21T08:44:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29815439048 |
| System3 Secure Install Credential Audit | 29815400957 | failure | `09dc3b69ae59` | 2026-07-21T08:43:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29815400957 |
| Dashboard Visual Loading Postflight | 29815371337 | failure | `e8265e5b9882` | 2026-07-21T08:43:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29815371337 |
| Dashboard Visual Proof Strict Gate | 29815371308 | failure | `e8265e5b9882` | 2026-07-21T08:43:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29815371308 |
| System3 Broker Chain Semantic Gate | 29814649955 | failure | `e0384fab291d` | 2026-07-21T08:32:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29814649955 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 29815990498 | in_progress | 2026-07-21T08:52:50Z |
| Permanent Repo Render Safety | 29815826344 | in_progress | 2026-07-21T08:50:17Z |
| System3 Safe Repair Runner | 29815789628 | in_progress | 2026-07-21T08:50:16Z |
| Dashboard Visible Issue Tracker | 29814629475 | in_progress | 2026-07-21T08:43:08Z |
| System3 Full Auto Truth | 29813856451 | in_progress | 2026-07-21T08:19:50Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 502 | HTTP status 502 | `none` |
| `/ui/` | 502 | HTTP status 502 | `none` |
| `/api/health` | 502 | HTTP status 502 | `none` |
| `/api/state` | 502 | HTTP status 502 | `none` |
| `/api/deploy/info` | 502 | HTTP status 502 | `none` |
| `/api/broker/diagnose` | 502 | HTTP status 502 | `none` |
| `/api/broker/funds` | 502 | HTTP status 502 | `none` |
| `/api/broker/holdings` | 502 | HTTP status 502 | `none` |
| `/api/broker/positions/live` | 502 | HTTP status 502 | `none` |
| `/api/scanner/top_contract_gainers` | 502 | HTTP status 502 | `none` |
| `/api/paper` | 502 | HTTP status 502 | `none` |
| `/api/ml/performance` | 502 | HTTP status 502 | `none` |
