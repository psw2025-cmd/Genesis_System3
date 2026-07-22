# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T16:31:17.612159Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29937624183 conclusion=failure commit=8383202ebf21
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29937653920 conclusion=failure commit=4cd5892c3aa6
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29937705977 conclusion=failure commit=213548fdae5e
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29937653944 conclusion=failure commit=4cd5892c3aa6
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29937624561 conclusion=failure commit=8383202ebf21
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29937624388 conclusion=failure commit=8383202ebf21
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29935321270 conclusion=failure commit=5a330c7b4519
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29935431350 conclusion=failure commit=d87ca888578d
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29935371862 conclusion=failure commit=d87ca888578d
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
| Dashboard Shell Diagnostic | 29937624183 | failure | `8383202ebf21` | 2026-07-22T16:24:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29937624183 |
| System3 Autopilot Proof Board | 29937653920 | failure | `4cd5892c3aa6` | 2026-07-22T16:22:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29937653920 |
| System3 Experimental Solution Planner | 29937705977 | failure | `213548fdae5e` | 2026-07-22T16:22:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29937705977 |
| System3 Secure Install Credential Audit | 29937653944 | failure | `4cd5892c3aa6` | 2026-07-22T16:22:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29937653944 |
| Dashboard Visual Proof Strict Gate | 29937624561 | failure | `8383202ebf21` | 2026-07-22T16:21:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29937624561 |
| Dashboard Visual Loading Postflight | 29937624388 | failure | `8383202ebf21` | 2026-07-22T16:21:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29937624388 |
| Dashboard Visible Auth-Resilient Proof | 29935321270 | failure | `5a330c7b4519` | 2026-07-22T16:09:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29935321270 |
| Dashboard Visible Proof Warmed | 29935431350 | failure | `d87ca888578d` | 2026-07-22T15:53:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29935431350 |
| System3 Backend Live Simulation Proof | 29935371862 | failure | `d87ca888578d` | 2026-07-22T15:52:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29935371862 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29938051945 | in_progress | 2026-07-22T16:27:47Z |
| Dashboard Visible Issue Tracker | 29937632673 | in_progress | 2026-07-22T16:26:36Z |

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
