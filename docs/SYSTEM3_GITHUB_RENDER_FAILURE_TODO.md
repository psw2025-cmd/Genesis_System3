# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T22:18:13.811533Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29705758971 conclusion=failure commit=feaeb1808e74
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29705758960 conclusion=failure commit=feaeb1808e74
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29705737362 conclusion=failure commit=59a7d41e6040
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29705758992 conclusion=failure commit=feaeb1808e74
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29705758954 conclusion=failure commit=feaeb1808e74
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29705758967 conclusion=failure commit=feaeb1808e74
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29705484693 conclusion=failure commit=57c79d41eaa0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29705466272 conclusion=failure commit=f48f6db018c9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29705210867 conclusion=failure commit=7c760e2f94a1
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
| Dashboard Shell Diagnostic | 29705758971 | failure | `feaeb1808e74` | 2026-07-19T22:16:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29705758971 |
| System3 Secure Install Credential Audit | 29705758960 | failure | `feaeb1808e74` | 2026-07-19T22:13:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29705758960 |
| System3 Autopilot Proof Board | 29705737362 | failure | `59a7d41e6040` | 2026-07-19T22:13:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29705737362 |
| Dashboard Visual Proof Strict Gate | 29705758992 | failure | `feaeb1808e74` | 2026-07-19T22:13:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29705758992 |
| System3 Experimental Solution Planner | 29705758954 | failure | `feaeb1808e74` | 2026-07-19T22:13:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29705758954 |
| Dashboard Visual Loading Postflight | 29705758967 | failure | `feaeb1808e74` | 2026-07-19T22:13:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29705758967 |
| System3 Windows Self-Hosted Full Proof | 29705484693 | failure | `57c79d41eaa0` | 2026-07-19T22:10:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29705484693 |
| Dashboard Visible Settle Proof | 29705466272 | failure | `f48f6db018c9` | 2026-07-19T22:09:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29705466272 |
| Dashboard Visible Proof Current | 29705210867 | failure | `7c760e2f94a1` | 2026-07-19T22:07:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29705210867 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29705814302 | in_progress | 2026-07-19T22:15:43Z |
| Dashboard Visible Issue Tracker | 29705757477 | pending | 2026-07-19T22:13:16Z |
| Dashboard Visible Auth-Resilient Proof | 29705568246 | in_progress | 2026-07-19T22:06:54Z |

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
