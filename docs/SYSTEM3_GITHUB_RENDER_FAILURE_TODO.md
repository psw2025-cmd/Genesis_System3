# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T08:53:50.675041Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `5`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29904315629 conclusion=failure commit=e51d7942cbcd
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29904387132 conclusion=failure commit=e46c97296a85
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29904331331 conclusion=failure commit=e9e0ffdbb51c
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=29904355302 conclusion=failure commit=ff3cdbd924b0
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29904315482 conclusion=failure commit=e51d7942cbcd
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29904315480 conclusion=failure commit=e51d7942cbcd
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29904315510 conclusion=failure commit=e51d7942cbcd
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
| Dashboard Shell Diagnostic | 29904315629 | failure | `e51d7942cbcd` | 2026-07-22T08:34:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29904315629 |
| System3 Experimental Solution Planner | 29904387132 | failure | `e46c97296a85` | 2026-07-22T08:32:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29904387132 |
| System3 Autopilot Proof Board | 29904331331 | failure | `e9e0ffdbb51c` | 2026-07-22T08:32:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29904331331 |
| System3 Broker Chain Semantic Gate | 29904355302 | failure | `ff3cdbd924b0` | 2026-07-22T08:32:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29904355302 |
| System3 Secure Install Credential Audit | 29904315482 | failure | `e51d7942cbcd` | 2026-07-22T08:31:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29904315482 |
| Dashboard Visual Proof Strict Gate | 29904315480 | failure | `e51d7942cbcd` | 2026-07-22T08:31:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29904315480 |
| Dashboard Visual Loading Postflight | 29904315510 | failure | `e51d7942cbcd` | 2026-07-22T08:31:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29904315510 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 29905656151 | in_progress | 2026-07-22T08:52:01Z |
| Permanent Repo Render Safety | 29905477051 | in_progress | 2026-07-22T08:49:18Z |
| System3 Safe Repair Runner | 29905441777 | in_progress | 2026-07-22T08:48:44Z |
| Dashboard Visible Issue Tracker | 29904318193 | in_progress | 2026-07-22T08:43:22Z |
| System3 Full Auto Truth | 29903556607 | in_progress | 2026-07-22T08:19:49Z |

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
