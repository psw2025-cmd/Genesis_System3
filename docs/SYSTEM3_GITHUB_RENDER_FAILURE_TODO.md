# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T21:25:01.618215Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `11`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=30853857005 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30853857140 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30853857075 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=30853857016 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30853857052 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30853856099 conclusion=failure commit=4d69f889d293
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30851527025 conclusion=failure commit=c147c07e22b3
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30851393952 conclusion=failure commit=dd9568ae3c9a
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30851341512 conclusion=failure commit=a1bc1e36aa1e
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
| Genesis System3 Global Safety CI | 30853857005 | failure | `4d69f889d293` | 2026-08-03T21:23:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853857005 |
| Dashboard Visual Production Proof | 30853857140 | failure | `4d69f889d293` | 2026-08-03T21:17:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853857140 |
| Dashboard Visible Proof Warmed | 30853857075 | failure | `4d69f889d293` | 2026-08-03T21:16:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853857075 |
| Dashboard Visible Proof Isolated | 30853857016 | failure | `4d69f889d293` | 2026-08-03T21:16:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853857016 |
| Dashboard Live UI Proof | 30853857052 | failure | `4d69f889d293` | 2026-08-03T21:15:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853857052 |
| .github/workflows/options-ml-training-proof.yml | 30853856099 | failure | `4d69f889d293` | 2026-08-03T21:15:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30853856099 |
| System3 Backend Live Simulation Proof | 30851527025 | failure | `c147c07e22b3` | 2026-08-03T20:44:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30851527025 |
| System3 Render Worker Preflight | 30851393952 | failure | `dd9568ae3c9a` | 2026-08-03T20:42:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30851393952 |
| Dashboard Deploy Provenance Gate | 30851341512 | failure | `a1bc1e36aa1e` | 2026-08-03T20:42:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30851341512 |
| Dashboard Visual Contract Check | 30845368512 | failure | `7d317001e66e` | 2026-08-03T19:21:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368512 |
| Dhan Only Data Truth Proof | 30845368220 | failure | `7d317001e66e` | 2026-08-03T19:21:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368220 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Actions Truth Autopsy | 30854528607 | in_progress | 2026-08-03T21:24:56Z |
| Permanent Repo Render Safety | 30853857029 | in_progress | 2026-08-03T21:15:38Z |
| System3 Latest Truth Publish | 30853857015 | in_progress | 2026-08-03T21:15:26Z |

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
