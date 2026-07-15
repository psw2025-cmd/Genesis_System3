# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-15T07:37:14.374924Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29397601834 conclusion=failure commit=405f71ca8e73
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29397314886 conclusion=failure commit=7b68749a2532
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29397601735 conclusion=failure commit=405f71ca8e73
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29397562607 conclusion=failure commit=07af073efd4d
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29397601855 conclusion=failure commit=405f71ca8e73
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29397601759 conclusion=failure commit=405f71ca8e73
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29397601813 conclusion=failure commit=405f71ca8e73
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
| Dashboard Shell Diagnostic | 29397601834 | failure | `405f71ca8e73` | 2026-07-15T07:34:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29397601834 |
| System3 Windows Self-Hosted Full Proof | 29397314886 | failure | `7b68749a2532` | 2026-07-15T07:31:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29397314886 |
| System3 Secure Install Credential Audit | 29397601735 | failure | `405f71ca8e73` | 2026-07-15T07:31:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29397601735 |
| System3 Autopilot Proof Board | 29397562607 | failure | `07af073efd4d` | 2026-07-15T07:31:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29397562607 |
| System3 Experimental Solution Planner | 29397601855 | failure | `405f71ca8e73` | 2026-07-15T07:31:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29397601855 |
| Dashboard Visual Loading Postflight | 29397601759 | failure | `405f71ca8e73` | 2026-07-15T07:31:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29397601759 |
| Dashboard Visual Proof Strict Gate | 29397601813 | failure | `405f71ca8e73` | 2026-07-15T07:31:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29397601813 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29397599629 | in_progress | 2026-07-15T07:35:53Z |
| System3 Safe Repair Runner | 29397760644 | in_progress | 2026-07-15T07:34:23Z |

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
