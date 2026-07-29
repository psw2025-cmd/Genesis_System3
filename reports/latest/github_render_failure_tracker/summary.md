# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-29T17:27:49.901590Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30472357220 conclusion=failure commit=804707525af6
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30472261411 conclusion=failure commit=804707525af6
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30472057311 conclusion=failure commit=9d308a006c58
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30472018057 conclusion=failure commit=9d308a006c58
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30471949337 conclusion=failure commit=9d308a006c58
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30447187262 conclusion=failure commit=413447021918
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30447853460 conclusion=failure commit=413447021918
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30447032852 conclusion=failure commit=bf60c2b8c371
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30445439303 conclusion=failure commit=06fca0cd46d4
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30445681864 conclusion=failure commit=06fca0cd46d4
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30445216616 conclusion=failure commit=06fca0cd46d4
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
| Dashboard Visible Proof Warmed | 30472357220 | failure | `804707525af6` | 2026-07-29T16:48:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30472357220 |
| System3 Backend Live Simulation Proof | 30472261411 | failure | `804707525af6` | 2026-07-29T16:46:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30472261411 |
| System3 Render Worker Preflight | 30472057311 | failure | `9d308a006c58` | 2026-07-29T16:43:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30472057311 |
| Dashboard Deploy Provenance Gate | 30472018057 | failure | `9d308a006c58` | 2026-07-29T16:43:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30472018057 |
| Dashboard Visual Production Proof | 30471949337 | failure | `9d308a006c58` | 2026-07-29T16:43:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30471949337 |
| System3 Full Auto Truth | 30447187262 | failure | `413447021918` | 2026-07-29T11:45:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30447187262 |
| System3 Broker Chain Semantic Gate | 30447853460 | failure | `413447021918` | 2026-07-29T11:31:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30447853460 |
| Dashboard Live UI Proof | 30447032852 | failure | `bf60c2b8c371` | 2026-07-29T11:18:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30447032852 |
| System3 Latest Truth Publish | 30445439303 | failure | `06fca0cd46d4` | 2026-07-29T11:03:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30445439303 |
| System3 Market Session Proof Runner | 30445681864 | failure | `06fca0cd46d4` | 2026-07-29T11:01:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30445681864 |
| Permanent Repo Render Safety | 30445216616 | failure | `06fca0cd46d4` | 2026-07-29T10:59:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30445216616 |

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
