# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-01T11:28:17.720699Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30696527846 conclusion=failure commit=47b1528e26ce
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30696488865 conclusion=failure commit=47b1528e26ce
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30696411377 conclusion=failure commit=8521edac4e68
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30696387060 conclusion=failure commit=8521edac4e68
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30684260993 conclusion=failure commit=000676b0694e
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
| Dashboard Visible Proof Warmed | 30696527846 | failure | `47b1528e26ce` | 2026-08-01T10:52:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30696527846 |
| System3 Backend Live Simulation Proof | 30696488865 | failure | `47b1528e26ce` | 2026-08-01T10:50:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30696488865 |
| Dashboard Deploy Provenance Gate | 30696411377 | failure | `8521edac4e68` | 2026-08-01T10:48:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30696411377 |
| Dashboard Visual Production Proof | 30696387060 | failure | `8521edac4e68` | 2026-08-01T10:47:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30696387060 |
| System3 Windows Self-Hosted Workflow Migration | 30684260993 | failure | `000676b0694e` | 2026-08-01T04:37:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30684260993 |

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
