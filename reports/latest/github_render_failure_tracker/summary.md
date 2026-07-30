# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-30T10:43:38.339689Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `8`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `20`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30534954095 conclusion=failure commit=bb14f331336d
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30533957332 conclusion=failure commit=dace81cc85fa
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30534130703 conclusion=failure commit=dace81cc85fa
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30533379625 conclusion=failure commit=dace81cc85fa
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30533358190 conclusion=failure commit=dace81cc85fa
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30533167224 conclusion=failure commit=ae505c0096d4
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30533172853 conclusion=failure commit=ae505c0096d4
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30524368255 conclusion=failure commit=f42ecf6aac26
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
| System3 Broker Chain Semantic Gate | 30534954095 | failure | `bb14f331336d` | 2026-07-30T10:31:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30534954095 |
| Permanent Repo Render Safety | 30533957332 | failure | `dace81cc85fa` | 2026-07-30T10:24:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30533957332 |
| Dashboard Live UI Proof | 30534130703 | failure | `dace81cc85fa` | 2026-07-30T10:18:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30534130703 |
| System3 Backend Live Simulation Proof | 30533379625 | failure | `dace81cc85fa` | 2026-07-30T10:06:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30533379625 |
| Dashboard Visible Proof Warmed | 30533358190 | failure | `dace81cc85fa` | 2026-07-30T10:06:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30533358190 |
| Dashboard Visual Production Proof | 30533167224 | failure | `ae505c0096d4` | 2026-07-30T10:04:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30533167224 |
| Dashboard Deploy Provenance Gate | 30533172853 | failure | `ae505c0096d4` | 2026-07-30T10:03:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30533172853 |
| System3 Market Session Proof Runner | 30524368255 | failure | `f42ecf6aac26` | 2026-07-30T07:55:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30524368255 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Full Auto Truth | 30534239093 | in_progress | 2026-07-30T10:19:49Z |

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
