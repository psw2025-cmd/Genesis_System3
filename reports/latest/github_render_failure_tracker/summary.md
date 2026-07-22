# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T12:33:58.334842Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29919509591 conclusion=failure commit=5ad6b7edcae7
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29919545253 conclusion=failure commit=607d42ff0845
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29919581052 conclusion=failure commit=607d42ff0845
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29919532470 conclusion=failure commit=032bd4db1b7f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29919509707 conclusion=failure commit=5ad6b7edcae7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29919509756 conclusion=failure commit=5ad6b7edcae7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29917771272 conclusion=failure commit=9620bfc2e54e
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
| Dashboard Shell Diagnostic | 29919509591 | failure | `5ad6b7edcae7` | 2026-07-22T12:27:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29919509591 |
| System3 Autopilot Proof Board | 29919545253 | failure | `607d42ff0845` | 2026-07-22T12:26:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29919545253 |
| System3 Experimental Solution Planner | 29919581052 | failure | `607d42ff0845` | 2026-07-22T12:26:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29919581052 |
| System3 Secure Install Credential Audit | 29919532470 | failure | `032bd4db1b7f` | 2026-07-22T12:25:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29919532470 |
| Dashboard Visual Loading Postflight | 29919509707 | failure | `5ad6b7edcae7` | 2026-07-22T12:24:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29919509707 |
| Dashboard Visual Proof Strict Gate | 29919509756 | failure | `5ad6b7edcae7` | 2026-07-22T12:24:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29919509756 |
| Dashboard Visible Proof Warmed | 29917771272 | failure | `9620bfc2e54e` | 2026-07-22T12:00:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29917771272 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29919507914 | in_progress | 2026-07-22T12:32:23Z |
| System3 Safe Repair Runner | 29919734374 | in_progress | 2026-07-22T12:28:35Z |

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
