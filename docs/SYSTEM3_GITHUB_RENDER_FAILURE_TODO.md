# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T07:49:17.482770Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `5`
Render failed endpoints: `12`
TODO count: `18`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29989148117 conclusion=failure commit=ec5e991599a0
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29989148167 conclusion=failure commit=ec5e991599a0
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29988926922 conclusion=failure commit=27a2f37e1104
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29988926912 conclusion=failure commit=27a2f37e1104
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29988926973 conclusion=failure commit=27a2f37e1104
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29988279172 conclusion=failure commit=dc3d2a40d984
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
| System3 Secure Install Credential Audit | 29989148117 | failure | `ec5e991599a0` | 2026-07-23T07:46:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29989148117 |
| System3 Autopilot Proof Board | 29989148167 | failure | `ec5e991599a0` | 2026-07-23T07:46:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29989148167 |
| Dashboard Shell Diagnostic | 29988926922 | failure | `27a2f37e1104` | 2026-07-23T07:45:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29988926922 |
| Dashboard Visual Loading Postflight | 29988926912 | failure | `27a2f37e1104` | 2026-07-23T07:41:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29988926912 |
| Dashboard Visual Proof Strict Gate | 29988926973 | failure | `27a2f37e1104` | 2026-07-23T07:40:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29988926973 |
| Dashboard Visible Proof Current | 29988279172 | failure | `dc3d2a40d984` | 2026-07-23T07:39:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29988279172 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 29989289878 | in_progress | 2026-07-23T07:48:07Z |
| Dashboard Visible Issue Tracker | 29989167253 | in_progress | 2026-07-23T07:47:49Z |
| Permanent Repo Render Safety | 29989218668 | in_progress | 2026-07-23T07:47:04Z |
| System3 Safe Repair Runner | 29989167246 | in_progress | 2026-07-23T07:46:04Z |
| System3 Experimental Solution Planner | 29989167288 | in_progress | 2026-07-23T07:45:31Z |

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
