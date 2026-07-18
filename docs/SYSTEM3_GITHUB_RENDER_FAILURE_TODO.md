# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T18:19:03.769096Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29655496753 conclusion=failure commit=94f3af1a45c9
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29655496775 conclusion=failure commit=94f3af1a45c9
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29655498964 conclusion=failure commit=94f3af1a45c9
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29655496750 conclusion=failure commit=94f3af1a45c9
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29655496741 conclusion=failure commit=94f3af1a45c9
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29655469604 conclusion=failure commit=9523452a9af8
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29655112724 conclusion=failure commit=1d8dc5a1f6d8
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29655106146 conclusion=failure commit=1d8dc5a1f6d8
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29654864755 conclusion=failure commit=18d0a8f08a0a
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
| Dashboard Shell Diagnostic | 29655496753 | failure | `94f3af1a45c9` | 2026-07-18T18:18:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29655496753 |
| System3 Secure Install Credential Audit | 29655496775 | failure | `94f3af1a45c9` | 2026-07-18T18:15:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29655496775 |
| System3 Experimental Solution Planner | 29655498964 | failure | `94f3af1a45c9` | 2026-07-18T18:15:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29655498964 |
| Dashboard Visual Loading Postflight | 29655496750 | failure | `94f3af1a45c9` | 2026-07-18T18:15:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29655496750 |
| Dashboard Visual Proof Strict Gate | 29655496741 | failure | `94f3af1a45c9` | 2026-07-18T18:15:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29655496741 |
| System3 Autopilot Proof Board | 29655469604 | failure | `9523452a9af8` | 2026-07-18T18:15:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29655469604 |
| System3 Windows Self-Hosted Full Proof | 29655112724 | failure | `1d8dc5a1f6d8` | 2026-07-18T18:10:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29655112724 |
| Dashboard Visible Settle Proof | 29655106146 | failure | `1d8dc5a1f6d8` | 2026-07-18T18:09:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29655106146 |
| Dashboard Visible Proof Current | 29654864755 | failure | `18d0a8f08a0a` | 2026-07-18T18:07:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29654864755 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29655498967 | in_progress | 2026-07-18T18:15:24Z |
| Dashboard Visible Issue Tracker | 29655499053 | pending | 2026-07-18T18:15:13Z |
| Dashboard Visible Auth-Resilient Proof | 29655202824 | in_progress | 2026-07-18T18:06:08Z |

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
