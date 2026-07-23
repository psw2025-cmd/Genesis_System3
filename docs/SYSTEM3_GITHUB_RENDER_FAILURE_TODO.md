# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T23:20:01.535726Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30052119147 conclusion=failure commit=4f57d6072322
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30052095383 conclusion=failure commit=200bc63f3ba6
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30052140642 conclusion=failure commit=4f57d6072322
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30052234126 conclusion=failure commit=d8b659f5805f
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30052160412 conclusion=failure commit=10a194a2fb28
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30051543403 conclusion=failure commit=3a620672e9ea
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30052196145 conclusion=failure commit=c57cb8b7dc8a
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30052158894 conclusion=failure commit=10a194a2fb28
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30052140648 conclusion=failure commit=4f57d6072322
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
| System3 Windows Self-Hosted Full Proof | 30052119147 | failure | `4f57d6072322` | 2026-07-23T23:12:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30052119147 |
| Dashboard Visible Settle Proof | 30052095383 | failure | `200bc63f3ba6` | 2026-07-23T23:11:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30052095383 |
| Dashboard Shell Diagnostic | 30052140642 | failure | `4f57d6072322` | 2026-07-23T23:09:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30052140642 |
| Dashboard Visual Proof Strict Gate | 30052234126 | failure | `d8b659f5805f` | 2026-07-23T23:08:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30052234126 |
| System3 Autopilot Proof Board | 30052160412 | failure | `10a194a2fb28` | 2026-07-23T23:07:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30052160412 |
| Dashboard Visible Proof Current | 30051543403 | failure | `3a620672e9ea` | 2026-07-23T23:07:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30051543403 |
| System3 Experimental Solution Planner | 30052196145 | failure | `c57cb8b7dc8a` | 2026-07-23T23:07:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30052196145 |
| System3 Secure Install Credential Audit | 30052158894 | failure | `10a194a2fb28` | 2026-07-23T23:06:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30052158894 |
| Dashboard Visual Loading Postflight | 30052140648 | failure | `4f57d6072322` | 2026-07-23T23:06:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30052140648 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 30052688182 | in_progress | 2026-07-23T23:16:34Z |
| Dashboard Visible Issue Tracker | 30052138195 | in_progress | 2026-07-23T23:09:50Z |
| Dashboard Visible Auth-Resilient Proof | 30052253102 | in_progress | 2026-07-23T23:08:23Z |

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
