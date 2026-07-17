# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-17T13:32:42.960598Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `11`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29583162784 conclusion=failure commit=d438df76db43
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29583051395 conclusion=failure commit=084dd776e1e4
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29583049782 conclusion=failure commit=084dd776e1e4
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29583323609 conclusion=failure commit=735387f43952
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29582924189 conclusion=failure commit=b98f6c284b8e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29582541622 conclusion=failure commit=df2d3163e2e9
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29583043786 conclusion=failure commit=3faef2fcc449
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29583070675 conclusion=failure commit=0ea255a557fc
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29583111566 conclusion=failure commit=ca42fa67e7ab
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29583070797 conclusion=failure commit=0ea255a557fc
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29583043733 conclusion=failure commit=3faef2fcc449
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
| Dashboard Visible Auth-Resilient Proof | 29583162784 | failure | `d438df76db43` | 2026-07-17T13:32:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29583162784 |
| Dashboard Visible Issue Tracker | 29583051395 | failure | `084dd776e1e4` | 2026-07-17T13:28:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29583051395 |
| System3 Windows Self-Hosted Full Proof | 29583049782 | failure | `084dd776e1e4` | 2026-07-17T13:17:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29583049782 |
| Dashboard Visual Proof Strict Gate | 29583323609 | failure | `735387f43952` | 2026-07-17T13:16:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29583323609 |
| Dashboard Visible Settle Proof | 29582924189 | failure | `b98f6c284b8e` | 2026-07-17T13:16:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29582924189 |
| Dashboard Visible Proof Current | 29582541622 | failure | `df2d3163e2e9` | 2026-07-17T13:16:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29582541622 |
| Dashboard Shell Diagnostic | 29583043786 | failure | `3faef2fcc449` | 2026-07-17T13:15:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29583043786 |
| System3 Autopilot Proof Board | 29583070675 | failure | `0ea255a557fc` | 2026-07-17T13:13:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29583070675 |
| System3 Experimental Solution Planner | 29583111566 | failure | `ca42fa67e7ab` | 2026-07-17T13:13:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29583111566 |
| System3 Secure Install Credential Audit | 29583070797 | failure | `0ea255a557fc` | 2026-07-17T13:12:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29583070797 |
| Dashboard Visual Loading Postflight | 29583043733 | failure | `3faef2fcc449` | 2026-07-17T13:12:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29583043733 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29584123263 | in_progress | 2026-07-17T13:29:07Z |

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
