# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T14:41:22.261969Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29928553971 conclusion=failure commit=712d76b0c72f
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29928773921 conclusion=failure commit=5b198c51c23e
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29928773954 conclusion=failure commit=5b198c51c23e
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29928773782 conclusion=failure commit=5b198c51c23e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29928776295 conclusion=failure commit=5b198c51c23e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29928774512 conclusion=failure commit=5b198c51c23e
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29928652722 conclusion=failure commit=7df2f1121841
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29926287941 conclusion=failure commit=8d1cff8014d9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29926584286 conclusion=failure commit=8d1cff8014d9
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29926412323 conclusion=failure commit=8d1cff8014d9
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
| Dashboard Visible Issue Tracker | 29928553971 | failure | `712d76b0c72f` | 2026-07-22T14:40:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29928553971 |
| Dashboard Shell Diagnostic | 29928773921 | failure | `5b198c51c23e` | 2026-07-22T14:32:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29928773921 |
| System3 Secure Install Credential Audit | 29928773954 | failure | `5b198c51c23e` | 2026-07-22T14:29:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29928773954 |
| System3 Experimental Solution Planner | 29928773782 | failure | `5b198c51c23e` | 2026-07-22T14:28:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29928773782 |
| Dashboard Visual Loading Postflight | 29928776295 | failure | `5b198c51c23e` | 2026-07-22T14:28:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29928776295 |
| Dashboard Visual Proof Strict Gate | 29928774512 | failure | `5b198c51c23e` | 2026-07-22T14:28:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29928774512 |
| System3 Autopilot Proof Board | 29928652722 | failure | `7df2f1121841` | 2026-07-22T14:28:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29928652722 |
| Dashboard Visible Auth-Resilient Proof | 29926287941 | failure | `8d1cff8014d9` | 2026-07-22T14:16:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29926287941 |
| Dashboard Visible Proof Warmed | 29926584286 | failure | `8d1cff8014d9` | 2026-07-22T14:02:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29926584286 |
| System3 Backend Live Simulation Proof | 29926412323 | failure | `8d1cff8014d9` | 2026-07-22T13:59:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29926412323 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29929516509 | in_progress | 2026-07-22T14:37:57Z |

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
