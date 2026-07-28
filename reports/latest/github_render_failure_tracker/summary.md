# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-28T08:56:32.081010Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `11`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30341969887 conclusion=failure commit=c2d535f39146
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30342803984 conclusion=failure commit=c2d535f39146
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30341683957 conclusion=failure commit=e7bf134542d7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30341098833 conclusion=failure commit=e7bf134542d7
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30341096530 conclusion=failure commit=e7bf134542d7
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30340974341 conclusion=failure commit=cfd53dd2ba2f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30340854267 conclusion=failure commit=984d78ede348
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30340883053 conclusion=failure commit=984d78ede348
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30340234238 conclusion=failure commit=584d0d1f6f52
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30340277618 conclusion=failure commit=584d0d1f6f52
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
| System3 Full Auto Truth | 30341969887 | failure | `c2d535f39146` | 2026-07-28T08:44:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30341969887 |
| System3 Broker Chain Semantic Gate | 30342803984 | failure | `c2d535f39146` | 2026-07-28T08:32:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30342803984 |
| Permanent Repo Render Safety | 30341683957 | failure | `e7bf134542d7` | 2026-07-28T08:25:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30341683957 |
| Dashboard Visible Proof Warmed | 30341098833 | failure | `e7bf134542d7` | 2026-07-28T08:08:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30341098833 |
| System3 Backend Live Simulation Proof | 30341096530 | failure | `e7bf134542d7` | 2026-07-28T08:07:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30341096530 |
| System3 Render Worker Preflight | 30340974341 | failure | `cfd53dd2ba2f` | 2026-07-28T08:05:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30340974341 |
| Dashboard Visual Production Proof | 30340854267 | failure | `984d78ede348` | 2026-07-28T08:04:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30340854267 |
| Dashboard Deploy Provenance Gate | 30340883053 | failure | `984d78ede348` | 2026-07-28T08:04:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30340883053 |
| System3 Market Session Proof Runner | 30340234238 | failure | `584d0d1f6f52` | 2026-07-28T07:58:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30340234238 |
| Dashboard Live UI Proof | 30340277618 | failure | `584d0d1f6f52` | 2026-07-28T07:55:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30340277618 |
| System3 Windows Self-Hosted Workflow Migration | 30329029225 | failure | `8cb5155b40be` | 2026-07-28T04:33:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30329029225 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30344311581 | in_progress | 2026-07-28T08:54:34Z |

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
