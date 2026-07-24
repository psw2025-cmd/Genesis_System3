# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-24T21:24:19.699992Z`
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

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30127420554 conclusion=failure commit=3b6239db7644
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30126743923 conclusion=failure commit=5c470e845d11
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30127076298 conclusion=failure commit=5c470e845d11
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30126998386 conclusion=failure commit=5c470e845d11
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30126721884 conclusion=failure commit=5c470e845d11
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30125340152 conclusion=failure commit=5c470e845d11
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30125277573 conclusion=failure commit=2f8b6f57770e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30125230541 conclusion=failure commit=f109c2fa7181
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30125177869 conclusion=failure commit=41536c0bd197
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30125208594 conclusion=failure commit=59c459f04b7a
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30125232910 conclusion=failure commit=f109c2fa7181
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30125204642 conclusion=failure commit=59c459f04b7a
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30125104413 conclusion=failure commit=f2c36cfaf3ca
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30125177883 conclusion=failure commit=41536c0bd197
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=30125131782 conclusion=failure commit=9457120d6166
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30125082640 conclusion=failure commit=f2c36cfaf3ca
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30124746784 conclusion=failure commit=b2da6149afbe
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
| System3 Safe Repair Runner | 30127420554 | failure | `3b6239db7644` | 2026-07-24T21:23:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30127420554 |
| System3 Windows Self-Hosted Full Proof | 30126743923 | failure | `5c470e845d11` | 2026-07-24T21:19:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30126743923 |
| Dashboard Visual Proof Strict Gate | 30127076298 | failure | `5c470e845d11` | 2026-07-24T21:15:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30127076298 |
| Dashboard Visible Auth-Resilient Proof | 30126998386 | failure | `5c470e845d11` | 2026-07-24T21:15:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30126998386 |
| Dashboard Visible Settle Proof | 30126721884 | failure | `5c470e845d11` | 2026-07-24T21:09:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30126721884 |
| Dashboard Visible Proof Warmed | 30125340152 | failure | `5c470e845d11` | 2026-07-24T20:47:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30125340152 |
| System3 Backend Live Simulation Proof | 30125277573 | failure | `2f8b6f57770e` | 2026-07-24T20:46:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30125277573 |
| Dashboard Visible Issue Tracker | 30125230541 | failure | `f109c2fa7181` | 2026-07-24T20:45:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30125230541 |
| Dashboard Shell Diagnostic | 30125177869 | failure | `41536c0bd197` | 2026-07-24T20:45:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30125177869 |
| System3 Autopilot Proof Board | 30125208594 | failure | `59c459f04b7a` | 2026-07-24T20:45:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30125208594 |
| System3 Experimental Solution Planner | 30125232910 | failure | `f109c2fa7181` | 2026-07-24T20:45:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30125232910 |
| System3 Secure Install Credential Audit | 30125204642 | failure | `59c459f04b7a` | 2026-07-24T20:44:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30125204642 |
| Dashboard Deploy Provenance Gate | 30125104413 | failure | `f2c36cfaf3ca` | 2026-07-24T20:44:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30125104413 |
| Dashboard Visual Loading Postflight | 30125177883 | failure | `41536c0bd197` | 2026-07-24T20:44:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30125177883 |
| System3 Workflow Failure Tracker | 30125131782 | failure | `9457120d6166` | 2026-07-24T20:43:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30125131782 |
| Dashboard Visual Production Proof | 30125082640 | failure | `f2c36cfaf3ca` | 2026-07-24T20:43:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30125082640 |
| Dashboard Visible Proof Current | 30124746784 | failure | `b2da6149afbe` | 2026-07-24T20:37:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30124746784 |

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
