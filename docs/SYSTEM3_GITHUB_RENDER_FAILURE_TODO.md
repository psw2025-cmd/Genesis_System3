# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-17T21:16:45.123512Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29613962250 conclusion=failure commit=eb1ed02e30f7
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29613916642 conclusion=failure commit=fc81a71384cd
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29613962216 conclusion=failure commit=eb1ed02e30f7
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29613962175 conclusion=failure commit=eb1ed02e30f7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29613962166 conclusion=failure commit=eb1ed02e30f7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29613962270 conclusion=failure commit=eb1ed02e30f7
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29613462316 conclusion=failure commit=2c65d68a3ae3
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29613450415 conclusion=failure commit=2c65d68a3ae3
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29612940787 conclusion=failure commit=cb6254e47960
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
| Dashboard Shell Diagnostic | 29613962250 | failure | `eb1ed02e30f7` | 2026-07-17T21:16:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29613962250 |
| System3 Autopilot Proof Board | 29613916642 | failure | `fc81a71384cd` | 2026-07-17T21:13:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29613916642 |
| System3 Secure Install Credential Audit | 29613962216 | failure | `eb1ed02e30f7` | 2026-07-17T21:13:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29613962216 |
| System3 Experimental Solution Planner | 29613962175 | failure | `eb1ed02e30f7` | 2026-07-17T21:13:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29613962175 |
| Dashboard Visual Loading Postflight | 29613962166 | failure | `eb1ed02e30f7` | 2026-07-17T21:13:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29613962166 |
| Dashboard Visual Proof Strict Gate | 29613962270 | failure | `eb1ed02e30f7` | 2026-07-17T21:13:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29613962270 |
| System3 Windows Self-Hosted Full Proof | 29613462316 | failure | `2c65d68a3ae3` | 2026-07-17T21:11:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29613462316 |
| Dashboard Visible Settle Proof | 29613450415 | failure | `2c65d68a3ae3` | 2026-07-17T21:10:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29613450415 |
| Dashboard Visible Proof Current | 29612940787 | failure | `cb6254e47960` | 2026-07-17T21:07:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29612940787 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29614032919 | in_progress | 2026-07-17T21:15:00Z |
| Dashboard Visible Issue Tracker | 29613959260 | pending | 2026-07-17T21:13:09Z |
| Dashboard Visible Auth-Resilient Proof | 29613588830 | in_progress | 2026-07-17T21:06:41Z |

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
