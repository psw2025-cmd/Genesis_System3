# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-17T16:26:58.604009Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `11`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29595362048 conclusion=failure commit=1ad692dbd4a9
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29595531167 conclusion=failure commit=1174383c8387
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29595295848 conclusion=failure commit=1ad692dbd4a9
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29595552310 conclusion=failure commit=ea1d1b9e6165
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29595602585 conclusion=failure commit=7d4dc5a91a4d
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29595552347 conclusion=failure commit=ea1d1b9e6165
- [ ] Fix latest GitHub workflow 'Dashboard Visual Settle Normalizer' run=29595531135 conclusion=failure commit=1174383c8387
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29595531156 conclusion=failure commit=1174383c8387
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29595531238 conclusion=failure commit=1174383c8387
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29594709716 conclusion=failure commit=b008bc310533
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29593710860 conclusion=failure commit=2eb2e885f55d
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
| System3 Windows Self-Hosted Full Proof | 29595362048 | failure | `1ad692dbd4a9` | 2026-07-17T16:20:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29595362048 |
| Dashboard Shell Diagnostic | 29595531167 | failure | `1174383c8387` | 2026-07-17T16:19:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29595531167 |
| Dashboard Visible Settle Proof | 29595295848 | failure | `1ad692dbd4a9` | 2026-07-17T16:19:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29595295848 |
| System3 Autopilot Proof Board | 29595552310 | failure | `ea1d1b9e6165` | 2026-07-17T16:18:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29595552310 |
| System3 Experimental Solution Planner | 29595602585 | failure | `7d4dc5a91a4d` | 2026-07-17T16:18:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29595602585 |
| System3 Secure Install Credential Audit | 29595552347 | failure | `ea1d1b9e6165` | 2026-07-17T16:17:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29595552347 |
| Dashboard Visual Settle Normalizer | 29595531135 | failure | `1174383c8387` | 2026-07-17T16:17:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29595531135 |
| Dashboard Visual Loading Postflight | 29595531156 | failure | `1174383c8387` | 2026-07-17T16:16:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29595531156 |
| Dashboard Visual Proof Strict Gate | 29595531238 | failure | `1174383c8387` | 2026-07-17T16:16:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29595531238 |
| Dashboard Visible Proof Current | 29594709716 | failure | `b008bc310533` | 2026-07-17T16:16:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29594709716 |
| Dashboard Visible Proof Warmed | 29593710860 | failure | `2eb2e885f55d` | 2026-07-17T15:50:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29593710860 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29596005876 | in_progress | 2026-07-17T16:24:38Z |
| Dashboard Visible Issue Tracker | 29595540616 | pending | 2026-07-17T16:16:54Z |

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
