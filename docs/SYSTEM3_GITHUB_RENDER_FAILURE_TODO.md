# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T12:19:00.424639Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29686455505 conclusion=failure commit=a2b73e82173d
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29686468538 conclusion=failure commit=23977e5f37f3
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29686302194 conclusion=failure commit=f2ebb57d2f0c
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29686485019 conclusion=failure commit=0cdf1bf1fa9d
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29686468561 conclusion=failure commit=23977e5f37f3
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29686455538 conclusion=failure commit=a2b73e82173d
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29686455520 conclusion=failure commit=a2b73e82173d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29686039054 conclusion=failure commit=3ba121934400
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
| Dashboard Shell Diagnostic | 29686455505 | failure | `a2b73e82173d` | 2026-07-19T12:12:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29686455505 |
| System3 Autopilot Proof Board | 29686468538 | failure | `23977e5f37f3` | 2026-07-19T12:10:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29686468538 |
| Dashboard Visible Settle Proof | 29686302194 | failure | `f2ebb57d2f0c` | 2026-07-19T12:10:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29686302194 |
| System3 Experimental Solution Planner | 29686485019 | failure | `0cdf1bf1fa9d` | 2026-07-19T12:10:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29686485019 |
| System3 Secure Install Credential Audit | 29686468561 | failure | `23977e5f37f3` | 2026-07-19T12:10:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29686468561 |
| Dashboard Visual Loading Postflight | 29686455538 | failure | `a2b73e82173d` | 2026-07-19T12:09:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29686455538 |
| Dashboard Visual Proof Strict Gate | 29686455520 | failure | `a2b73e82173d` | 2026-07-19T12:09:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29686455520 |
| Dashboard Visible Proof Current | 29686039054 | failure | `3ba121934400` | 2026-07-19T12:08:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29686039054 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29686594025 | in_progress | 2026-07-19T12:14:23Z |
| Dashboard Visible Issue Tracker | 29686457731 | in_progress | 2026-07-19T12:12:28Z |
| System3 Windows Self-Hosted Full Proof | 29686303369 | in_progress | 2026-07-19T12:08:50Z |
| Dashboard Visible Auth-Resilient Proof | 29686360002 | in_progress | 2026-07-19T12:06:04Z |

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
