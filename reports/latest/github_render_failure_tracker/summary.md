# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-24T08:52:22.909361Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `14`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `26`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30080190000 conclusion=failure commit=ed37d94c957e
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30078531760 conclusion=failure commit=9118a8f203a3
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30079240272 conclusion=failure commit=d93dc5270c50
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30078705460 conclusion=failure commit=ace1899b9381
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30078689820 conclusion=failure commit=dbb14f0cbd81
- [ ] Fix latest GitHub workflow 'Dashboard Visual Settle Normalizer' run=30078705293 conclusion=failure commit=ace1899b9381
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30078705331 conclusion=failure commit=ace1899b9381
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30078705586 conclusion=failure commit=ace1899b9381
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30078705426 conclusion=failure commit=ace1899b9381
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30078705324 conclusion=failure commit=ace1899b9381
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30078651092 conclusion=failure commit=839a54458e22
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30077596021 conclusion=failure commit=8bf1132cb289
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30077501158 conclusion=failure commit=c8473cbf1836
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30077390614 conclusion=failure commit=3eba5d972865
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
| System3 Safe Repair Runner | 30080190000 | failure | `ed37d94c957e` | 2026-07-24T08:49:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30080190000 |
| System3 Full Auto Truth | 30078531760 | failure | `9118a8f203a3` | 2026-07-24T08:44:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30078531760 |
| System3 Broker Chain Semantic Gate | 30079240272 | failure | `d93dc5270c50` | 2026-07-24T08:32:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30079240272 |
| Dashboard Shell Diagnostic | 30078705460 | failure | `ace1899b9381` | 2026-07-24T08:24:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30078705460 |
| Dashboard Visible Issue Tracker | 30078689820 | failure | `dbb14f0cbd81` | 2026-07-24T08:23:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30078689820 |
| Dashboard Visual Settle Normalizer | 30078705293 | failure | `ace1899b9381` | 2026-07-24T08:22:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30078705293 |
| System3 Secure Install Credential Audit | 30078705331 | failure | `ace1899b9381` | 2026-07-24T08:22:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30078705331 |
| System3 Experimental Solution Planner | 30078705586 | failure | `ace1899b9381` | 2026-07-24T08:22:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30078705586 |
| Dashboard Visual Loading Postflight | 30078705426 | failure | `ace1899b9381` | 2026-07-24T08:22:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30078705426 |
| Dashboard Visual Proof Strict Gate | 30078705324 | failure | `ace1899b9381` | 2026-07-24T08:22:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30078705324 |
| System3 Autopilot Proof Board | 30078651092 | failure | `839a54458e22` | 2026-07-24T08:22:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30078651092 |
| Dashboard Visible Proof Warmed | 30077596021 | failure | `8bf1132cb289` | 2026-07-24T08:04:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30077596021 |
| System3 Backend Live Simulation Proof | 30077501158 | failure | `c8473cbf1836` | 2026-07-24T08:02:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30077501158 |
| Dashboard Visible Auth-Resilient Proof | 30077390614 | failure | `3eba5d972865` | 2026-07-24T08:01:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30077390614 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30080367473 | in_progress | 2026-07-24T08:50:41Z |
| Permanent Repo Render Safety | 30080219405 | in_progress | 2026-07-24T08:48:12Z |

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
