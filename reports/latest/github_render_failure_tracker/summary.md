# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-29T22:19:49.562168Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30493146544 conclusion=failure commit=cefd96ddb210
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30493064556 conclusion=failure commit=cefd96ddb210
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30492882244 conclusion=failure commit=38177fcc13cd
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30492899492 conclusion=failure commit=1b5c5e4b99e6
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30492825808 conclusion=failure commit=38177fcc13cd
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
| Dashboard Visible Proof Warmed | 30493146544 | failure | `cefd96ddb210` | 2026-07-29T21:39:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30493146544 |
| System3 Backend Live Simulation Proof | 30493064556 | failure | `cefd96ddb210` | 2026-07-29T21:37:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30493064556 |
| Dashboard Deploy Provenance Gate | 30492882244 | failure | `38177fcc13cd` | 2026-07-29T21:35:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30492882244 |
| System3 Render Worker Preflight | 30492899492 | failure | `1b5c5e4b99e6` | 2026-07-29T21:34:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30492899492 |
| Dashboard Visual Production Proof | 30492825808 | failure | `38177fcc13cd` | 2026-07-29T21:34:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30492825808 |

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
