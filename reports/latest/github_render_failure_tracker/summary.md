# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T23:18:43.786720Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29664568273 conclusion=failure commit=7a5dd4c65fe2
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29664553860 conclusion=failure commit=788b3672bd25
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29664565148 conclusion=failure commit=788b3672bd25
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29664290145 conclusion=failure commit=242071eced9a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29664641787 conclusion=failure commit=cfaf1429b6c8
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29664576138 conclusion=failure commit=6b98b459c453
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29664596807 conclusion=failure commit=344f4e234cf4
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29664576146 conclusion=failure commit=6b98b459c453
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29664565088 conclusion=failure commit=788b3672bd25
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
| System3 Windows Self-Hosted Full Proof | 29664568273 | failure | `7a5dd4c65fe2` | 2026-07-18T23:11:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29664568273 |
| Dashboard Visible Settle Proof | 29664553860 | failure | `788b3672bd25` | 2026-07-18T23:09:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29664553860 |
| Dashboard Shell Diagnostic | 29664565148 | failure | `788b3672bd25` | 2026-07-18T23:07:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29664565148 |
| Dashboard Visible Proof Current | 29664290145 | failure | `242071eced9a` | 2026-07-18T23:06:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29664290145 |
| Dashboard Visual Proof Strict Gate | 29664641787 | failure | `cfaf1429b6c8` | 2026-07-18T23:06:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29664641787 |
| System3 Autopilot Proof Board | 29664576138 | failure | `6b98b459c453` | 2026-07-18T23:05:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29664576138 |
| System3 Experimental Solution Planner | 29664596807 | failure | `344f4e234cf4` | 2026-07-18T23:05:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29664596807 |
| System3 Secure Install Credential Audit | 29664576146 | failure | `6b98b459c453` | 2026-07-18T23:04:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29664576146 |
| Dashboard Visual Loading Postflight | 29664565088 | failure | `788b3672bd25` | 2026-07-18T23:04:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29664565088 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29664906585 | in_progress | 2026-07-18T23:15:30Z |
| Dashboard Visible Issue Tracker | 29664565710 | in_progress | 2026-07-18T23:12:44Z |
| Dashboard Visible Auth-Resilient Proof | 29664650228 | in_progress | 2026-07-18T23:06:51Z |

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
