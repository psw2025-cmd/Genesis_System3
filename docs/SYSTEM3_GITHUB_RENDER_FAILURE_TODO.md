# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-01T03:03:36.028581Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30679214786 conclusion=failure commit=e414dcca7cda
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30679140953 conclusion=failure commit=e414dcca7cda
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30678997576 conclusion=failure commit=07272c0a8bf2
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30678956481 conclusion=failure commit=07272c0a8bf2
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
| Dashboard Visible Proof Warmed | 30679214786 | failure | `e414dcca7cda` | 2026-08-01T02:04:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30679214786 |
| System3 Backend Live Simulation Proof | 30679140953 | failure | `e414dcca7cda` | 2026-08-01T02:01:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30679140953 |
| Dashboard Deploy Provenance Gate | 30678997576 | failure | `07272c0a8bf2` | 2026-08-01T01:57:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30678997576 |
| Dashboard Visual Production Proof | 30678956481 | failure | `07272c0a8bf2` | 2026-08-01T01:56:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30678956481 |

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
