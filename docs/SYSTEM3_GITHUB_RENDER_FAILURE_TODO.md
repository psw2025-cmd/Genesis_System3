# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-31T14:49:20.270515Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30636879055 conclusion=failure commit=d99d7aaef299
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30636769882 conclusion=failure commit=d99d7aaef299
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30636501602 conclusion=failure commit=5eb7608865d1
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30636450796 conclusion=failure commit=d5230eb62650
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30636375196 conclusion=failure commit=d5230eb62650
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30626904525 conclusion=failure commit=1164098dbfde
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30627316004 conclusion=failure commit=1164098dbfde
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30626482567 conclusion=failure commit=d806ee0d20bb
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30626441575 conclusion=failure commit=d806ee0d20bb
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30626586701 conclusion=failure commit=7f0041ec3bee
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30625405965 conclusion=failure commit=b60800aec82a
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
| Dashboard Visible Proof Warmed | 30636879055 | failure | `d99d7aaef299` | 2026-07-31T14:02:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30636879055 |
| System3 Backend Live Simulation Proof | 30636769882 | failure | `d99d7aaef299` | 2026-07-31T14:00:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30636769882 |
| System3 Render Worker Preflight | 30636501602 | failure | `5eb7608865d1` | 2026-07-31T13:56:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30636501602 |
| Dashboard Deploy Provenance Gate | 30636450796 | failure | `d5230eb62650` | 2026-07-31T13:56:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30636450796 |
| Dashboard Visual Production Proof | 30636375196 | failure | `d5230eb62650` | 2026-07-31T13:55:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30636375196 |
| System3 Full Auto Truth | 30626904525 | failure | `1164098dbfde` | 2026-07-31T11:48:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30626904525 |
| System3 Broker Chain Semantic Gate | 30627316004 | failure | `1164098dbfde` | 2026-07-31T11:31:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30627316004 |
| System3 Latest Truth Publish | 30626482567 | failure | `d806ee0d20bb` | 2026-07-31T11:26:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30626482567 |
| Permanent Repo Render Safety | 30626441575 | failure | `d806ee0d20bb` | 2026-07-31T11:25:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30626441575 |
| Dashboard Live UI Proof | 30626586701 | failure | `7f0041ec3bee` | 2026-07-31T11:19:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30626586701 |
| System3 Market Session Proof Runner | 30625405965 | failure | `b60800aec82a` | 2026-07-31T11:02:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30625405965 |

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
