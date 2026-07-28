# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-28T09:55:30.467168Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30346571764 conclusion=failure commit=1aff2bc4f33a
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30347061917 conclusion=failure commit=1aff2bc4f33a
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30346314287 conclusion=failure commit=8a7d80ac57d9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30345927039 conclusion=failure commit=8a7d80ac57d9
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30345829820 conclusion=failure commit=8a7d80ac57d9
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30345617351 conclusion=failure commit=d93e1c32d1f1
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30345573759 conclusion=failure commit=d93e1c32d1f1
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30344652684 conclusion=failure commit=d93e1c32d1f1
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30340234238 conclusion=failure commit=584d0d1f6f52
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30329029225 conclusion=failure commit=8cb5155b40be
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
| System3 Full Auto Truth | 30346571764 | failure | `1aff2bc4f33a` | 2026-07-28T09:50:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30346571764 |
| System3 Broker Chain Semantic Gate | 30347061917 | failure | `1aff2bc4f33a` | 2026-07-28T09:33:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30347061917 |
| Permanent Repo Render Safety | 30346314287 | failure | `8a7d80ac57d9` | 2026-07-28T09:32:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30346314287 |
| Dashboard Visible Proof Warmed | 30345927039 | failure | `8a7d80ac57d9` | 2026-07-28T09:17:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30345927039 |
| System3 Backend Live Simulation Proof | 30345829820 | failure | `8a7d80ac57d9` | 2026-07-28T09:16:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30345829820 |
| Dashboard Deploy Provenance Gate | 30345617351 | failure | `d93e1c32d1f1` | 2026-07-28T09:13:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30345617351 |
| Dashboard Visual Production Proof | 30345573759 | failure | `d93e1c32d1f1` | 2026-07-28T09:13:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30345573759 |
| Dashboard Live UI Proof | 30344652684 | failure | `d93e1c32d1f1` | 2026-07-28T08:59:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30344652684 |
| System3 Market Session Proof Runner | 30340234238 | failure | `584d0d1f6f52` | 2026-07-28T07:58:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30340234238 |
| System3 Windows Self-Hosted Workflow Migration | 30329029225 | failure | `8cb5155b40be` | 2026-07-28T04:33:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30329029225 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30348396129 | in_progress | 2026-07-28T09:52:11Z |

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
