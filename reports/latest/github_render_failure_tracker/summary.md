# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-29T05:04:46.805235Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `11`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30423486776 conclusion=failure commit=ad3909bc1ce3
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30422641994 conclusion=failure commit=21176045c695
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30421367925 conclusion=failure commit=85a3b7d3f77f
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30421813510 conclusion=failure commit=a99b1938a8cc
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30421067469 conclusion=failure commit=85a3b7d3f77f
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30421239001 conclusion=failure commit=85a3b7d3f77f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30419691745 conclusion=failure commit=85a3b7d3f77f
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30419628020 conclusion=failure commit=85a3b7d3f77f
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30419469750 conclusion=failure commit=3b1cd8923c6b
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30419489645 conclusion=failure commit=ef4b83d216ed
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30419409611 conclusion=failure commit=3b1cd8923c6b
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
| System3 Market Session Proof Runner | 30423486776 | failure | `ad3909bc1ce3` | 2026-07-29T04:56:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30423486776 |
| System3 Windows Self-Hosted Workflow Migration | 30422641994 | failure | `21176045c695` | 2026-07-29T04:35:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30422641994 |
| System3 Full Auto Truth | 30421367925 | failure | `85a3b7d3f77f` | 2026-07-29T04:31:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30421367925 |
| System3 Broker Chain Semantic Gate | 30421813510 | failure | `a99b1938a8cc` | 2026-07-29T04:16:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30421813510 |
| Permanent Repo Render Safety | 30421067469 | failure | `85a3b7d3f77f` | 2026-07-29T04:09:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30421067469 |
| Dashboard Live UI Proof | 30421239001 | failure | `85a3b7d3f77f` | 2026-07-29T04:04:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30421239001 |
| Dashboard Visible Proof Warmed | 30419691745 | failure | `85a3b7d3f77f` | 2026-07-29T03:29:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30419691745 |
| System3 Backend Live Simulation Proof | 30419628020 | failure | `85a3b7d3f77f` | 2026-07-29T03:28:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30419628020 |
| Dashboard Deploy Provenance Gate | 30419469750 | failure | `3b1cd8923c6b` | 2026-07-29T03:24:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30419469750 |
| System3 Render Worker Preflight | 30419489645 | failure | `ef4b83d216ed` | 2026-07-29T03:24:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30419489645 |
| Dashboard Visual Production Proof | 30419409611 | failure | `3b1cd8923c6b` | 2026-07-29T03:23:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30419409611 |

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
