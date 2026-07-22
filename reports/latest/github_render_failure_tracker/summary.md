# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T19:30:36.851095Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29949927085 conclusion=failure commit=170f40e702d6
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29949837433 conclusion=failure commit=5cbee1ff6c07
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29950157300 conclusion=failure commit=d4c886b24585
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29949697793 conclusion=failure commit=0a961c2cd151
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29949917337 conclusion=failure commit=2627ff6e7de3
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29949245170 conclusion=failure commit=a7974daca46d
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29950026890 conclusion=failure commit=515ff8c9ab6c
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29949949551 conclusion=failure commit=c096f61085b8
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29949949925 conclusion=failure commit=c096f61085b8
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29949916325 conclusion=failure commit=2627ff6e7de3
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
| Dashboard Visible Issue Tracker | 29949927085 | failure | `170f40e702d6` | 2026-07-22T19:27:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29949927085 |
| System3 Windows Self-Hosted Full Proof | 29949837433 | failure | `5cbee1ff6c07` | 2026-07-22T19:18:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29949837433 |
| Dashboard Visual Proof Strict Gate | 29950157300 | failure | `d4c886b24585` | 2026-07-22T19:15:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29950157300 |
| Dashboard Visible Settle Proof | 29949697793 | failure | `0a961c2cd151` | 2026-07-22T19:14:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29949697793 |
| Dashboard Shell Diagnostic | 29949917337 | failure | `2627ff6e7de3` | 2026-07-22T19:14:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29949917337 |
| Dashboard Visible Proof Current | 29949245170 | failure | `a7974daca46d` | 2026-07-22T19:14:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29949245170 |
| System3 Experimental Solution Planner | 29950026890 | failure | `515ff8c9ab6c` | 2026-07-22T19:13:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29950026890 |
| System3 Autopilot Proof Board | 29949949551 | failure | `c096f61085b8` | 2026-07-22T19:12:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29949949551 |
| System3 Secure Install Credential Audit | 29949949925 | failure | `c096f61085b8` | 2026-07-22T19:12:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29949949925 |
| Dashboard Visual Loading Postflight | 29949916325 | failure | `2627ff6e7de3` | 2026-07-22T19:11:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29949916325 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29951083450 | in_progress | 2026-07-22T19:28:12Z |
| Dashboard Visible Auth-Resilient Proof | 29950281272 | in_progress | 2026-07-22T19:16:42Z |

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
