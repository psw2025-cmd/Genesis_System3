# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-15T22:21:04.609475Z`
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

- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29454956081 conclusion=failure commit=90d1ca525e91
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29454930388 conclusion=failure commit=b6f789864017
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29454982731 conclusion=failure commit=4b6d52f0cf2e
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29454952116 conclusion=failure commit=90d1ca525e91
- [ ] Fix latest GitHub workflow 'Dashboard Visual Settle Normalizer' run=29454930390 conclusion=failure commit=b6f789864017
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29454930418 conclusion=failure commit=b6f789864017
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29454930274 conclusion=failure commit=b6f789864017
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29454267590 conclusion=failure commit=828adeb753a8
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29454289508 conclusion=failure commit=2afb587d9166
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29453675515 conclusion=failure commit=5fc3f87fef00
- [ ] Fix Render endpoint /: HTTP status 503 status=503
- [ ] Fix Render endpoint /ui/: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/health: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/state: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/paper: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 503 status=503

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Autopilot Proof Board | 29454956081 | failure | `90d1ca525e91` | 2026-07-15T22:19:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29454956081 |
| Dashboard Shell Diagnostic | 29454930388 | failure | `b6f789864017` | 2026-07-15T22:19:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29454930388 |
| System3 Experimental Solution Planner | 29454982731 | failure | `4b6d52f0cf2e` | 2026-07-15T22:19:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29454982731 |
| System3 Secure Install Credential Audit | 29454952116 | failure | `90d1ca525e91` | 2026-07-15T22:18:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29454952116 |
| Dashboard Visual Settle Normalizer | 29454930390 | failure | `b6f789864017` | 2026-07-15T22:18:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29454930390 |
| Dashboard Visual Loading Postflight | 29454930418 | failure | `b6f789864017` | 2026-07-15T22:18:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29454930418 |
| Dashboard Visual Proof Strict Gate | 29454930274 | failure | `b6f789864017` | 2026-07-15T22:18:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29454930274 |
| Dashboard Visible Settle Proof | 29454267590 | failure | `828adeb753a8` | 2026-07-15T22:12:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29454267590 |
| System3 Windows Self-Hosted Full Proof | 29454289508 | failure | `2afb587d9166` | 2026-07-15T22:12:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29454289508 |
| Dashboard Visible Proof Current | 29453675515 | failure | `5fc3f87fef00` | 2026-07-15T22:02:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29453675515 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29454982750 | in_progress | 2026-07-15T22:19:29Z |
| Dashboard Visible Issue Tracker | 29454311562 | in_progress | 2026-07-15T22:17:57Z |
| Dashboard Visible Auth-Resilient Proof | 29454472943 | in_progress | 2026-07-15T22:10:01Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 503 | HTTP status 503 | `none` |
| `/ui/` | 503 | HTTP status 503 | `none` |
| `/api/health` | 503 | HTTP status 503 | `none` |
| `/api/state` | 503 | HTTP status 503 | `none` |
| `/api/deploy/info` | 503 | HTTP status 503 | `none` |
| `/api/broker/diagnose` | 503 | HTTP status 503 | `none` |
| `/api/broker/funds` | 503 | HTTP status 503 | `none` |
| `/api/broker/holdings` | 503 | HTTP status 503 | `none` |
| `/api/broker/positions/live` | 503 | HTTP status 503 | `none` |
| `/api/scanner/top_contract_gainers` | 503 | HTTP status 503 | `none` |
| `/api/paper` | 503 | HTTP status 503 | `none` |
| `/api/ml/performance` | 503 | HTTP status 503 | `none` |
