# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T06:40:03.843872Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29633960638 conclusion=failure commit=f8099b753802
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29633960888 conclusion=failure commit=f8099b753802
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29634025906 conclusion=failure commit=57ddfbe687d5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29633755792 conclusion=failure commit=70a9027e4817
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29634036519 conclusion=failure commit=afdd389e7eb5
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29634052107 conclusion=failure commit=ae20b443e8e8
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29634036507 conclusion=failure commit=afdd389e7eb5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29634025892 conclusion=failure commit=57ddfbe687d5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29634025905 conclusion=failure commit=57ddfbe687d5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29633298893 conclusion=failure commit=f9f9f122cb89
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
| System3 Windows Self-Hosted Full Proof | 29633960638 | failure | `f8099b753802` | 2026-07-18T06:31:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29633960638 |
| Dashboard Visible Settle Proof | 29633960888 | failure | `f8099b753802` | 2026-07-18T06:31:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29633960888 |
| Dashboard Shell Diagnostic | 29634025906 | failure | `57ddfbe687d5` | 2026-07-18T06:30:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29634025906 |
| Dashboard Visible Proof Current | 29633755792 | failure | `70a9027e4817` | 2026-07-18T06:30:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29633755792 |
| System3 Autopilot Proof Board | 29634036519 | failure | `afdd389e7eb5` | 2026-07-18T06:28:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29634036519 |
| System3 Experimental Solution Planner | 29634052107 | failure | `ae20b443e8e8` | 2026-07-18T06:28:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29634052107 |
| System3 Secure Install Credential Audit | 29634036507 | failure | `afdd389e7eb5` | 2026-07-18T06:28:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29634036507 |
| Dashboard Visual Loading Postflight | 29634025892 | failure | `57ddfbe687d5` | 2026-07-18T06:27:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29634025892 |
| Dashboard Visual Proof Strict Gate | 29634025905 | failure | `57ddfbe687d5` | 2026-07-18T06:27:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29634025905 |
| Dashboard Visible Proof Warmed | 29633298893 | failure | `f9f9f122cb89` | 2026-07-18T06:03:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29633298893 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29634032219 | in_progress | 2026-07-18T06:37:39Z |
| System3 Safe Repair Runner | 29634225352 | in_progress | 2026-07-18T06:35:05Z |
| Dashboard Visible Auth-Resilient Proof | 29634029172 | in_progress | 2026-07-18T06:27:42Z |

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
