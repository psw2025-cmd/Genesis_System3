# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-15T19:28:39.881053Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `14`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `26`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29444176256 conclusion=failure commit=e5af4f348bfe
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29444204706 conclusion=failure commit=45b7855581a6
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29444241099 conclusion=failure commit=8e17eae34224
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29444204763 conclusion=failure commit=45b7855581a6
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29444176059 conclusion=failure commit=e5af4f348bfe
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29444176231 conclusion=failure commit=e5af4f348bfe
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29443342082 conclusion=failure commit=228f20efbaa3
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29443361189 conclusion=failure commit=228f20efbaa3
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=29441359564 conclusion=cancelled commit=768dca97398e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29442695581 conclusion=failure commit=9f431338e055
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29441630501 conclusion=failure commit=ae4003de121b
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29441563990 conclusion=failure commit=ae4003de121b
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=29441443495 conclusion=failure commit=768dca97398e
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=29441424778 conclusion=failure commit=768dca97398e
- [ ] Fix Render endpoint /: HTTP status 503 status=503
- [ ] Fix Render endpoint /ui/: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/health: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/state: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/paper: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 503 status=503

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Shell Diagnostic | 29444176256 | failure | `e5af4f348bfe` | 2026-07-15T19:22:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29444176256 |
| System3 Autopilot Proof Board | 29444204706 | failure | `45b7855581a6` | 2026-07-15T19:22:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29444204706 |
| System3 Experimental Solution Planner | 29444241099 | failure | `8e17eae34224` | 2026-07-15T19:22:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29444241099 |
| System3 Secure Install Credential Audit | 29444204763 | failure | `45b7855581a6` | 2026-07-15T19:22:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29444204763 |
| Dashboard Visual Loading Postflight | 29444176059 | failure | `e5af4f348bfe` | 2026-07-15T19:21:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29444176059 |
| Dashboard Visual Proof Strict Gate | 29444176231 | failure | `e5af4f348bfe` | 2026-07-15T19:21:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29444176231 |
| Dashboard Visible Settle Proof | 29443342082 | failure | `228f20efbaa3` | 2026-07-15T19:14:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29443342082 |
| System3 Windows Self-Hosted Full Proof | 29443361189 | failure | `228f20efbaa3` | 2026-07-15T19:13:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29443361189 |
| Dashboard Visual Production Proof | 29441359564 | cancelled | `768dca97398e` | 2026-07-15T19:08:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29441359564 |
| Dashboard Visible Proof Current | 29442695581 | failure | `9f431338e055` | 2026-07-15T19:04:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29442695581 |
| Dashboard Visible Proof Warmed | 29441630501 | failure | `ae4003de121b` | 2026-07-15T18:43:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29441630501 |
| System3 Backend Live Simulation Proof | 29441563990 | failure | `ae4003de121b` | 2026-07-15T18:41:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29441563990 |
| System3 Render Worker Preflight | 29441443495 | failure | `768dca97398e` | 2026-07-15T18:39:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29441443495 |
| Dashboard Deploy Provenance Gate | 29441424778 | failure | `768dca97398e` | 2026-07-15T18:39:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29441424778 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29444506921 | in_progress | 2026-07-15T19:27:07Z |
| Dashboard Visible Issue Tracker | 29443478232 | in_progress | 2026-07-15T19:21:12Z |
| Dashboard Visible Auth-Resilient Proof | 29443656230 | in_progress | 2026-07-15T19:12:56Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 503 | HTTP status 503 | `none` |
| `/ui/` | 503 | HTTP status 503 | `none` |
| `/api/health` | 503 | HTTP status 503 | `none` |
| `/api/state` | 503 | HTTP status 503 | `none` |
| `/api/deploy/info` | 503 | HTTP status 503 | `none` |
| `/api/broker/diagnose` | 503 | HTTP status 503 | `none` |
| `/api/broker/funds` | 503 | HTTP status 503 | `none` |
| `/api/broker/holdings` | 503 | HTTP status 503 | `none` |
| `/api/broker/positions/live` | 503 | HTTP status 503 | `none` |
| `/api/scanner/top_contract_gainers` | 503 | HTTP status 503 | `none` |
| `/api/paper` | 503 | HTTP status 503 | `none` |
| `/api/ml/performance` | 503 | HTTP status 503 | `none` |
