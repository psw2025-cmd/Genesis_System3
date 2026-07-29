# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-29T10:57:42.933971Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30443608516 conclusion=failure commit=6e93b3e0bee9
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30444125977 conclusion=failure commit=6e93b3e0bee9
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30443329865 conclusion=failure commit=1e88f0a5ba44
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30443019576 conclusion=failure commit=1e88f0a5ba44
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30442807421 conclusion=failure commit=08ca51daf3eb
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30442770737 conclusion=failure commit=45beeb48f4d2
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30439040418 conclusion=failure commit=a97766fd4b3c
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
| System3 Full Auto Truth | 30443608516 | failure | `6e93b3e0bee9` | 2026-07-29T10:50:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30443608516 |
| System3 Broker Chain Semantic Gate | 30444125977 | failure | `6e93b3e0bee9` | 2026-07-29T10:33:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30444125977 |
| Dashboard Live UI Proof | 30443329865 | failure | `1e88f0a5ba44` | 2026-07-29T10:21:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30443329865 |
| Dashboard Visible Proof Warmed | 30443019576 | failure | `1e88f0a5ba44` | 2026-07-29T10:17:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30443019576 |
| Dashboard Visual Production Proof | 30442807421 | failure | `08ca51daf3eb` | 2026-07-29T10:14:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30442807421 |
| Dashboard Deploy Provenance Gate | 30442770737 | failure | `45beeb48f4d2` | 2026-07-29T10:13:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30442770737 |
| System3 Backend Live Simulation Proof | 30439040418 | failure | `a97766fd4b3c` | 2026-07-29T09:18:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30439040418 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Market Session Proof Runner | 30445681864 | in_progress | 2026-07-29T10:57:35Z |
| System3 Latest Truth Publish | 30445439303 | in_progress | 2026-07-29T10:53:51Z |
| Permanent Repo Render Safety | 30445216616 | in_progress | 2026-07-29T10:50:25Z |

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
