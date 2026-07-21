# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-21T09:50:38.479741Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29819605127 conclusion=failure commit=198e86f341c5
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29819568982 conclusion=failure commit=198e86f341c5
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29819616950 conclusion=failure commit=7c2b5fe67508
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29819605166 conclusion=failure commit=198e86f341c5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29819605148 conclusion=failure commit=198e86f341c5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29819605250 conclusion=failure commit=198e86f341c5
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=29818613760 conclusion=failure commit=504a60da7580
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
| Dashboard Shell Diagnostic | 29819605127 | failure | `198e86f341c5` | 2026-07-21T09:49:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29819605127 |
| System3 Autopilot Proof Board | 29819568982 | failure | `198e86f341c5` | 2026-07-21T09:47:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29819568982 |
| System3 Experimental Solution Planner | 29819616950 | failure | `7c2b5fe67508` | 2026-07-21T09:46:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29819616950 |
| System3 Secure Install Credential Audit | 29819605166 | failure | `198e86f341c5` | 2026-07-21T09:46:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29819605166 |
| Dashboard Visual Proof Strict Gate | 29819605148 | failure | `198e86f341c5` | 2026-07-21T09:46:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29819605148 |
| Dashboard Visual Loading Postflight | 29819605250 | failure | `198e86f341c5` | 2026-07-21T09:46:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29819605250 |
| System3 Broker Chain Semantic Gate | 29818613760 | failure | `504a60da7580` | 2026-07-21T09:31:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29818613760 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 29819775450 | in_progress | 2026-07-21T09:49:08Z |
| Permanent Repo Render Safety | 29819658150 | in_progress | 2026-07-21T09:47:19Z |
| System3 Safe Repair Runner | 29819644916 | in_progress | 2026-07-21T09:47:10Z |
| Dashboard Visible Issue Tracker | 29819616972 | pending | 2026-07-21T09:46:40Z |
| System3 Full Auto Truth | 29817942785 | in_progress | 2026-07-21T09:21:27Z |

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
