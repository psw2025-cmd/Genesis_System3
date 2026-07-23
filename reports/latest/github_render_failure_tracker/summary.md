# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T22:21:49.883092Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `8`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `12`
TODO count: `20`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30049538843 conclusion=failure commit=c89506c10b22
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30049573703 conclusion=failure commit=fae6d385e4e8
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30049538990 conclusion=failure commit=c89506c10b22
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30049508301 conclusion=failure commit=3cba6ab7999a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30049508350 conclusion=failure commit=3cba6ab7999a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30048732720 conclusion=failure commit=46cf645e712d
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30048748690 conclusion=failure commit=46cf645e712d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30048135560 conclusion=failure commit=5b664031b4b9
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
| System3 Autopilot Proof Board | 30049538843 | failure | `c89506c10b22` | 2026-07-23T22:21:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30049538843 |
| System3 Experimental Solution Planner | 30049573703 | failure | `fae6d385e4e8` | 2026-07-23T22:21:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30049573703 |
| System3 Secure Install Credential Audit | 30049538990 | failure | `c89506c10b22` | 2026-07-23T22:20:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30049538990 |
| Dashboard Visual Proof Strict Gate | 30049508301 | failure | `3cba6ab7999a` | 2026-07-23T22:20:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30049508301 |
| Dashboard Visual Loading Postflight | 30049508350 | failure | `3cba6ab7999a` | 2026-07-23T22:20:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30049508350 |
| Dashboard Visible Settle Proof | 30048732720 | failure | `46cf645e712d` | 2026-07-23T22:13:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30048732720 |
| System3 Windows Self-Hosted Full Proof | 30048748690 | failure | `46cf645e712d` | 2026-07-23T22:12:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30048748690 |
| Dashboard Visible Proof Current | 30048135560 | failure | `5b664031b4b9` | 2026-07-23T22:09:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30048135560 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 30049573813 | in_progress | 2026-07-23T22:21:24Z |
| Dashboard Shell Diagnostic | 30049508371 | in_progress | 2026-07-23T22:20:04Z |
| Dashboard Visible Issue Tracker | 30048885135 | in_progress | 2026-07-23T22:20:01Z |
| Dashboard Visible Auth-Resilient Proof | 30048957115 | in_progress | 2026-07-23T22:10:42Z |

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
