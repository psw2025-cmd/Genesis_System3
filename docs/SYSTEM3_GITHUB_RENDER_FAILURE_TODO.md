# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-29T03:03:04.219403Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30415757262 conclusion=failure commit=d667409d9ee1
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30415663623 conclusion=failure commit=d667409d9ee1
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30415500957 conclusion=failure commit=adcc51494561
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30415474103 conclusion=failure commit=c6313b3debab
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30415422245 conclusion=failure commit=72a8c12e4c8f
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
| Dashboard Visible Proof Warmed | 30415757262 | failure | `d667409d9ee1` | 2026-07-29T02:03:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30415757262 |
| System3 Backend Live Simulation Proof | 30415663623 | failure | `d667409d9ee1` | 2026-07-29T02:01:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30415663623 |
| System3 Render Worker Preflight | 30415500957 | failure | `adcc51494561` | 2026-07-29T01:57:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30415500957 |
| Dashboard Deploy Provenance Gate | 30415474103 | failure | `c6313b3debab` | 2026-07-29T01:57:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30415474103 |
| Dashboard Visual Production Proof | 30415422245 | failure | `72a8c12e4c8f` | 2026-07-29T01:56:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30415422245 |

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
