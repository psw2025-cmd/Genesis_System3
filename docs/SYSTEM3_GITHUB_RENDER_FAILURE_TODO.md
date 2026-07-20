# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T16:31:20.415523Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29759507668 conclusion=failure commit=3f7ade91368e
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29759542903 conclusion=failure commit=4a28ac1faaf9
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29759580644 conclusion=failure commit=407f2d1faab3
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29759541093 conclusion=failure commit=4a28ac1faaf9
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29759508477 conclusion=failure commit=3f7ade91368e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29759507671 conclusion=failure commit=3f7ade91368e
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29758800602 conclusion=failure commit=33be5c169a94
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29758363045 conclusion=failure commit=e63e16d4e6b5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29758765422 conclusion=failure commit=33be5c169a94
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
| Dashboard Shell Diagnostic | 29759507668 | failure | `3f7ade91368e` | 2026-07-20T16:28:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29759507668 |
| System3 Autopilot Proof Board | 29759542903 | failure | `4a28ac1faaf9` | 2026-07-20T16:26:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29759542903 |
| System3 Experimental Solution Planner | 29759580644 | failure | `407f2d1faab3` | 2026-07-20T16:26:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29759580644 |
| System3 Secure Install Credential Audit | 29759541093 | failure | `4a28ac1faaf9` | 2026-07-20T16:25:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29759541093 |
| Dashboard Visual Proof Strict Gate | 29759508477 | failure | `3f7ade91368e` | 2026-07-20T16:25:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29759508477 |
| Dashboard Visual Loading Postflight | 29759507671 | failure | `3f7ade91368e` | 2026-07-20T16:25:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29759507671 |
| System3 Windows Self-Hosted Full Proof | 29758800602 | failure | `33be5c169a94` | 2026-07-20T16:22:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29758800602 |
| Dashboard Visible Proof Current | 29758363045 | failure | `e63e16d4e6b5` | 2026-07-20T16:21:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29758363045 |
| Dashboard Visible Settle Proof | 29758765422 | failure | `33be5c169a94` | 2026-07-20T16:21:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29758765422 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29759516969 | in_progress | 2026-07-20T16:30:29Z |
| System3 Safe Repair Runner | 29759701726 | in_progress | 2026-07-20T16:28:29Z |
| Dashboard Visible Auth-Resilient Proof | 29758911992 | in_progress | 2026-07-20T16:16:55Z |

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
