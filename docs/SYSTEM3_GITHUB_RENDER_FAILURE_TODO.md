# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-21T13:32:40.869035Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29833676656 conclusion=failure commit=aa77fe696c02
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29833597467 conclusion=failure commit=d7b3b852ddfa
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29833721572 conclusion=failure commit=aa77fe696c02
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29833753632 conclusion=failure commit=265d4de199c3
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29833803431 conclusion=failure commit=bf41ec07dece
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29833751145 conclusion=failure commit=265d4de199c3
- [ ] Fix latest GitHub workflow 'Dashboard Visual Settle Normalizer' run=29833721965 conclusion=failure commit=aa77fe696c02
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29833721943 conclusion=failure commit=aa77fe696c02
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29833722124 conclusion=failure commit=aa77fe696c02
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
| System3 Windows Self-Hosted Full Proof | 29833676656 | failure | `aa77fe696c02` | 2026-07-21T13:21:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29833676656 |
| Dashboard Visible Settle Proof | 29833597467 | failure | `d7b3b852ddfa` | 2026-07-21T13:21:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29833597467 |
| Dashboard Shell Diagnostic | 29833721572 | failure | `aa77fe696c02` | 2026-07-21T13:19:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29833721572 |
| System3 Autopilot Proof Board | 29833753632 | failure | `265d4de199c3` | 2026-07-21T13:18:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29833753632 |
| System3 Experimental Solution Planner | 29833803431 | failure | `bf41ec07dece` | 2026-07-21T13:18:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29833803431 |
| System3 Secure Install Credential Audit | 29833751145 | failure | `265d4de199c3` | 2026-07-21T13:17:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29833751145 |
| Dashboard Visual Settle Normalizer | 29833721965 | failure | `aa77fe696c02` | 2026-07-21T13:17:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29833721965 |
| Dashboard Visual Loading Postflight | 29833721943 | failure | `aa77fe696c02` | 2026-07-21T13:16:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29833721943 |
| Dashboard Visual Proof Strict Gate | 29833722124 | failure | `aa77fe696c02` | 2026-07-21T13:16:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29833722124 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29834688923 | in_progress | 2026-07-21T13:29:56Z |
| Dashboard Visible Issue Tracker | 29833726109 | in_progress | 2026-07-21T13:24:45Z |
| Dashboard Visible Auth-Resilient Proof | 29834083725 | in_progress | 2026-07-21T13:21:51Z |

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
