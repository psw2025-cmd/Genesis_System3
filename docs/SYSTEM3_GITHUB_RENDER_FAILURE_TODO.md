# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-30T05:02:40.365643Z`
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

- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30514921167 conclusion=failure commit=11323d56f74a
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30514055102 conclusion=failure commit=275458e986fa
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30512872244 conclusion=failure commit=a4adb00e180d
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30513321843 conclusion=failure commit=d8d35a9d714c
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30512607209 conclusion=failure commit=a4adb00e180d
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30512769141 conclusion=failure commit=a4adb00e180d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30511140349 conclusion=failure commit=a4adb00e180d
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30511069341 conclusion=failure commit=a4adb00e180d
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30510957314 conclusion=failure commit=4974b7501b04
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30510931068 conclusion=failure commit=886f84dfa52d
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30510893726 conclusion=failure commit=886f84dfa52d
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
| System3 Market Session Proof Runner | 30514921167 | failure | `11323d56f74a` | 2026-07-30T04:53:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30514921167 |
| System3 Windows Self-Hosted Workflow Migration | 30514055102 | failure | `275458e986fa` | 2026-07-30T04:31:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30514055102 |
| System3 Full Auto Truth | 30512872244 | failure | `a4adb00e180d` | 2026-07-30T04:29:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30512872244 |
| System3 Broker Chain Semantic Gate | 30513321843 | failure | `d8d35a9d714c` | 2026-07-30T04:14:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30513321843 |
| Permanent Repo Render Safety | 30512607209 | failure | `a4adb00e180d` | 2026-07-30T04:08:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30512607209 |
| Dashboard Live UI Proof | 30512769141 | failure | `a4adb00e180d` | 2026-07-30T04:02:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30512769141 |
| Dashboard Visible Proof Warmed | 30511140349 | failure | `a4adb00e180d` | 2026-07-30T03:26:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30511140349 |
| System3 Backend Live Simulation Proof | 30511069341 | failure | `a4adb00e180d` | 2026-07-30T03:24:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30511069341 |
| System3 Render Worker Preflight | 30510957314 | failure | `4974b7501b04` | 2026-07-30T03:21:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30510957314 |
| Dashboard Deploy Provenance Gate | 30510931068 | failure | `886f84dfa52d` | 2026-07-30T03:21:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30510931068 |
| Dashboard Visual Production Proof | 30510893726 | failure | `886f84dfa52d` | 2026-07-30T03:20:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30510893726 |

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
