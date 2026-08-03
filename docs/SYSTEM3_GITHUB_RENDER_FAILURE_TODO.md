# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T22:22:55.782919Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30855836783 conclusion=failure commit=da0fa8bf2359
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30855781831 conclusion=failure commit=da0fa8bf2359
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30855581732 conclusion=failure commit=61dd5cc0ac2c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30855516829 conclusion=failure commit=7f21f1a45c0a
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30853857015 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30853857029 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=30853857005 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=30853857016 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30853857052 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30853856099 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow 'Dashboard Visual Contract Check' run=30845368512 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'Dhan Only Data Truth Proof' run=30845368220 conclusion=failure commit=7d317001e66e
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
| Dashboard Visible Proof Warmed | 30855836783 | failure | `da0fa8bf2359` | 2026-08-03T21:44:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30855836783 |
| System3 Backend Live Simulation Proof | 30855781831 | failure | `da0fa8bf2359` | 2026-08-03T21:43:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30855781831 |
| Dashboard Deploy Provenance Gate | 30855581732 | failure | `61dd5cc0ac2c` | 2026-08-03T21:42:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30855581732 |
| Dashboard Visual Production Proof | 30855516829 | failure | `7f21f1a45c0a` | 2026-08-03T21:40:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30855516829 |
| System3 Latest Truth Publish | 30853857015 | failure | `4d69f889d293` | 2026-08-03T21:25:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853857015 |
| Permanent Repo Render Safety | 30853857029 | failure | `4d69f889d293` | 2026-08-03T21:25:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853857029 |
| Genesis System3 Global Safety CI | 30853857005 | failure | `4d69f889d293` | 2026-08-03T21:23:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853857005 |
| Dashboard Visible Proof Isolated | 30853857016 | failure | `4d69f889d293` | 2026-08-03T21:16:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853857016 |
| Dashboard Live UI Proof | 30853857052 | failure | `4d69f889d293` | 2026-08-03T21:15:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853857052 |
| .github/workflows/options-ml-training-proof.yml | 30853856099 | failure | `4d69f889d293` | 2026-08-03T21:15:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853856099 |
| Dashboard Visual Contract Check | 30845368512 | failure | `7d317001e66e` | 2026-08-03T19:21:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368512 |
| Dhan Only Data Truth Proof | 30845368220 | failure | `7d317001e66e` | 2026-08-03T19:21:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368220 |

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
