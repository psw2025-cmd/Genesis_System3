# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-02T20:48:45.554793Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `2`
GitHub workflows currently queued/in progress: `14`
Render failed endpoints: `12`
TODO count: `14`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30766449998 conclusion=failure commit=1e8dca59755e
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30765986506 conclusion=failure commit=0eb1d76b2bfe
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
| .github/workflows/options-ml-training-proof.yml | 30766449998 | failure | `1e8dca59755e` | 2026-08-02T20:48:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30766449998 |
| System3 Backend Live Simulation Proof | 30765986506 | failure | `0eb1d76b2bfe` | 2026-08-02T20:36:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30765986506 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Deploy Provenance Gate | 30766450412 | in_progress | 2026-08-02T20:48:42Z |
| Dashboard Visible Proof Isolated | 30766450429 | in_progress | 2026-08-02T20:48:41Z |
| Genesis System3 Global Safety CI | 30766450393 | in_progress | 2026-08-02T20:48:41Z |
| Cloud Runtime Check | 30766450476 | in_progress | 2026-08-02T20:48:40Z |
| Dashboard Live UI Proof | 30766450431 | in_progress | 2026-08-02T20:48:40Z |
| System3 Render Worker Preflight | 30766450423 | in_progress | 2026-08-02T20:48:40Z |
| Dashboard Visual Production Proof | 30766450413 | in_progress | 2026-08-02T20:48:40Z |
| System3 Render Worker Issue Proof | 30766450398 | in_progress | 2026-08-02T20:48:40Z |
| System3 Render Worker Env Audit | 30766450397 | in_progress | 2026-08-02T20:48:40Z |
| Dashboard Visible Proof Warmed | 30766450394 | in_progress | 2026-08-02T20:48:40Z |
| Graph Update: pip in /dashboard/backend #1500739048 | 30766451450 | queued | 2026-08-02T20:48:39Z |
| Permanent Repo Render Safety | 30766450408 | queued | 2026-08-02T20:48:37Z |
| System3 Parallel Root-Cause Audit | 30766450401 | queued | 2026-08-02T20:48:37Z |
| System3 Latest Truth Publish | 30766450382 | queued | 2026-08-02T20:48:37Z |

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
