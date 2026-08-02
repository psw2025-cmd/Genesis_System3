# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-02T19:26:57.399887Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `5`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `17`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30761623807 conclusion=failure commit=603a365d2aec
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30761570927 conclusion=failure commit=603a365d2aec
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30761498932 conclusion=failure commit=2c8f68100bb0
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30761482532 conclusion=failure commit=a0024cd86f51
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30761458009 conclusion=failure commit=a0024cd86f51
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
| Dashboard Visible Proof Warmed | 30761623807 | failure | `603a365d2aec` | 2026-08-02T18:40:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30761623807 |
| System3 Backend Live Simulation Proof | 30761570927 | failure | `603a365d2aec` | 2026-08-02T18:38:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30761570927 |
| System3 Render Worker Preflight | 30761498932 | failure | `2c8f68100bb0` | 2026-08-02T18:36:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30761498932 |
| Dashboard Deploy Provenance Gate | 30761482532 | failure | `a0024cd86f51` | 2026-08-02T18:36:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30761482532 |
| Dashboard Visual Production Proof | 30761458009 | failure | `a0024cd86f51` | 2026-08-02T18:36:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30761458009 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Workflow Failure Tracker | 30763386143 | queued | 2026-08-02T19:26:55Z |

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
