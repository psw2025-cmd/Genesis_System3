# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-28T11:40:54.162700Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30354784400 conclusion=failure commit=99efd9e3ad7f
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30353998697 conclusion=failure commit=7368e1d6d03e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30353126014 conclusion=failure commit=e87367b875a8
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30353374410 conclusion=failure commit=594d2a78777b
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30353388559 conclusion=failure commit=594d2a78777b
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30353149968 conclusion=failure commit=e87367b875a8
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30352260724 conclusion=failure commit=8e3f934ec3dd
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30352633381 conclusion=failure commit=b91ca22358bc
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30352644970 conclusion=failure commit=b91ca22358bc
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
| System3 Broker Chain Semantic Gate | 30354784400 | failure | `99efd9e3ad7f` | 2026-07-28T11:26:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30354784400 |
| Permanent Repo Render Safety | 30353998697 | failure | `7368e1d6d03e` | 2026-07-28T11:24:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30353998697 |
| Dashboard Visual Production Proof | 30353126014 | failure | `e87367b875a8` | 2026-07-28T11:12:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30353126014 |
| Dashboard Visible Proof Warmed | 30353374410 | failure | `594d2a78777b` | 2026-07-28T11:06:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30353374410 |
| System3 Backend Live Simulation Proof | 30353388559 | failure | `594d2a78777b` | 2026-07-28T11:06:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30353388559 |
| Dashboard Deploy Provenance Gate | 30353149968 | failure | `e87367b875a8` | 2026-07-28T11:02:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30353149968 |
| System3 Latest Truth Publish | 30352260724 | failure | `8e3f934ec3dd` | 2026-07-28T10:58:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30352260724 |
| System3 Market Session Proof Runner | 30352633381 | failure | `b91ca22358bc` | 2026-07-28T10:58:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30352633381 |
| Dashboard Live UI Proof | 30352644970 | failure | `b91ca22358bc` | 2026-07-28T10:55:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30352644970 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Full Auto Truth | 30354258089 | in_progress | 2026-07-28T11:18:31Z |

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
