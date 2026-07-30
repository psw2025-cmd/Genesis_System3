# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-30T09:52:01.588948Z`
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

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30530441382 conclusion=failure commit=a95d6dabedbc
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30531048203 conclusion=failure commit=caa546145b36
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30530252605 conclusion=failure commit=a95d6dabedbc
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30530338958 conclusion=failure commit=a95d6dabedbc
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30529957961 conclusion=failure commit=a95d6dabedbc
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30529883433 conclusion=failure commit=a95d6dabedbc
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30529706045 conclusion=failure commit=b67ccebd6f31
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30529714649 conclusion=failure commit=b67ccebd6f31
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30529644761 conclusion=failure commit=b67ccebd6f31
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30524368255 conclusion=failure commit=f42ecf6aac26
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30514055102 conclusion=failure commit=275458e986fa
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
| System3 Full Auto Truth | 30530441382 | failure | `a95d6dabedbc` | 2026-07-30T09:47:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30530441382 |
| System3 Broker Chain Semantic Gate | 30531048203 | failure | `caa546145b36` | 2026-07-30T09:32:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30531048203 |
| Permanent Repo Render Safety | 30530252605 | failure | `a95d6dabedbc` | 2026-07-30T09:29:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30530252605 |
| Dashboard Live UI Proof | 30530338958 | failure | `a95d6dabedbc` | 2026-07-30T09:21:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30530338958 |
| Dashboard Visible Proof Warmed | 30529957961 | failure | `a95d6dabedbc` | 2026-07-30T09:16:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30529957961 |
| System3 Backend Live Simulation Proof | 30529883433 | failure | `a95d6dabedbc` | 2026-07-30T09:14:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30529883433 |
| Dashboard Deploy Provenance Gate | 30529706045 | failure | `b67ccebd6f31` | 2026-07-30T09:12:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30529706045 |
| System3 Render Worker Preflight | 30529714649 | failure | `b67ccebd6f31` | 2026-07-30T09:12:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30529714649 |
| Dashboard Visual Production Proof | 30529644761 | failure | `b67ccebd6f31` | 2026-07-30T09:11:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30529644761 |
| System3 Market Session Proof Runner | 30524368255 | failure | `f42ecf6aac26` | 2026-07-30T07:55:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30524368255 |
| System3 Windows Self-Hosted Workflow Migration | 30514055102 | failure | `275458e986fa` | 2026-07-30T04:31:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30514055102 |

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
