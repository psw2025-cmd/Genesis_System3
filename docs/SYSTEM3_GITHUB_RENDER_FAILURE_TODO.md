# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T08:47:42.518603Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29679866930 conclusion=failure commit=4d00c12773f2
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29679917037 conclusion=failure commit=698e1783075b
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29679917059 conclusion=failure commit=698e1783075b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29679917076 conclusion=failure commit=698e1783075b
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29679917069 conclusion=failure commit=698e1783075b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29679917049 conclusion=failure commit=698e1783075b
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29679867994 conclusion=failure commit=4d00c12773f2
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29679148564 conclusion=failure commit=1cff97c861aa
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29679094358 conclusion=failure commit=1cff97c861aa
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
| Dashboard Visible Issue Tracker | 29679866930 | failure | `4d00c12773f2` | 2026-07-19T08:41:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29679866930 |
| Dashboard Shell Diagnostic | 29679917037 | failure | `698e1783075b` | 2026-07-19T08:33:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29679917037 |
| System3 Secure Install Credential Audit | 29679917059 | failure | `698e1783075b` | 2026-07-19T08:30:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29679917059 |
| Dashboard Visual Loading Postflight | 29679917076 | failure | `698e1783075b` | 2026-07-19T08:29:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29679917076 |
| System3 Experimental Solution Planner | 29679917069 | failure | `698e1783075b` | 2026-07-19T08:29:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29679917069 |
| Dashboard Visual Proof Strict Gate | 29679917049 | failure | `698e1783075b` | 2026-07-19T08:29:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29679917049 |
| System3 Autopilot Proof Board | 29679867994 | failure | `4d00c12773f2` | 2026-07-19T08:29:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29679867994 |
| Dashboard Visible Proof Warmed | 29679148564 | failure | `1cff97c861aa` | 2026-07-19T08:04:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29679148564 |
| System3 Backend Live Simulation Proof | 29679094358 | failure | `1cff97c861aa` | 2026-07-19T08:01:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29679094358 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29680302989 | in_progress | 2026-07-19T08:43:26Z |

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
