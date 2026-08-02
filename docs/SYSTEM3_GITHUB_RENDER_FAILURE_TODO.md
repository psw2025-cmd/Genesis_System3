# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-02T05:04:59.046853Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `18`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30732685725 conclusion=failure commit=07b199fc2eaf
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30730743941 conclusion=failure commit=07b199fc2eaf
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30730677288 conclusion=failure commit=07b199fc2eaf
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30730579958 conclusion=failure commit=49f2cdf2c3dc
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30730559494 conclusion=failure commit=1bcd26411e1d
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30730531739 conclusion=failure commit=1bcd26411e1d
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
| System3 Windows Self-Hosted Workflow Migration | 30732685725 | failure | `07b199fc2eaf` | 2026-08-02T04:38:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30732685725 |
| Dashboard Visible Proof Warmed | 30730743941 | failure | `07b199fc2eaf` | 2026-08-02T03:31:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30730743941 |
| System3 Backend Live Simulation Proof | 30730677288 | failure | `07b199fc2eaf` | 2026-08-02T03:28:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30730677288 |
| System3 Render Worker Preflight | 30730579958 | failure | `49f2cdf2c3dc` | 2026-08-02T03:25:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30730579958 |
| Dashboard Deploy Provenance Gate | 30730559494 | failure | `1bcd26411e1d` | 2026-08-02T03:24:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30730559494 |
| Dashboard Visual Production Proof | 30730531739 | failure | `1bcd26411e1d` | 2026-08-02T03:24:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30730531739 |

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
