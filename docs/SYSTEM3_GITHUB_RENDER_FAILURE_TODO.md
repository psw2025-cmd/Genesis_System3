# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T22:22:11.508293Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29962383817 conclusion=failure commit=8444e455fd92
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29962397715 conclusion=failure commit=6ce7c59fe0ef
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29962338851 conclusion=failure commit=0800ad309202
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29962383803 conclusion=failure commit=8444e455fd92
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29962383883 conclusion=failure commit=8444e455fd92
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29962383833 conclusion=failure commit=8444e455fd92
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29961730845 conclusion=failure commit=f28060c4369c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29961703658 conclusion=failure commit=f28060c4369c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29961122122 conclusion=failure commit=f7f7cf7e6444
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
| Dashboard Shell Diagnostic | 29962383817 | failure | `8444e455fd92` | 2026-07-22T22:21:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29962383817 |
| System3 Experimental Solution Planner | 29962397715 | failure | `6ce7c59fe0ef` | 2026-07-22T22:18:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29962397715 |
| System3 Autopilot Proof Board | 29962338851 | failure | `0800ad309202` | 2026-07-22T22:18:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29962338851 |
| System3 Secure Install Credential Audit | 29962383803 | failure | `8444e455fd92` | 2026-07-22T22:18:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29962383803 |
| Dashboard Visual Loading Postflight | 29962383883 | failure | `8444e455fd92` | 2026-07-22T22:18:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29962383883 |
| Dashboard Visual Proof Strict Gate | 29962383833 | failure | `8444e455fd92` | 2026-07-22T22:18:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29962383833 |
| System3 Windows Self-Hosted Full Proof | 29961730845 | failure | `f28060c4369c` | 2026-07-22T22:14:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29961730845 |
| Dashboard Visible Settle Proof | 29961703658 | failure | `f28060c4369c` | 2026-07-22T22:12:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29961703658 |
| Dashboard Visible Proof Current | 29961122122 | failure | `f7f7cf7e6444` | 2026-07-22T22:09:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29961122122 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29962419872 | in_progress | 2026-07-22T22:19:00Z |
| Dashboard Visible Issue Tracker | 29962397699 | pending | 2026-07-22T22:18:31Z |
| Dashboard Visible Auth-Resilient Proof | 29961978206 | in_progress | 2026-07-22T22:11:26Z |

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
