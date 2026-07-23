# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T16:32:16.346787Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30025099041 conclusion=failure commit=fd2fe2281edf
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30025309342 conclusion=failure commit=f5d42a153085
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30025129649 conclusion=failure commit=4b29fa517f4c
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30025129609 conclusion=failure commit=4b29fa517f4c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30025098879 conclusion=failure commit=fd2fe2281edf
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30025098788 conclusion=failure commit=fd2fe2281edf
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30023848052 conclusion=failure commit=851b87a3e03d
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
| Dashboard Shell Diagnostic | 30025099041 | failure | `fd2fe2281edf` | 2026-07-23T16:30:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30025099041 |
| System3 Experimental Solution Planner | 30025309342 | failure | `f5d42a153085` | 2026-07-23T16:29:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30025309342 |
| System3 Autopilot Proof Board | 30025129649 | failure | `4b29fa517f4c` | 2026-07-23T16:27:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30025129649 |
| System3 Secure Install Credential Audit | 30025129609 | failure | `4b29fa517f4c` | 2026-07-23T16:27:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30025129609 |
| Dashboard Visual Loading Postflight | 30025098879 | failure | `fd2fe2281edf` | 2026-07-23T16:26:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30025098879 |
| Dashboard Visual Proof Strict Gate | 30025098788 | failure | `fd2fe2281edf` | 2026-07-23T16:26:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30025098788 |
| Dashboard Visible Proof Current | 30023848052 | failure | `851b87a3e03d` | 2026-07-23T16:21:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30023848052 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 30025308990 | in_progress | 2026-07-23T16:29:55Z |
| System3 Safe Repair Runner | 30025309151 | in_progress | 2026-07-23T16:29:39Z |

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
