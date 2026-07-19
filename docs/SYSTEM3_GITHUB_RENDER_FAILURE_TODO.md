# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T21:17:36.277124Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29703910361 conclusion=failure commit=267e08ae48cc
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29703910386 conclusion=failure commit=267e08ae48cc
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29703890613 conclusion=failure commit=267e08ae48cc
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29703910344 conclusion=failure commit=267e08ae48cc
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29703910875 conclusion=failure commit=267e08ae48cc
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29703910357 conclusion=failure commit=267e08ae48cc
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29703671693 conclusion=failure commit=e99c7aeb927b
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29703675518 conclusion=failure commit=e99c7aeb927b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29703393913 conclusion=failure commit=ed56c6577110
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
| Dashboard Shell Diagnostic | 29703910361 | failure | `267e08ae48cc` | 2026-07-19T21:14:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29703910361 |
| System3 Secure Install Credential Audit | 29703910386 | failure | `267e08ae48cc` | 2026-07-19T21:11:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29703910386 |
| System3 Autopilot Proof Board | 29703890613 | failure | `267e08ae48cc` | 2026-07-19T21:11:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29703890613 |
| Dashboard Visual Loading Postflight | 29703910344 | failure | `267e08ae48cc` | 2026-07-19T21:11:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29703910344 |
| System3 Experimental Solution Planner | 29703910875 | failure | `267e08ae48cc` | 2026-07-19T21:11:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29703910875 |
| Dashboard Visual Proof Strict Gate | 29703910357 | failure | `267e08ae48cc` | 2026-07-19T21:11:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29703910357 |
| Dashboard Visible Settle Proof | 29703671693 | failure | `e99c7aeb927b` | 2026-07-19T21:09:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29703671693 |
| System3 Windows Self-Hosted Full Proof | 29703675518 | failure | `e99c7aeb927b` | 2026-07-19T21:09:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29703675518 |
| Dashboard Visible Proof Current | 29703393913 | failure | `ed56c6577110` | 2026-07-19T21:06:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29703393913 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29703998182 | in_progress | 2026-07-19T21:15:09Z |
| Dashboard Visible Issue Tracker | 29703910854 | pending | 2026-07-19T21:11:31Z |
| Dashboard Visible Auth-Resilient Proof | 29703755647 | in_progress | 2026-07-19T21:06:16Z |

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
