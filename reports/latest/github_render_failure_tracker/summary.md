# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-02T03:03:57.038594Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `4`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `16`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30728138462 conclusion=failure commit=7fd67c50037d
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30728075217 conclusion=failure commit=7fd67c50037d
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30727945458 conclusion=failure commit=60af05ed4989
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30727915036 conclusion=failure commit=60af05ed4989
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
| Dashboard Visible Proof Warmed | 30728138462 | failure | `7fd67c50037d` | 2026-08-02T02:03:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30728138462 |
| System3 Backend Live Simulation Proof | 30728075217 | failure | `7fd67c50037d` | 2026-08-02T02:01:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30728075217 |
| Dashboard Deploy Provenance Gate | 30727945458 | failure | `60af05ed4989` | 2026-08-02T01:57:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30727945458 |
| Dashboard Visual Production Proof | 30727915036 | failure | `60af05ed4989` | 2026-08-02T01:56:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30727915036 |

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
