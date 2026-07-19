# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T16:19:56.837727Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29694136608 conclusion=failure commit=575214ab1b7c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29694118420 conclusion=failure commit=ea301a991929
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29694194150 conclusion=failure commit=b827360b145c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29693829144 conclusion=failure commit=a2d208f9eefe
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29694208923 conclusion=failure commit=69f3867e38fe
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29694227143 conclusion=failure commit=866ca1a36f02
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29694208241 conclusion=failure commit=69f3867e38fe
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29694210632 conclusion=failure commit=69f3867e38fe
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29694194186 conclusion=failure commit=b827360b145c
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
| System3 Windows Self-Hosted Full Proof | 29694136608 | failure | `575214ab1b7c` | 2026-07-19T16:13:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29694136608 |
| Dashboard Visible Settle Proof | 29694118420 | failure | `ea301a991929` | 2026-07-19T16:10:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29694118420 |
| Dashboard Shell Diagnostic | 29694194150 | failure | `b827360b145c` | 2026-07-19T16:09:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29694194150 |
| Dashboard Visible Proof Current | 29693829144 | failure | `a2d208f9eefe` | 2026-07-19T16:07:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29693829144 |
| System3 Autopilot Proof Board | 29694208923 | failure | `69f3867e38fe` | 2026-07-19T16:07:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29694208923 |
| System3 Experimental Solution Planner | 29694227143 | failure | `866ca1a36f02` | 2026-07-19T16:07:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29694227143 |
| System3 Secure Install Credential Audit | 29694208241 | failure | `69f3867e38fe` | 2026-07-19T16:07:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29694208241 |
| Dashboard Visual Proof Strict Gate | 29694210632 | failure | `69f3867e38fe` | 2026-07-19T16:06:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29694210632 |
| Dashboard Visual Loading Postflight | 29694194186 | failure | `b827360b145c` | 2026-07-19T16:06:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29694194186 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29694529517 | in_progress | 2026-07-19T16:16:27Z |
| Dashboard Visible Issue Tracker | 29694196790 | in_progress | 2026-07-19T16:13:31Z |
| Dashboard Visible Auth-Resilient Proof | 29694235784 | in_progress | 2026-07-19T16:07:40Z |

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
