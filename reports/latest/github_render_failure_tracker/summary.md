# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-28T16:33:32.448030Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30375833685 conclusion=failure commit=4976ef3c3eb3
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30376343897 conclusion=failure commit=b4da1a764be2
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30376176797 conclusion=failure commit=b4da1a764be2
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30375942068 conclusion=failure commit=4976ef3c3eb3
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30375906149 conclusion=failure commit=4976ef3c3eb3
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30354258089 conclusion=failure commit=99efd9e3ad7f
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30354784400 conclusion=failure commit=99efd9e3ad7f
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30353998697 conclusion=failure commit=7368e1d6d03e
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
| Dashboard Visual Production Proof | 30375833685 | failure | `4976ef3c3eb3` | 2026-07-28T16:04:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30375833685 |
| Dashboard Visible Proof Warmed | 30376343897 | failure | `b4da1a764be2` | 2026-07-28T16:03:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30376343897 |
| System3 Backend Live Simulation Proof | 30376176797 | failure | `b4da1a764be2` | 2026-07-28T16:01:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30376176797 |
| System3 Render Worker Preflight | 30375942068 | failure | `4976ef3c3eb3` | 2026-07-28T15:58:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30375942068 |
| Dashboard Deploy Provenance Gate | 30375906149 | failure | `4976ef3c3eb3` | 2026-07-28T15:58:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30375906149 |
| System3 Full Auto Truth | 30354258089 | failure | `99efd9e3ad7f` | 2026-07-28T11:43:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30354258089 |
| System3 Broker Chain Semantic Gate | 30354784400 | failure | `99efd9e3ad7f` | 2026-07-28T11:26:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30354784400 |
| Permanent Repo Render Safety | 30353998697 | failure | `7368e1d6d03e` | 2026-07-28T11:24:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30353998697 |
| System3 Latest Truth Publish | 30352260724 | failure | `8e3f934ec3dd` | 2026-07-28T10:58:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30352260724 |
| System3 Market Session Proof Runner | 30352633381 | failure | `b91ca22358bc` | 2026-07-28T10:58:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30352633381 |
| Dashboard Live UI Proof | 30352644970 | failure | `b91ca22358bc` | 2026-07-28T10:55:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30352644970 |

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
