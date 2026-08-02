# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-02T01:34:43.569431Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `5`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `17`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30726220536 conclusion=failure commit=daefb9d4c47c
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30726199867 conclusion=failure commit=daefb9d4c47c
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=30726169742 conclusion=failure commit=cea2b5e00687
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30726157846 conclusion=failure commit=cea2b5e00687
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30726141794 conclusion=failure commit=cea2b5e00687
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
| Dashboard Visible Proof Warmed | 30726220536 | failure | `daefb9d4c47c` | 2026-08-02T01:00:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30726220536 |
| System3 Backend Live Simulation Proof | 30726199867 | failure | `daefb9d4c47c` | 2026-08-02T00:59:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30726199867 |
| System3 Workflow Failure Tracker | 30726169742 | failure | `cea2b5e00687` | 2026-08-02T00:57:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30726169742 |
| Dashboard Deploy Provenance Gate | 30726157846 | failure | `cea2b5e00687` | 2026-08-02T00:57:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30726157846 |
| Dashboard Visual Production Proof | 30726141794 | failure | `cea2b5e00687` | 2026-08-02T00:57:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30726141794 |

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
