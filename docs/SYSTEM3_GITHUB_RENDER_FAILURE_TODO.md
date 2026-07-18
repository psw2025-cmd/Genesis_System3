# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T16:19:07.734661Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29651428549 conclusion=failure commit=c3939c9ac06e
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29651243432 conclusion=failure commit=6c7cfe7e00b3
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29651443042 conclusion=failure commit=3272b1d3f36a
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29651409664 conclusion=failure commit=ae2fd991b3a6
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29651236761 conclusion=failure commit=b72c9a34373d
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29651428524 conclusion=failure commit=c3939c9ac06e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29651428544 conclusion=failure commit=c3939c9ac06e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29651428518 conclusion=failure commit=c3939c9ac06e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29650942322 conclusion=failure commit=3e81a6ec236f
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
| Dashboard Shell Diagnostic | 29651428549 | failure | `c3939c9ac06e` | 2026-07-18T16:13:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29651428549 |
| System3 Windows Self-Hosted Full Proof | 29651243432 | failure | `6c7cfe7e00b3` | 2026-07-18T16:12:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29651243432 |
| System3 Experimental Solution Planner | 29651443042 | failure | `3272b1d3f36a` | 2026-07-18T16:10:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29651443042 |
| System3 Autopilot Proof Board | 29651409664 | failure | `ae2fd991b3a6` | 2026-07-18T16:10:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29651409664 |
| Dashboard Visible Settle Proof | 29651236761 | failure | `b72c9a34373d` | 2026-07-18T16:10:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29651236761 |
| System3 Secure Install Credential Audit | 29651428524 | failure | `c3939c9ac06e` | 2026-07-18T16:10:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29651428524 |
| Dashboard Visual Loading Postflight | 29651428544 | failure | `c3939c9ac06e` | 2026-07-18T16:10:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29651428544 |
| Dashboard Visual Proof Strict Gate | 29651428518 | failure | `c3939c9ac06e` | 2026-07-18T16:10:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29651428518 |
| Dashboard Visible Proof Current | 29650942322 | failure | `3e81a6ec236f` | 2026-07-18T16:07:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29650942322 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29651612711 | in_progress | 2026-07-18T16:16:31Z |
| Dashboard Visible Issue Tracker | 29651443035 | pending | 2026-07-18T16:10:46Z |
| Dashboard Visible Auth-Resilient Proof | 29651333349 | in_progress | 2026-07-18T16:07:26Z |

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
