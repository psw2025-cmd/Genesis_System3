# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T11:21:59.127851Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29642116256 conclusion=failure commit=bbc4ef691e1e
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29642234720 conclusion=failure commit=2d6e358eb5e6
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29642271617 conclusion=failure commit=7ead6d66eece
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29642246226 conclusion=failure commit=4fefdbe461a9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29642080043 conclusion=failure commit=bbc4ef691e1e
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29642246211 conclusion=failure commit=4fefdbe461a9
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29642234750 conclusion=failure commit=2d6e358eb5e6
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29642234732 conclusion=failure commit=2d6e358eb5e6
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
| System3 Windows Self-Hosted Full Proof | 29642116256 | failure | `bbc4ef691e1e` | 2026-07-18T11:18:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29642116256 |
| Dashboard Shell Diagnostic | 29642234720 | failure | `2d6e358eb5e6` | 2026-07-18T11:18:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29642234720 |
| System3 Experimental Solution Planner | 29642271617 | failure | `7ead6d66eece` | 2026-07-18T11:16:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29642271617 |
| System3 Autopilot Proof Board | 29642246226 | failure | `4fefdbe461a9` | 2026-07-18T11:16:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29642246226 |
| Dashboard Visible Settle Proof | 29642080043 | failure | `bbc4ef691e1e` | 2026-07-18T11:15:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29642080043 |
| System3 Secure Install Credential Audit | 29642246211 | failure | `4fefdbe461a9` | 2026-07-18T11:15:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29642246211 |
| Dashboard Visual Proof Strict Gate | 29642234750 | failure | `2d6e358eb5e6` | 2026-07-18T11:15:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29642234750 |
| Dashboard Visual Loading Postflight | 29642234732 | failure | `2d6e358eb5e6` | 2026-07-18T11:15:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29642234732 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29642355713 | in_progress | 2026-07-18T11:20:02Z |
| Dashboard Visible Issue Tracker | 29642240358 | in_progress | 2026-07-18T11:16:40Z |
| Dashboard Visible Auth-Resilient Proof | 29642198898 | in_progress | 2026-07-18T11:13:54Z |

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
