# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-02T18:20:35.312200Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30759428544 conclusion=failure commit=4494a7ecbb1d
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30759374042 conclusion=failure commit=4494a7ecbb1d
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30759298727 conclusion=failure commit=a160c6f3ec28
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30759282010 conclusion=failure commit=80347e9f8134
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30759245170 conclusion=failure commit=80347e9f8134
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
| Dashboard Visible Proof Warmed | 30759428544 | failure | `4494a7ecbb1d` | 2026-08-02T17:42:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30759428544 |
| System3 Backend Live Simulation Proof | 30759374042 | failure | `4494a7ecbb1d` | 2026-08-02T17:40:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30759374042 |
| System3 Render Worker Preflight | 30759298727 | failure | `a160c6f3ec28` | 2026-08-02T17:38:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30759298727 |
| Dashboard Deploy Provenance Gate | 30759282010 | failure | `80347e9f8134` | 2026-08-02T17:38:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30759282010 |
| Dashboard Visual Production Proof | 30759245170 | failure | `80347e9f8134` | 2026-08-02T17:37:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30759245170 |

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
