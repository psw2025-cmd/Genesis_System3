# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T12:33:25.180650Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30006889662 conclusion=failure commit=75325f8f2b0c
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30006915483 conclusion=failure commit=cc5f4116a0a7
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30006956073 conclusion=failure commit=35c0d2d36aa5
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30006915380 conclusion=failure commit=cc5f4116a0a7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30006889538 conclusion=failure commit=75325f8f2b0c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30006889536 conclusion=failure commit=75325f8f2b0c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30005926028 conclusion=failure commit=5657aa0e8f41
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
| Dashboard Shell Diagnostic | 30006889662 | failure | `75325f8f2b0c` | 2026-07-23T12:28:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30006889662 |
| System3 Autopilot Proof Board | 30006915483 | failure | `cc5f4116a0a7` | 2026-07-23T12:26:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30006915483 |
| System3 Experimental Solution Planner | 30006956073 | failure | `35c0d2d36aa5` | 2026-07-23T12:26:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30006956073 |
| System3 Secure Install Credential Audit | 30006915380 | failure | `cc5f4116a0a7` | 2026-07-23T12:25:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30006915380 |
| Dashboard Visual Proof Strict Gate | 30006889538 | failure | `75325f8f2b0c` | 2026-07-23T12:25:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30006889538 |
| Dashboard Visual Loading Postflight | 30006889536 | failure | `75325f8f2b0c` | 2026-07-23T12:25:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30006889536 |
| Dashboard Visible Proof Current | 30005926028 | failure | `5657aa0e8f41` | 2026-07-23T12:22:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30005926028 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 30006896363 | in_progress | 2026-07-23T12:31:23Z |
| System3 Safe Repair Runner | 30007073427 | in_progress | 2026-07-23T12:28:21Z |

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
