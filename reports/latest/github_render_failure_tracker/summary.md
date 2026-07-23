# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T19:30:51.788224Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30037305472 conclusion=failure commit=8645b2b2f46a
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30036813518 conclusion=failure commit=bce75f723802
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30037051195 conclusion=failure commit=aed42e6b9ede
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30036794299 conclusion=failure commit=bce75f723802
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30036355129 conclusion=failure commit=0727a03cd487
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30037132690 conclusion=failure commit=f6ab0e2c9765
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30037079483 conclusion=failure commit=575f65218ee7
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30037075894 conclusion=failure commit=575f65218ee7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30037050957 conclusion=failure commit=aed42e6b9ede
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
| Dashboard Visual Proof Strict Gate | 30037305472 | failure | `8645b2b2f46a` | 2026-07-23T19:17:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30037305472 |
| System3 Windows Self-Hosted Full Proof | 30036813518 | failure | `bce75f723802` | 2026-07-23T19:16:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30036813518 |
| Dashboard Shell Diagnostic | 30037051195 | failure | `aed42e6b9ede` | 2026-07-23T19:16:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30037051195 |
| Dashboard Visible Settle Proof | 30036794299 | failure | `bce75f723802` | 2026-07-23T19:15:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30036794299 |
| Dashboard Visible Proof Current | 30036355129 | failure | `0727a03cd487` | 2026-07-23T19:15:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30036355129 |
| System3 Experimental Solution Planner | 30037132690 | failure | `f6ab0e2c9765` | 2026-07-23T19:14:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30037132690 |
| System3 Autopilot Proof Board | 30037079483 | failure | `575f65218ee7` | 2026-07-23T19:14:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30037079483 |
| System3 Secure Install Credential Audit | 30037075894 | failure | `575f65218ee7` | 2026-07-23T19:13:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30037075894 |
| Dashboard Visual Loading Postflight | 30037050957 | failure | `aed42e6b9ede` | 2026-07-23T19:13:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30037050957 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 30038060406 | in_progress | 2026-07-23T19:27:50Z |
| Dashboard Visible Issue Tracker | 30037055800 | in_progress | 2026-07-23T19:19:43Z |
| Dashboard Visible Auth-Resilient Proof | 30037214571 | in_progress | 2026-07-23T19:15:29Z |

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
