# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-24T12:31:39.834957Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `13`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `25`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30093026843 conclusion=failure commit=be9d017cae10
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30091797492 conclusion=failure commit=16a2e69c6a84
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30091780892 conclusion=failure commit=996b9cfd8793
- [ ] Fix latest GitHub workflow 'Dashboard Visual Settle Normalizer' run=30091797491 conclusion=failure commit=16a2e69c6a84
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30091797480 conclusion=failure commit=16a2e69c6a84
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30091797544 conclusion=failure commit=16a2e69c6a84
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30091753205 conclusion=failure commit=c00604320150
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30091797528 conclusion=failure commit=16a2e69c6a84
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30091797488 conclusion=failure commit=16a2e69c6a84
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30091198381 conclusion=failure commit=054eebc08ddb
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30091143253 conclusion=failure commit=1885f5ed09ae
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30091093947 conclusion=failure commit=4180b8090950
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30091043882 conclusion=failure commit=8c831228920a
- [ ] Fix Render endpoint /: HTTP status 0 status=0
- [ ] Fix Render endpoint /ui/: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/health: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/paper: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Safe Repair Runner | 30093026843 | failure | `be9d017cae10` | 2026-07-24T12:27:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30093026843 |
| Dashboard Shell Diagnostic | 30091797492 | failure | `16a2e69c6a84` | 2026-07-24T12:06:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091797492 |
| Dashboard Visible Issue Tracker | 30091780892 | failure | `996b9cfd8793` | 2026-07-24T12:05:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091780892 |
| Dashboard Visual Settle Normalizer | 30091797491 | failure | `16a2e69c6a84` | 2026-07-24T12:05:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091797491 |
| System3 Secure Install Credential Audit | 30091797480 | failure | `16a2e69c6a84` | 2026-07-24T12:05:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091797480 |
| System3 Experimental Solution Planner | 30091797544 | failure | `16a2e69c6a84` | 2026-07-24T12:05:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091797544 |
| System3 Autopilot Proof Board | 30091753205 | failure | `c00604320150` | 2026-07-24T12:05:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091753205 |
| Dashboard Visual Loading Postflight | 30091797528 | failure | `16a2e69c6a84` | 2026-07-24T12:05:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091797528 |
| Dashboard Visual Proof Strict Gate | 30091797488 | failure | `16a2e69c6a84` | 2026-07-24T12:05:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091797488 |
| Dashboard Visible Proof Warmed | 30091198381 | failure | `054eebc08ddb` | 2026-07-24T11:55:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091198381 |
| System3 Backend Live Simulation Proof | 30091143253 | failure | `1885f5ed09ae` | 2026-07-24T11:54:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091143253 |
| Dashboard Visible Auth-Resilient Proof | 30091093947 | failure | `4180b8090950` | 2026-07-24T11:54:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091093947 |
| System3 Render Worker Preflight | 30091043882 | failure | `8c831228920a` | 2026-07-24T11:52:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30091043882 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 0 | HTTP status 0 | `none` |
| `/ui/` | 0 | HTTP status 0 | `none` |
| `/api/health` | 0 | HTTP status 0 | `none` |
| `/api/state` | 0 | HTTP status 0 | `none` |
| `/api/deploy/info` | 0 | HTTP status 0 | `none` |
| `/api/broker/diagnose` | 0 | HTTP status 0 | `none` |
| `/api/broker/funds` | 0 | HTTP status 0 | `none` |
| `/api/broker/holdings` | 0 | HTTP status 0 | `none` |
| `/api/broker/positions/live` | 0 | HTTP status 0 | `none` |
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
| `/api/paper` | 0 | HTTP status 0 | `none` |
| `/api/ml/performance` | 0 | HTTP status 0 | `none` |
