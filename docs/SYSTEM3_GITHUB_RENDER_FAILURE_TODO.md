# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-30T14:46:26.211182Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30549717919 conclusion=failure commit=4d861b080951
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30549528293 conclusion=failure commit=4d861b080951
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30549199982 conclusion=failure commit=7fe79efa1778
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30549113365 conclusion=failure commit=7fe79efa1778
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30537933819 conclusion=failure commit=a17f2e82da73
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30537748617 conclusion=failure commit=a17f2e82da73
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30538301176 conclusion=failure commit=a17f2e82da73
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30537668568 conclusion=failure commit=a17f2e82da73
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30537860527 conclusion=failure commit=a17f2e82da73
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30536093803 conclusion=failure commit=e250ee6f4532
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
| Dashboard Visible Proof Warmed | 30549717919 | failure | `4d861b080951` | 2026-07-30T14:02:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30549717919 |
| System3 Backend Live Simulation Proof | 30549528293 | failure | `4d861b080951` | 2026-07-30T14:00:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30549528293 |
| Dashboard Deploy Provenance Gate | 30549199982 | failure | `7fe79efa1778` | 2026-07-30T13:56:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30549199982 |
| Dashboard Visual Production Proof | 30549113365 | failure | `7fe79efa1778` | 2026-07-30T13:55:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30549113365 |
| System3 Full Auto Truth | 30537933819 | failure | `a17f2e82da73` | 2026-07-30T11:41:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30537933819 |
| System3 Latest Truth Publish | 30537748617 | failure | `a17f2e82da73` | 2026-07-30T11:23:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30537748617 |
| System3 Broker Chain Semantic Gate | 30538301176 | failure | `a17f2e82da73` | 2026-07-30T11:23:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30538301176 |
| Permanent Repo Render Safety | 30537668568 | failure | `a17f2e82da73` | 2026-07-30T11:22:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30537668568 |
| Dashboard Live UI Proof | 30537860527 | failure | `a17f2e82da73` | 2026-07-30T11:16:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30537860527 |
| System3 Market Session Proof Runner | 30536093803 | failure | `e250ee6f4532` | 2026-07-30T10:51:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30536093803 |

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
