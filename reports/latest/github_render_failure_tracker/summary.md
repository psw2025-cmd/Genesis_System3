# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-21T21:27:08.920497Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29869021306 conclusion=failure commit=b6b4a99c66aa
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29869205088 conclusion=failure commit=10c9e1727237
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29868724992 conclusion=failure commit=a574f40a18e6
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29869048083 conclusion=failure commit=ef73347f540a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29868685389 conclusion=failure commit=a574f40a18e6
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29869094205 conclusion=failure commit=5a08a07bf7e3
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29869046673 conclusion=failure commit=ef73347f540a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29869021198 conclusion=failure commit=b6b4a99c66aa
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29868169738 conclusion=failure commit=b39dee9a3a78
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
| Dashboard Shell Diagnostic | 29869021306 | failure | `b6b4a99c66aa` | 2026-07-21T21:15:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29869021306 |
| Dashboard Visual Proof Strict Gate | 29869205088 | failure | `10c9e1727237` | 2026-07-21T21:15:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29869205088 |
| System3 Windows Self-Hosted Full Proof | 29868724992 | failure | `a574f40a18e6` | 2026-07-21T21:14:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29868724992 |
| System3 Autopilot Proof Board | 29869048083 | failure | `ef73347f540a` | 2026-07-21T21:14:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29869048083 |
| Dashboard Visible Settle Proof | 29868685389 | failure | `a574f40a18e6` | 2026-07-21T21:13:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29868685389 |
| System3 Experimental Solution Planner | 29869094205 | failure | `5a08a07bf7e3` | 2026-07-21T21:13:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29869094205 |
| System3 Secure Install Credential Audit | 29869046673 | failure | `ef73347f540a` | 2026-07-21T21:13:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29869046673 |
| Dashboard Visual Loading Postflight | 29869021198 | failure | `b6b4a99c66aa` | 2026-07-21T21:12:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29869021198 |
| Dashboard Visible Proof Current | 29868169738 | failure | `b39dee9a3a78` | 2026-07-21T21:12:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29868169738 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29869791565 | in_progress | 2026-07-21T21:23:57Z |
| Dashboard Visible Issue Tracker | 29869017135 | in_progress | 2026-07-21T21:20:48Z |
| Dashboard Visible Auth-Resilient Proof | 29869326535 | in_progress | 2026-07-21T21:16:58Z |

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
