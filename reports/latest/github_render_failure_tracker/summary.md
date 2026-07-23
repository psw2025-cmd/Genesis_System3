# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-23T10:45:05.053978Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `6`
Render failed endpoints: `12`
TODO count: `18`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30000385823 conclusion=failure commit=1eb4b2042eac
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30000427419 conclusion=failure commit=ec7faa383db4
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30000427466 conclusion=failure commit=ec7faa383db4
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30000427421 conclusion=failure commit=ec7faa383db4
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30000427450 conclusion=failure commit=ec7faa383db4
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29999219910 conclusion=failure commit=32e4b7910926
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
| System3 Autopilot Proof Board | 30000385823 | failure | `1eb4b2042eac` | 2026-07-23T10:44:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30000385823 |
| System3 Secure Install Credential Audit | 30000427419 | failure | `ec7faa383db4` | 2026-07-23T10:44:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30000427419 |
| System3 Experimental Solution Planner | 30000427466 | failure | `ec7faa383db4` | 2026-07-23T10:44:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30000427466 |
| Dashboard Visual Proof Strict Gate | 30000427421 | failure | `ec7faa383db4` | 2026-07-23T10:44:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30000427421 |
| Dashboard Visual Loading Postflight | 30000427450 | failure | `ec7faa383db4` | 2026-07-23T10:44:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30000427450 |
| Dashboard Visible Proof Current | 29999219910 | failure | `32e4b7910926` | 2026-07-23T10:37:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29999219910 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Shell Diagnostic | 30000427454 | in_progress | 2026-07-23T10:44:39Z |
| System3 Safe Repair Runner | 30000427479 | in_progress | 2026-07-23T10:44:25Z |
| Dashboard Visible Issue Tracker | 30000426114 | pending | 2026-07-23T10:44:21Z |
| System3 Latest Truth Publish | 30000399899 | in_progress | 2026-07-23T10:43:58Z |
| Permanent Repo Render Safety | 30000274037 | in_progress | 2026-07-23T10:41:58Z |
| System3 Full Auto Truth | 29998860386 | in_progress | 2026-07-23T10:19:27Z |

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
