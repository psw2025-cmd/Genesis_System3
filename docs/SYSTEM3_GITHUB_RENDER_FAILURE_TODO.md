# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-25T11:26:20.821933Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `17`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `29`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30156161115 conclusion=failure commit=078a00c0fea2
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30155898323 conclusion=failure commit=beb10d806b43
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30155861007 conclusion=failure commit=beb10d806b43
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30155140269 conclusion=failure commit=19941675b3f9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30155106280 conclusion=failure commit=0e12f0c0a1d8
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30155085490 conclusion=failure commit=02652dd909b9
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30155099976 conclusion=failure commit=58b96d3ce8fa
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30155110397 conclusion=failure commit=fe3df64f90b7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30155085902 conclusion=failure commit=02652dd909b9
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30155112221 conclusion=failure commit=fe3df64f90b7
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30155097872 conclusion=failure commit=58b96d3ce8fa
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30155085538 conclusion=failure commit=02652dd909b9
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30155085495 conclusion=failure commit=02652dd909b9
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30155026499 conclusion=failure commit=e5be712149a0
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30155051331 conclusion=failure commit=e5be712149a0
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30155061080 conclusion=failure commit=e5be712149a0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30154838193 conclusion=failure commit=5d7c2f43a5da
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
| System3 Safe Repair Runner | 30156161115 | failure | `078a00c0fea2` | 2026-07-25T11:25:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30156161115 |
| System3 Windows Self-Hosted Full Proof | 30155898323 | failure | `beb10d806b43` | 2026-07-25T11:21:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155898323 |
| Dashboard Visible Settle Proof | 30155861007 | failure | `beb10d806b43` | 2026-07-25T11:13:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155861007 |
| Dashboard Visible Proof Warmed | 30155140269 | failure | `19941675b3f9` | 2026-07-25T10:49:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155140269 |
| Dashboard Visible Issue Tracker | 30155106280 | failure | `0e12f0c0a1d8` | 2026-07-25T10:49:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155106280 |
| Dashboard Shell Diagnostic | 30155085490 | failure | `02652dd909b9` | 2026-07-25T10:48:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155085490 |
| System3 Autopilot Proof Board | 30155099976 | failure | `58b96d3ce8fa` | 2026-07-25T10:48:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155099976 |
| System3 Backend Live Simulation Proof | 30155110397 | failure | `fe3df64f90b7` | 2026-07-25T10:48:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155110397 |
| Dashboard Visible Auth-Resilient Proof | 30155085902 | failure | `02652dd909b9` | 2026-07-25T10:48:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155085902 |
| System3 Experimental Solution Planner | 30155112221 | failure | `fe3df64f90b7` | 2026-07-25T10:48:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155112221 |
| System3 Secure Install Credential Audit | 30155097872 | failure | `58b96d3ce8fa` | 2026-07-25T10:48:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155097872 |
| Dashboard Visual Loading Postflight | 30155085538 | failure | `02652dd909b9` | 2026-07-25T10:47:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155085538 |
| Dashboard Visual Proof Strict Gate | 30155085495 | failure | `02652dd909b9` | 2026-07-25T10:47:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155085495 |
| Dashboard Visual Production Proof | 30155026499 | failure | `e5be712149a0` | 2026-07-25T10:46:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155026499 |
| Dashboard Deploy Provenance Gate | 30155051331 | failure | `e5be712149a0` | 2026-07-25T10:46:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155051331 |
| System3 Render Worker Preflight | 30155061080 | failure | `e5be712149a0` | 2026-07-25T10:46:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30155061080 |
| Dashboard Visible Proof Current | 30154838193 | failure | `5d7c2f43a5da` | 2026-07-25T10:39:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30154838193 |

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
