# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-31T20:29:00.856200Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `18`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30660795728 conclusion=failure commit=1bce3d22db47
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30660709217 conclusion=failure commit=1bce3d22db47
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30660560229 conclusion=failure commit=e4985316b066
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=30660551043 conclusion=failure commit=e4985316b066
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30660533526 conclusion=failure commit=e4985316b066
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30660503647 conclusion=failure commit=e4985316b066
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
| Dashboard Visible Proof Warmed | 30660795728 | failure | `1bce3d22db47` | 2026-07-31T19:54:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30660795728 |
| System3 Backend Live Simulation Proof | 30660709217 | failure | `1bce3d22db47` | 2026-07-31T19:52:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30660709217 |
| System3 Render Worker Preflight | 30660560229 | failure | `e4985316b066` | 2026-07-31T19:49:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30660560229 |
| System3 Workflow Failure Tracker | 30660551043 | failure | `e4985316b066` | 2026-07-31T19:49:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30660551043 |
| Dashboard Deploy Provenance Gate | 30660533526 | failure | `e4985316b066` | 2026-07-31T19:49:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30660533526 |
| Dashboard Visual Production Proof | 30660503647 | failure | `e4985316b066` | 2026-07-31T19:49:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30660503647 |

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
