# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-30T08:55:48.736660Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30526243449 conclusion=failure commit=fb8c1d5af900
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30527034181 conclusion=failure commit=c65da5f414e0
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30525941541 conclusion=failure commit=fb8c1d5af900
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30526148666 conclusion=failure commit=fb8c1d5af900
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30525212956 conclusion=failure commit=fb8c1d5af900
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30525234518 conclusion=failure commit=fb8c1d5af900
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30524782522 conclusion=failure commit=3c65d577b1e0
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30524812339 conclusion=failure commit=3c65d577b1e0
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30524368255 conclusion=failure commit=f42ecf6aac26
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30514055102 conclusion=failure commit=275458e986fa
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
| System3 Full Auto Truth | 30526243449 | failure | `fb8c1d5af900` | 2026-07-30T08:44:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30526243449 |
| System3 Broker Chain Semantic Gate | 30527034181 | failure | `c65da5f414e0` | 2026-07-30T08:31:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30527034181 |
| Permanent Repo Render Safety | 30525941541 | failure | `fb8c1d5af900` | 2026-07-30T08:24:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30525941541 |
| Dashboard Live UI Proof | 30526148666 | failure | `fb8c1d5af900` | 2026-07-30T08:18:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30526148666 |
| Dashboard Visible Proof Warmed | 30525212956 | failure | `fb8c1d5af900` | 2026-07-30T08:05:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30525212956 |
| System3 Backend Live Simulation Proof | 30525234518 | failure | `fb8c1d5af900` | 2026-07-30T08:05:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30525234518 |
| Dashboard Visual Production Proof | 30524782522 | failure | `3c65d577b1e0` | 2026-07-30T07:59:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30524782522 |
| Dashboard Deploy Provenance Gate | 30524812339 | failure | `3c65d577b1e0` | 2026-07-30T07:59:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30524812339 |
| System3 Market Session Proof Runner | 30524368255 | failure | `f42ecf6aac26` | 2026-07-30T07:55:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30524368255 |
| System3 Windows Self-Hosted Workflow Migration | 30514055102 | failure | `275458e986fa` | 2026-07-30T04:31:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30514055102 |

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
