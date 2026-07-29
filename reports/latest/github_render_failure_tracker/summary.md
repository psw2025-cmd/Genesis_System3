# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-29T08:59:49.282030Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30435122392 conclusion=failure commit=d5ca2e7f9939
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30436103359 conclusion=failure commit=af91c87b4810
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30434486665 conclusion=failure commit=d5ca2e7f9939
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30434501226 conclusion=failure commit=d5ca2e7f9939
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30434263248 conclusion=failure commit=7616be47960f
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30434266926 conclusion=failure commit=7616be47960f
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30433617761 conclusion=failure commit=506c561f061c
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30433707601 conclusion=failure commit=506c561f061c
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30422641994 conclusion=failure commit=21176045c695
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
| System3 Full Auto Truth | 30435122392 | failure | `d5ca2e7f9939` | 2026-07-29T08:45:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30435122392 |
| System3 Broker Chain Semantic Gate | 30436103359 | failure | `af91c87b4810` | 2026-07-29T08:35:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30436103359 |
| Dashboard Visible Proof Warmed | 30434486665 | failure | `d5ca2e7f9939` | 2026-07-29T08:11:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30434486665 |
| System3 Backend Live Simulation Proof | 30434501226 | failure | `d5ca2e7f9939` | 2026-07-29T08:11:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30434501226 |
| Dashboard Visual Production Proof | 30434263248 | failure | `7616be47960f` | 2026-07-29T08:08:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30434263248 |
| Dashboard Deploy Provenance Gate | 30434266926 | failure | `7616be47960f` | 2026-07-29T08:08:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30434266926 |
| System3 Market Session Proof Runner | 30433617761 | failure | `506c561f061c` | 2026-07-29T08:01:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30433617761 |
| Dashboard Live UI Proof | 30433707601 | failure | `506c561f061c` | 2026-07-29T07:59:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30433707601 |
| System3 Windows Self-Hosted Workflow Migration | 30422641994 | failure | `21176045c695` | 2026-07-29T04:35:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30422641994 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30437573496 | in_progress | 2026-07-29T08:56:57Z |
| Permanent Repo Render Safety | 30437375665 | in_progress | 2026-07-29T08:54:16Z |

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
