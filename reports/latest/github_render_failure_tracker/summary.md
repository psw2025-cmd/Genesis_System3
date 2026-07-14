# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-14T13:33:12.395649Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `18`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29336700861 conclusion=failure commit=77eebea0ed51
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29336742846 conclusion=failure commit=03bec1f18d72
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29336670519 conclusion=failure commit=a1697905e781
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29336699029 conclusion=failure commit=77eebea0ed51
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29336670761 conclusion=failure commit=a1697905e781
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29336670792 conclusion=failure commit=a1697905e781
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
| System3 Autopilot Proof Board | 29336700861 | failure | `77eebea0ed51` | 2026-07-14T13:30:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29336700861 |
| System3 Experimental Solution Planner | 29336742846 | failure | `03bec1f18d72` | 2026-07-14T13:30:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29336742846 |
| Dashboard Shell Diagnostic | 29336670519 | failure | `a1697905e781` | 2026-07-14T13:30:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29336670519 |
| System3 Secure Install Credential Audit | 29336699029 | failure | `77eebea0ed51` | 2026-07-14T13:29:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29336699029 |
| Dashboard Visual Proof Strict Gate | 29336670761 | failure | `a1697905e781` | 2026-07-14T13:29:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29336670761 |
| Dashboard Visual Loading Postflight | 29336670792 | failure | `a1697905e781` | 2026-07-14T13:29:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29336670792 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29336686987 | in_progress | 2026-07-14T13:31:25Z |
| System3 Safe Repair Runner | 29336742828 | in_progress | 2026-07-14T13:30:27Z |

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
