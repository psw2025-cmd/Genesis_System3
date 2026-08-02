# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-02T15:23:55.228348Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `4`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `16`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30752857122 conclusion=failure commit=3735f52d820d
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30752817042 conclusion=failure commit=3735f52d820d
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30752759004 conclusion=failure commit=f01f6f9d1f3c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30752745839 conclusion=failure commit=f01f6f9d1f3c
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
| Dashboard Visible Proof Warmed | 30752857122 | failure | `3735f52d820d` | 2026-08-02T14:47:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30752857122 |
| System3 Backend Live Simulation Proof | 30752817042 | failure | `3735f52d820d` | 2026-08-02T14:45:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30752817042 |
| Dashboard Deploy Provenance Gate | 30752759004 | failure | `f01f6f9d1f3c` | 2026-08-02T14:44:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30752759004 |
| Dashboard Visual Production Proof | 30752745839 | failure | `f01f6f9d1f3c` | 2026-08-02T14:44:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30752745839 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Workflow Failure Tracker | 30754253555 | in_progress | 2026-08-02T15:23:53Z |

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
