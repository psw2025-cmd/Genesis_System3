# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-02T12:23:32.183917Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30746335839 conclusion=failure commit=2402a6e0cc32
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30746307470 conclusion=failure commit=2402a6e0cc32
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30746248118 conclusion=failure commit=636528b407b9
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30746236461 conclusion=failure commit=e8e1c53c3e2a
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30746207777 conclusion=failure commit=e8e1c53c3e2a
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30732685725 conclusion=failure commit=07b199fc2eaf
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
| Dashboard Visible Proof Warmed | 30746335839 | failure | `2402a6e0cc32` | 2026-08-02T11:44:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30746335839 |
| System3 Backend Live Simulation Proof | 30746307470 | failure | `2402a6e0cc32` | 2026-08-02T11:43:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30746307470 |
| System3 Render Worker Preflight | 30746248118 | failure | `636528b407b9` | 2026-08-02T11:41:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30746248118 |
| Dashboard Deploy Provenance Gate | 30746236461 | failure | `e8e1c53c3e2a` | 2026-08-02T11:41:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30746236461 |
| Dashboard Visual Production Proof | 30746207777 | failure | `e8e1c53c3e2a` | 2026-08-02T11:40:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30746207777 |
| System3 Windows Self-Hosted Workflow Migration | 30732685725 | failure | `07b199fc2eaf` | 2026-08-02T04:38:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30732685725 |

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
