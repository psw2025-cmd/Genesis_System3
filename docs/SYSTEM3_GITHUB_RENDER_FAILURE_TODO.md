# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-01T21:17:59.420839Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30717325442 conclusion=failure commit=5b598b6db69a
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30717284198 conclusion=failure commit=5b598b6db69a
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30717213489 conclusion=failure commit=ae1fc03b356f
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30717223398 conclusion=failure commit=ae1fc03b356f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30717185754 conclusion=failure commit=ae1fc03b356f
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
| Dashboard Visible Proof Warmed | 30717325442 | failure | `5b598b6db69a` | 2026-08-01T20:36:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30717325442 |
| System3 Backend Live Simulation Proof | 30717284198 | failure | `5b598b6db69a` | 2026-08-01T20:35:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30717284198 |
| Dashboard Deploy Provenance Gate | 30717213489 | failure | `ae1fc03b356f` | 2026-08-01T20:33:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30717213489 |
| System3 Render Worker Preflight | 30717223398 | failure | `ae1fc03b356f` | 2026-08-01T20:33:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30717223398 |
| Dashboard Visual Production Proof | 30717185754 | failure | `ae1fc03b356f` | 2026-08-01T20:32:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30717185754 |

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
