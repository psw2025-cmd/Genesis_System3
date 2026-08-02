# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-02T06:53:41.170698Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30734264801 conclusion=failure commit=606b2c96d163
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30734200352 conclusion=failure commit=606b2c96d163
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30734099528 conclusion=failure commit=affc173c481a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30734069404 conclusion=failure commit=1699560a4bce
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30732685725 conclusion=failure commit=07b199fc2eaf
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
| Dashboard Visible Proof Warmed | 30734264801 | failure | `606b2c96d163` | 2026-08-02T05:33:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30734264801 |
| System3 Backend Live Simulation Proof | 30734200352 | failure | `606b2c96d163` | 2026-08-02T05:29:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30734200352 |
| Dashboard Deploy Provenance Gate | 30734099528 | failure | `affc173c481a` | 2026-08-02T05:26:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30734099528 |
| Dashboard Visual Production Proof | 30734069404 | failure | `1699560a4bce` | 2026-08-02T05:25:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30734069404 |
| System3 Windows Self-Hosted Workflow Migration | 30732685725 | failure | `07b199fc2eaf` | 2026-08-02T04:38:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30732685725 |

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
