# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T08:54:01.882632Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `5`
Render failed endpoints: `12`
TODO count: `18`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29992584402 conclusion=failure commit=1a394f7ec26e
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29992802253 conclusion=failure commit=0b881774c3e8
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29992705470 conclusion=failure commit=36f1daace629
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29992584326 conclusion=failure commit=1a394f7ec26e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29992583995 conclusion=failure commit=1a394f7ec26e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29991166173 conclusion=failure commit=e8d0b6c24c38
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
| Dashboard Shell Diagnostic | 29992584402 | failure | `1a394f7ec26e` | 2026-07-23T08:53:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29992584402 |
| System3 Experimental Solution Planner | 29992802253 | failure | `0b881774c3e8` | 2026-07-23T08:52:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29992802253 |
| System3 Secure Install Credential Audit | 29992705470 | failure | `36f1daace629` | 2026-07-23T08:51:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29992705470 |
| Dashboard Visual Loading Postflight | 29992584326 | failure | `1a394f7ec26e` | 2026-07-23T08:50:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29992584326 |
| Dashboard Visual Proof Strict Gate | 29992583995 | failure | `1a394f7ec26e` | 2026-07-23T08:50:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29992583995 |
| Dashboard Visible Proof Current | 29991166173 | failure | `e8d0b6c24c38` | 2026-07-23T08:38:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29991166173 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29992802642 | in_progress | 2026-07-23T08:52:31Z |
| System3 Latest Truth Publish | 29992827523 | queued | 2026-07-23T08:52:10Z |
| Dashboard Visible Issue Tracker | 29992801846 | pending | 2026-07-23T08:51:52Z |
| System3 Autopilot Proof Board | 29992740709 | in_progress | 2026-07-23T08:51:12Z |
| Permanent Repo Render Safety | 29992533927 | in_progress | 2026-07-23T08:49:15Z |

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
