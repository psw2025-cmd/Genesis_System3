# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-17T17:25:33.427048Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29599065019 conclusion=failure commit=c4c5eee39096
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29598960827 conclusion=failure commit=ac056d3335b1
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29599071826 conclusion=failure commit=c4c5eee39096
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29598495510 conclusion=failure commit=1e7686ac4ac6
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29599210466 conclusion=failure commit=54dbd42909ba
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29599095914 conclusion=failure commit=fbe624b5ff1e
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29599131843 conclusion=failure commit=f299cd8b924a
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29599095266 conclusion=failure commit=fbe624b5ff1e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29599071792 conclusion=failure commit=c4c5eee39096
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
| System3 Windows Self-Hosted Full Proof | 29599065019 | failure | `c4c5eee39096` | 2026-07-17T17:19:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29599065019 |
| Dashboard Visible Settle Proof | 29598960827 | failure | `ac056d3335b1` | 2026-07-17T17:15:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29598960827 |
| Dashboard Shell Diagnostic | 29599071826 | failure | `c4c5eee39096` | 2026-07-17T17:14:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29599071826 |
| Dashboard Visible Proof Current | 29598495510 | failure | `1e7686ac4ac6` | 2026-07-17T17:14:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29598495510 |
| Dashboard Visual Proof Strict Gate | 29599210466 | failure | `54dbd42909ba` | 2026-07-17T17:13:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29599210466 |
| System3 Autopilot Proof Board | 29599095914 | failure | `fbe624b5ff1e` | 2026-07-17T17:12:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29599095914 |
| System3 Experimental Solution Planner | 29599131843 | failure | `f299cd8b924a` | 2026-07-17T17:12:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29599131843 |
| System3 Secure Install Credential Audit | 29599095266 | failure | `fbe624b5ff1e` | 2026-07-17T17:12:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29599095266 |
| Dashboard Visual Loading Postflight | 29599071792 | failure | `c4c5eee39096` | 2026-07-17T17:11:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29599071792 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29599821709 | in_progress | 2026-07-17T17:23:04Z |
| Dashboard Visible Issue Tracker | 29599083820 | in_progress | 2026-07-17T17:16:43Z |
| Dashboard Visible Auth-Resilient Proof | 29599164786 | in_progress | 2026-07-17T17:12:50Z |

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
