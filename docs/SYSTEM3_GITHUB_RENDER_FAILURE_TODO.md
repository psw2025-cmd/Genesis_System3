# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T09:48:59.227389Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29996610119 conclusion=failure commit=c83afc876336
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29996648026 conclusion=failure commit=677a9adbe8a1
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29996564366 conclusion=failure commit=9dd5a0f31ead
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29996610008 conclusion=failure commit=c83afc876336
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29996610219 conclusion=failure commit=c83afc876336
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29996609998 conclusion=failure commit=c83afc876336
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29995238818 conclusion=failure commit=9ce62f7c7ff0
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
| Dashboard Shell Diagnostic | 29996610119 | failure | `c83afc876336` | 2026-07-23T09:48:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29996610119 |
| System3 Experimental Solution Planner | 29996648026 | failure | `677a9adbe8a1` | 2026-07-23T09:46:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29996648026 |
| System3 Autopilot Proof Board | 29996564366 | failure | `9dd5a0f31ead` | 2026-07-23T09:45:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29996564366 |
| System3 Secure Install Credential Audit | 29996610008 | failure | `c83afc876336` | 2026-07-23T09:45:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29996610008 |
| Dashboard Visual Loading Postflight | 29996610219 | failure | `c83afc876336` | 2026-07-23T09:45:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29996610219 |
| Dashboard Visual Proof Strict Gate | 29996609998 | failure | `c83afc876336` | 2026-07-23T09:45:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29996609998 |
| Dashboard Visible Proof Current | 29995238818 | failure | `9ce62f7c7ff0` | 2026-07-23T09:31:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29995238818 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 29996769621 | in_progress | 2026-07-23T09:47:48Z |
| System3 Safe Repair Runner | 29996647947 | in_progress | 2026-07-23T09:46:15Z |
| Dashboard Visible Issue Tracker | 29996647738 | pending | 2026-07-23T09:45:58Z |
| Permanent Repo Render Safety | 29996622088 | in_progress | 2026-07-23T09:45:37Z |

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
