# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T15:01:33.704982Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `14`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `26`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30817594931 conclusion=failure commit=58743ecdbb79
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30817536202 conclusion=failure commit=58743ecdbb79
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30817329490 conclusion=failure commit=e2bd71fd046f
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30817346783 conclusion=failure commit=e2bd71fd046f
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30810589818 conclusion=failure commit=509c96d50542
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30810426189 conclusion=failure commit=509c96d50542
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30811080508 conclusion=failure commit=509c96d50542
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30810401783 conclusion=failure commit=509c96d50542
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30810495753 conclusion=failure commit=509c96d50542
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30808393357 conclusion=failure commit=63a7adba2564
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=30803487489 conclusion=failure commit=c789ce37a997
- [ ] Fix latest GitHub workflow 'System3 Parallel Root-Cause Audit' run=30803487416 conclusion=failure commit=c789ce37a997
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30803485872 conclusion=failure commit=c789ce37a997
- [ ] Fix latest GitHub workflow 'Dhan Only Data Truth Proof' run=30801957996 conclusion=failure commit=051ed7b7d458
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
| Dashboard Visible Proof Warmed | 30817594931 | failure | `58743ecdbb79` | 2026-08-03T13:22:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30817594931 |
| System3 Backend Live Simulation Proof | 30817536202 | failure | `58743ecdbb79` | 2026-08-03T13:21:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30817536202 |
| Dashboard Visual Production Proof | 30817329490 | failure | `e2bd71fd046f` | 2026-08-03T13:19:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30817329490 |
| Dashboard Deploy Provenance Gate | 30817346783 | failure | `e2bd71fd046f` | 2026-08-03T13:18:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30817346783 |
| System3 Full Auto Truth | 30810589818 | failure | `509c96d50542` | 2026-08-03T12:07:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30810589818 |
| System3 Latest Truth Publish | 30810426189 | failure | `509c96d50542` | 2026-08-03T11:50:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30810426189 |
| System3 Broker Chain Semantic Gate | 30811080508 | failure | `509c96d50542` | 2026-08-03T11:50:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30811080508 |
| Permanent Repo Render Safety | 30810401783 | failure | `509c96d50542` | 2026-08-03T11:49:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30810401783 |
| Dashboard Live UI Proof | 30810495753 | failure | `509c96d50542` | 2026-08-03T11:41:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30810495753 |
| System3 Market Session Proof Runner | 30808393357 | failure | `63a7adba2564` | 2026-08-03T11:16:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30808393357 |
| Dashboard Visible Proof Isolated | 30803487489 | failure | `c789ce37a997` | 2026-08-03T09:56:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30803487489 |
| System3 Parallel Root-Cause Audit | 30803487416 | failure | `c789ce37a997` | 2026-08-03T09:56:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30803487416 |
| .github/workflows/options-ml-training-proof.yml | 30803485872 | failure | `c789ce37a997` | 2026-08-03T09:55:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30803485872 |
| Dhan Only Data Truth Proof | 30801957996 | failure | `051ed7b7d458` | 2026-08-03T09:34:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30801957996 |

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
