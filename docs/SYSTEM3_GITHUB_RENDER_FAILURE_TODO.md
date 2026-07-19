# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T11:24:46.965141Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29684841236 conclusion=failure commit=c32d6eb47efd
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29684710923 conclusion=failure commit=b31b96d18d6d
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29684854163 conclusion=failure commit=0eb7f5b961b1
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29684860995 conclusion=failure commit=ab2997250e71
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29684854169 conclusion=failure commit=0eb7f5b961b1
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29684841257 conclusion=failure commit=c32d6eb47efd
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29684841272 conclusion=failure commit=c32d6eb47efd
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
| Dashboard Shell Diagnostic | 29684841236 | failure | `c32d6eb47efd` | 2026-07-19T11:19:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29684841236 |
| Dashboard Visible Settle Proof | 29684710923 | failure | `b31b96d18d6d` | 2026-07-19T11:18:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29684710923 |
| System3 Autopilot Proof Board | 29684854163 | failure | `0eb7f5b961b1` | 2026-07-19T11:18:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29684854163 |
| System3 Experimental Solution Planner | 29684860995 | failure | `ab2997250e71` | 2026-07-19T11:17:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29684860995 |
| System3 Secure Install Credential Audit | 29684854169 | failure | `0eb7f5b961b1` | 2026-07-19T11:17:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29684854169 |
| Dashboard Visual Loading Postflight | 29684841257 | failure | `c32d6eb47efd` | 2026-07-19T11:16:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29684841257 |
| Dashboard Visual Proof Strict Gate | 29684841272 | failure | `c32d6eb47efd` | 2026-07-19T11:16:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29684841272 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29685005724 | in_progress | 2026-07-19T11:23:00Z |
| Dashboard Visible Issue Tracker | 29684844002 | in_progress | 2026-07-19T11:22:53Z |
| System3 Windows Self-Hosted Full Proof | 29684729327 | in_progress | 2026-07-19T11:19:15Z |
| Dashboard Visible Auth-Resilient Proof | 29684850071 | in_progress | 2026-07-19T11:17:06Z |

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
