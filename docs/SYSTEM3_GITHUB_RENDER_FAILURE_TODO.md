# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T00:32:35.914293Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `13`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `25`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30772741755 conclusion=failure commit=f331fae7aa69
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30772693516 conclusion=failure commit=f331fae7aa69
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30772594458 conclusion=failure commit=3b344d40e108
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30772609371 conclusion=failure commit=3b344d40e108
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30772563405 conclusion=failure commit=3b344d40e108
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30766450382 conclusion=failure commit=1e8dca59755e
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30766450408 conclusion=failure commit=1e8dca59755e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=30766450429 conclusion=failure commit=1e8dca59755e
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30766450431 conclusion=failure commit=1e8dca59755e
- [ ] Fix latest GitHub workflow 'System3 Parallel Root-Cause Audit' run=30766450401 conclusion=failure commit=1e8dca59755e
- [ ] Fix latest GitHub workflow 'System3 Render Worker Issue Proof' run=30766450398 conclusion=failure commit=1e8dca59755e
- [ ] Fix latest GitHub workflow 'System3 Render Worker Env Audit' run=30766450397 conclusion=failure commit=1e8dca59755e
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30766449998 conclusion=failure commit=1e8dca59755e
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
| Dashboard Visible Proof Warmed | 30772741755 | failure | `f331fae7aa69` | 2026-08-02T23:41:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30772741755 |
| System3 Backend Live Simulation Proof | 30772693516 | failure | `f331fae7aa69` | 2026-08-02T23:39:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30772693516 |
| Dashboard Deploy Provenance Gate | 30772594458 | failure | `3b344d40e108` | 2026-08-02T23:36:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30772594458 |
| System3 Render Worker Preflight | 30772609371 | failure | `3b344d40e108` | 2026-08-02T23:36:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30772609371 |
| Dashboard Visual Production Proof | 30772563405 | failure | `3b344d40e108` | 2026-08-02T23:35:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30772563405 |
| System3 Latest Truth Publish | 30766450382 | failure | `1e8dca59755e` | 2026-08-02T20:59:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30766450382 |
| Permanent Repo Render Safety | 30766450408 | failure | `1e8dca59755e` | 2026-08-02T20:58:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30766450408 |
| Dashboard Visible Proof Isolated | 30766450429 | failure | `1e8dca59755e` | 2026-08-02T20:49:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30766450429 |
| Dashboard Live UI Proof | 30766450431 | failure | `1e8dca59755e` | 2026-08-02T20:49:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30766450431 |
| System3 Parallel Root-Cause Audit | 30766450401 | failure | `1e8dca59755e` | 2026-08-02T20:49:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30766450401 |
| System3 Render Worker Issue Proof | 30766450398 | failure | `1e8dca59755e` | 2026-08-02T20:48:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30766450398 |
| System3 Render Worker Env Audit | 30766450397 | failure | `1e8dca59755e` | 2026-08-02T20:48:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30766450397 |
| .github/workflows/options-ml-training-proof.yml | 30766449998 | failure | `1e8dca59755e` | 2026-08-02T20:48:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30766449998 |

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
