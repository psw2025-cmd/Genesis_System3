# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T18:35:33.239753Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30839226482 conclusion=failure commit=e74e8f9ee9dd
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30839129085 conclusion=failure commit=e74e8f9ee9dd
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30838849793 conclusion=failure commit=b3a6e18e353c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30838760415 conclusion=failure commit=b3a6e18e353c
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30810589818 conclusion=failure commit=509c96d50542
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30810426189 conclusion=failure commit=509c96d50542
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30811080508 conclusion=failure commit=509c96d50542
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30810401783 conclusion=failure commit=509c96d50542
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30810495753 conclusion=failure commit=509c96d50542
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30808393357 conclusion=failure commit=63a7adba2564
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
| Dashboard Visible Proof Warmed | 30839226482 | failure | `e74e8f9ee9dd` | 2026-08-03T18:00:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30839226482 |
| System3 Backend Live Simulation Proof | 30839129085 | failure | `e74e8f9ee9dd` | 2026-08-03T17:58:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30839129085 |
| Dashboard Deploy Provenance Gate | 30838849793 | failure | `b3a6e18e353c` | 2026-08-03T17:55:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30838849793 |
| Dashboard Visual Production Proof | 30838760415 | failure | `b3a6e18e353c` | 2026-08-03T17:54:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30838760415 |
| System3 Full Auto Truth | 30810589818 | failure | `509c96d50542` | 2026-08-03T12:07:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30810589818 |
| System3 Latest Truth Publish | 30810426189 | failure | `509c96d50542` | 2026-08-03T11:50:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30810426189 |
| System3 Broker Chain Semantic Gate | 30811080508 | failure | `509c96d50542` | 2026-08-03T11:50:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30811080508 |
| Permanent Repo Render Safety | 30810401783 | failure | `509c96d50542` | 2026-08-03T11:49:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30810401783 |
| Dashboard Live UI Proof | 30810495753 | failure | `509c96d50542` | 2026-08-03T11:41:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30810495753 |
| System3 Market Session Proof Runner | 30808393357 | failure | `63a7adba2564` | 2026-08-03T11:16:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30808393357 |

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
