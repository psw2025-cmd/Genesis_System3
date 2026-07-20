# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T21:25:48.070755Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `8`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `20`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29779306150 conclusion=failure commit=cb9534be57bf
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29779482322 conclusion=failure commit=ef16a5975289
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29779259781 conclusion=failure commit=cb9534be57bf
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29779506107 conclusion=failure commit=8f21b271fa2b
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29779545968 conclusion=failure commit=6a119804fbcd
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29779506278 conclusion=failure commit=8f21b271fa2b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29779482630 conclusion=failure commit=ef16a5975289
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29779481958 conclusion=failure commit=ef16a5975289
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
| System3 Windows Self-Hosted Full Proof | 29779306150 | failure | `cb9534be57bf` | 2026-07-20T21:25:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29779306150 |
| Dashboard Shell Diagnostic | 29779482322 | failure | `ef16a5975289` | 2026-07-20T21:18:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29779482322 |
| Dashboard Visible Settle Proof | 29779259781 | failure | `cb9534be57bf` | 2026-07-20T21:18:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29779259781 |
| System3 Autopilot Proof Board | 29779506107 | failure | `8f21b271fa2b` | 2026-07-20T21:16:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29779506107 |
| System3 Experimental Solution Planner | 29779545968 | failure | `6a119804fbcd` | 2026-07-20T21:16:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29779545968 |
| System3 Secure Install Credential Audit | 29779506278 | failure | `8f21b271fa2b` | 2026-07-20T21:16:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29779506278 |
| Dashboard Visual Loading Postflight | 29779482630 | failure | `ef16a5975289` | 2026-07-20T21:15:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29779482630 |
| Dashboard Visual Proof Strict Gate | 29779481958 | failure | `ef16a5975289` | 2026-07-20T21:15:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29779481958 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29779944010 | in_progress | 2026-07-20T21:23:25Z |
| Dashboard Visible Issue Tracker | 29779498276 | in_progress | 2026-07-20T21:19:00Z |
| Dashboard Visible Auth-Resilient Proof | 29779564377 | in_progress | 2026-07-20T21:16:59Z |

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
