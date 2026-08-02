# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-02T20:20:58.935595Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `18`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30765245535 conclusion=failure commit=8cb138eb5ac4
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30764058915 conclusion=failure commit=9e4d08147bd2
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30764017237 conclusion=failure commit=9e4d08147bd2
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30763942519 conclusion=failure commit=2a366284b496
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30763925678 conclusion=failure commit=2a366284b496
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30763912432 conclusion=failure commit=2a366284b496
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
| .github/workflows/options-ml-training-proof.yml | 30765245535 | failure | `8cb138eb5ac4` | 2026-08-02T20:16:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30765245535 |
| Dashboard Visible Proof Warmed | 30764058915 | failure | `9e4d08147bd2` | 2026-08-02T19:45:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30764058915 |
| System3 Backend Live Simulation Proof | 30764017237 | failure | `9e4d08147bd2` | 2026-08-02T19:44:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30764017237 |
| System3 Render Worker Preflight | 30763942519 | failure | `2a366284b496` | 2026-08-02T19:41:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30763942519 |
| Dashboard Deploy Provenance Gate | 30763925678 | failure | `2a366284b496` | 2026-08-02T19:41:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30763925678 |
| Dashboard Visual Production Proof | 30763912432 | failure | `2a366284b496` | 2026-08-02T19:41:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30763912432 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Genesis System3 Global Safety CI | 30765247899 | queued | 2026-08-02T20:17:48Z |

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
