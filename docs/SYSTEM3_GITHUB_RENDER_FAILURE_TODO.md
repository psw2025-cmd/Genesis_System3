# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-24T10:41:20.899591Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `13`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `25`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30086838265 conclusion=failure commit=b25fa21fa94a
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30086219625 conclusion=failure commit=74793a66fc76
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30085857997 conclusion=failure commit=ea9bc068f8a8
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30085852181 conclusion=failure commit=7c67bc5379ec
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30085857934 conclusion=failure commit=ea9bc068f8a8
- [ ] Fix latest GitHub workflow 'Dashboard Visual Settle Normalizer' run=30085857978 conclusion=failure commit=ea9bc068f8a8
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30085857893 conclusion=failure commit=ea9bc068f8a8
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30085857894 conclusion=failure commit=ea9bc068f8a8
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30085857973 conclusion=failure commit=ea9bc068f8a8
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30085803708 conclusion=failure commit=538280bd6b22
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30084852245 conclusion=failure commit=f5746996fe12
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30084711917 conclusion=failure commit=4c5221d1a456
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30084740147 conclusion=failure commit=c8b641fff4a6
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
| System3 Safe Repair Runner | 30086838265 | failure | `b25fa21fa94a` | 2026-07-24T10:40:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30086838265 |
| System3 Broker Chain Semantic Gate | 30086219625 | failure | `74793a66fc76` | 2026-07-24T10:27:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30086219625 |
| Dashboard Shell Diagnostic | 30085857997 | failure | `ea9bc068f8a8` | 2026-07-24T10:22:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30085857997 |
| Dashboard Visible Issue Tracker | 30085852181 | failure | `7c67bc5379ec` | 2026-07-24T10:21:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30085852181 |
| System3 Secure Install Credential Audit | 30085857934 | failure | `ea9bc068f8a8` | 2026-07-24T10:21:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30085857934 |
| Dashboard Visual Settle Normalizer | 30085857978 | failure | `ea9bc068f8a8` | 2026-07-24T10:21:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30085857978 |
| System3 Experimental Solution Planner | 30085857893 | failure | `ea9bc068f8a8` | 2026-07-24T10:21:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30085857893 |
| Dashboard Visual Proof Strict Gate | 30085857894 | failure | `ea9bc068f8a8` | 2026-07-24T10:21:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30085857894 |
| Dashboard Visual Loading Postflight | 30085857973 | failure | `ea9bc068f8a8` | 2026-07-24T10:21:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30085857973 |
| System3 Autopilot Proof Board | 30085803708 | failure | `538280bd6b22` | 2026-07-24T10:21:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30085803708 |
| Dashboard Visible Proof Warmed | 30084852245 | failure | `f5746996fe12` | 2026-07-24T10:04:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30084852245 |
| Dashboard Visible Auth-Resilient Proof | 30084711917 | failure | `4c5221d1a456` | 2026-07-24T10:02:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30084711917 |
| System3 Backend Live Simulation Proof | 30084740147 | failure | `c8b641fff4a6` | 2026-07-24T10:02:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30084740147 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30086946255 | in_progress | 2026-07-24T10:39:57Z |
| Permanent Repo Render Safety | 30086848453 | in_progress | 2026-07-24T10:38:10Z |
| System3 Full Auto Truth | 30085710325 | in_progress | 2026-07-24T10:18:36Z |

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
