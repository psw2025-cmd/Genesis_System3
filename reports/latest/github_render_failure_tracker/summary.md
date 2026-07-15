# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-15T01:34:48.357119Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `18`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29381732915 conclusion=failure commit=a5d8afc097ac
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29381732952 conclusion=failure commit=a5d8afc097ac
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29381732920 conclusion=failure commit=a5d8afc097ac
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29381732958 conclusion=failure commit=a5d8afc097ac
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29381732942 conclusion=failure commit=a5d8afc097ac
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29381695879 conclusion=failure commit=f3b28896c858
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
| Dashboard Shell Diagnostic | 29381732915 | failure | `a5d8afc097ac` | 2026-07-15T01:31:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29381732915 |
| System3 Secure Install Credential Audit | 29381732952 | failure | `a5d8afc097ac` | 2026-07-15T01:29:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29381732952 |
| Dashboard Visual Loading Postflight | 29381732920 | failure | `a5d8afc097ac` | 2026-07-15T01:29:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29381732920 |
| Dashboard Visual Proof Strict Gate | 29381732958 | failure | `a5d8afc097ac` | 2026-07-15T01:29:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29381732958 |
| System3 Experimental Solution Planner | 29381732942 | failure | `a5d8afc097ac` | 2026-07-15T01:29:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29381732942 |
| System3 Autopilot Proof Board | 29381695879 | failure | `f3b28896c858` | 2026-07-15T01:29:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29381695879 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29381731826 | in_progress | 2026-07-15T01:34:41Z |
| System3 Safe Repair Runner | 29381796533 | in_progress | 2026-07-15T01:30:55Z |

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
