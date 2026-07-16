# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-16T22:21:21.788927Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29538447883 conclusion=failure commit=9452b3ed0553
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29538435892 conclusion=failure commit=9452b3ed0553
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29538554314 conclusion=failure commit=1399cd9e5a27
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29538641965 conclusion=failure commit=2099a36538dd
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29538577337 conclusion=failure commit=dbaf2f70046e
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29538613267 conclusion=failure commit=f093a2ab84dc
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29538574367 conclusion=failure commit=dbaf2f70046e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29537783921 conclusion=failure commit=7c243c48796d
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29538554683 conclusion=failure commit=1399cd9e5a27
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
| System3 Windows Self-Hosted Full Proof | 29538447883 | failure | `9452b3ed0553` | 2026-07-16T22:13:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29538447883 |
| Dashboard Visible Settle Proof | 29538435892 | failure | `9452b3ed0553` | 2026-07-16T22:12:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29538435892 |
| Dashboard Shell Diagnostic | 29538554314 | failure | `1399cd9e5a27` | 2026-07-16T22:11:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29538554314 |
| Dashboard Visual Proof Strict Gate | 29538641965 | failure | `2099a36538dd` | 2026-07-16T22:10:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29538641965 |
| System3 Autopilot Proof Board | 29538577337 | failure | `dbaf2f70046e` | 2026-07-16T22:10:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29538577337 |
| System3 Experimental Solution Planner | 29538613267 | failure | `f093a2ab84dc` | 2026-07-16T22:10:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29538613267 |
| System3 Secure Install Credential Audit | 29538574367 | failure | `dbaf2f70046e` | 2026-07-16T22:09:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29538574367 |
| Dashboard Visible Proof Current | 29537783921 | failure | `7c243c48796d` | 2026-07-16T22:09:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29537783921 |
| Dashboard Visual Loading Postflight | 29538554683 | failure | `1399cd9e5a27` | 2026-07-16T22:09:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29538554683 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29539098196 | in_progress | 2026-07-16T22:18:52Z |
| Dashboard Visible Issue Tracker | 29538554837 | in_progress | 2026-07-16T22:13:40Z |
| Dashboard Visible Auth-Resilient Proof | 29538669478 | in_progress | 2026-07-16T22:10:55Z |

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
