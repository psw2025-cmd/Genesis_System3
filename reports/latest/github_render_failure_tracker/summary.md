# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-29T23:21:38.245396Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `5`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `17`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30496890426 conclusion=failure commit=3772e80d96cd
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30496817880 conclusion=failure commit=3772e80d96cd
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30496687236 conclusion=failure commit=de71f260511f
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30496663760 conclusion=failure commit=3a55edfbba1f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30496615542 conclusion=failure commit=3a55edfbba1f
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
| Dashboard Visible Proof Warmed | 30496890426 | failure | `3772e80d96cd` | 2026-07-29T22:40:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30496890426 |
| System3 Backend Live Simulation Proof | 30496817880 | failure | `3772e80d96cd` | 2026-07-29T22:38:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30496817880 |
| System3 Render Worker Preflight | 30496687236 | failure | `de71f260511f` | 2026-07-29T22:35:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30496687236 |
| Dashboard Deploy Provenance Gate | 30496663760 | failure | `3a55edfbba1f` | 2026-07-29T22:35:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30496663760 |
| Dashboard Visual Production Proof | 30496615542 | failure | `3a55edfbba1f` | 2026-07-29T22:35:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30496615542 |

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
