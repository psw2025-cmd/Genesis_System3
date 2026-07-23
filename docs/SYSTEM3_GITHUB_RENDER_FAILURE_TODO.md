# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T11:37:54.583166Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30003288673 conclusion=failure commit=9effef1be5a1
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30002670184 conclusion=failure commit=a8d9f4f050ca
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30003264824 conclusion=failure commit=9d99d91b4642
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30003288649 conclusion=failure commit=9effef1be5a1
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30003295570 conclusion=failure commit=9effef1be5a1
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30003288698 conclusion=failure commit=9effef1be5a1
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30003288628 conclusion=failure commit=9effef1be5a1
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
| Dashboard Shell Diagnostic | 30003288673 | failure | `9effef1be5a1` | 2026-07-23T11:32:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30003288673 |
| Dashboard Visible Proof Current | 30002670184 | failure | `a8d9f4f050ca` | 2026-07-23T11:31:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30002670184 |
| System3 Autopilot Proof Board | 30003264824 | failure | `9d99d91b4642` | 2026-07-23T11:29:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30003264824 |
| System3 Secure Install Credential Audit | 30003288649 | failure | `9effef1be5a1` | 2026-07-23T11:29:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30003288649 |
| System3 Experimental Solution Planner | 30003295570 | failure | `9effef1be5a1` | 2026-07-23T11:29:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30003295570 |
| Dashboard Visual Proof Strict Gate | 30003288698 | failure | `9effef1be5a1` | 2026-07-23T11:29:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30003288698 |
| Dashboard Visual Loading Postflight | 30003288628 | failure | `9effef1be5a1` | 2026-07-23T11:29:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30003288628 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 30003657065 | in_progress | 2026-07-23T11:35:16Z |
| Dashboard Visible Issue Tracker | 30003239488 | in_progress | 2026-07-23T11:28:56Z |
| System3 Full Auto Truth | 30002542060 | in_progress | 2026-07-23T11:17:06Z |

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
