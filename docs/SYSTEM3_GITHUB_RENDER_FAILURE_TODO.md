# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T17:20:57.204762Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29653454140 conclusion=failure commit=ea550992ba2a
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29653255608 conclusion=failure commit=c45808ce3776
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29653435505 conclusion=failure commit=3f77c4d7b4c7
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29653454167 conclusion=failure commit=ea550992ba2a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29653454148 conclusion=failure commit=ea550992ba2a
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29653454119 conclusion=failure commit=ea550992ba2a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29653454188 conclusion=failure commit=ea550992ba2a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29653248418 conclusion=failure commit=b5e583d24b80
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29652923602 conclusion=failure commit=0287030f679a
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
| Dashboard Shell Diagnostic | 29653454140 | failure | `ea550992ba2a` | 2026-07-18T17:15:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29653454140 |
| System3 Windows Self-Hosted Full Proof | 29653255608 | failure | `c45808ce3776` | 2026-07-18T17:13:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29653255608 |
| System3 Autopilot Proof Board | 29653435505 | failure | `3f77c4d7b4c7` | 2026-07-18T17:12:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29653435505 |
| System3 Secure Install Credential Audit | 29653454167 | failure | `ea550992ba2a` | 2026-07-18T17:12:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29653454167 |
| Dashboard Visual Loading Postflight | 29653454148 | failure | `ea550992ba2a` | 2026-07-18T17:12:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29653454148 |
| System3 Experimental Solution Planner | 29653454119 | failure | `ea550992ba2a` | 2026-07-18T17:12:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29653454119 |
| Dashboard Visual Proof Strict Gate | 29653454188 | failure | `ea550992ba2a` | 2026-07-18T17:12:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29653454188 |
| Dashboard Visible Settle Proof | 29653248418 | failure | `b5e583d24b80` | 2026-07-18T17:11:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29653248418 |
| Dashboard Visible Proof Current | 29652923602 | failure | `0287030f679a` | 2026-07-18T17:07:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29652923602 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29653662201 | in_progress | 2026-07-18T17:19:15Z |
| Dashboard Visible Issue Tracker | 29653453581 | pending | 2026-07-18T17:12:08Z |
| Dashboard Visible Auth-Resilient Proof | 29653340783 | in_progress | 2026-07-18T17:08:33Z |

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
