# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T12:18:51.075794Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29643705425 conclusion=failure commit=91e364696d66
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29643375485 conclusion=failure commit=aa6deb736454
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29643598842 conclusion=failure commit=ebd8b182c985
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29643698167 conclusion=failure commit=c4ea3a54b4e4
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29643592279 conclusion=failure commit=ebd8b182c985
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29643711880 conclusion=failure commit=4f7949470be5
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29643726420 conclusion=failure commit=ee49c381b4ab
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29643710289 conclusion=failure commit=4f7949470be5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29643698109 conclusion=failure commit=c4ea3a54b4e4
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29643698157 conclusion=failure commit=c4ea3a54b4e4
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
| Dashboard Visible Issue Tracker | 29643705425 | failure | `91e364696d66` | 2026-07-18T12:18:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29643705425 |
| Dashboard Visible Proof Current | 29643375485 | failure | `aa6deb736454` | 2026-07-18T12:14:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29643375485 |
| System3 Windows Self-Hosted Full Proof | 29643598842 | failure | `ebd8b182c985` | 2026-07-18T12:09:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29643598842 |
| Dashboard Shell Diagnostic | 29643698167 | failure | `c4ea3a54b4e4` | 2026-07-18T12:08:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29643698167 |
| Dashboard Visible Settle Proof | 29643592279 | failure | `ebd8b182c985` | 2026-07-18T12:08:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29643592279 |
| System3 Autopilot Proof Board | 29643711880 | failure | `4f7949470be5` | 2026-07-18T12:06:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29643711880 |
| System3 Experimental Solution Planner | 29643726420 | failure | `ee49c381b4ab` | 2026-07-18T12:06:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29643726420 |
| System3 Secure Install Credential Audit | 29643710289 | failure | `4f7949470be5` | 2026-07-18T12:06:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29643710289 |
| Dashboard Visual Loading Postflight | 29643698109 | failure | `c4ea3a54b4e4` | 2026-07-18T12:05:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29643698109 |
| Dashboard Visual Proof Strict Gate | 29643698157 | failure | `c4ea3a54b4e4` | 2026-07-18T12:05:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29643698157 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29643931971 | in_progress | 2026-07-18T12:14:00Z |
| Dashboard Visible Auth-Resilient Proof | 29643688841 | in_progress | 2026-07-18T12:05:10Z |

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
