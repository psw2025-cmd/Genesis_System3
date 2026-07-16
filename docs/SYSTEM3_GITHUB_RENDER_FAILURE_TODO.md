# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-16T01:34:27.586617Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29464436673 conclusion=failure commit=d898ef96efd3
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29464436674 conclusion=failure commit=d898ef96efd3
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29464417919 conclusion=failure commit=24d4ef0e4b82
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29464417846 conclusion=failure commit=24d4ef0e4b82
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=29462569088 conclusion=cancelled commit=ea5541abe590
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29462626063 conclusion=failure commit=2d01a7dc5a9d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29462459856 conclusion=failure commit=ea5541abe590
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29462532100 conclusion=failure commit=ea5541abe590
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29462559917 conclusion=failure commit=ea5541abe590
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29462656449 conclusion=failure commit=2d01a7dc5a9d
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29462638996 conclusion=failure commit=2d01a7dc5a9d
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=29462592678 conclusion=failure commit=ea5541abe590
- [ ] Fix Render endpoint /: HTTP status 503 status=503
- [ ] Fix Render endpoint /ui/: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/health: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/state: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/paper: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 503 status=503

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Secure Install Credential Audit | 29464436673 | failure | `d898ef96efd3` | 2026-07-16T01:34:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29464436673 |
| System3 Experimental Solution Planner | 29464436674 | failure | `d898ef96efd3` | 2026-07-16T01:34:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29464436674 |
| Dashboard Visual Proof Strict Gate | 29464417919 | failure | `24d4ef0e4b82` | 2026-07-16T01:33:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29464417919 |
| Dashboard Visual Loading Postflight | 29464417846 | failure | `24d4ef0e4b82` | 2026-07-16T01:33:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29464417846 |
| Dashboard Visual Production Proof | 29462569088 | cancelled | `ea5541abe590` | 2026-07-16T01:21:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29462569088 |
| Dashboard Visible Auth-Resilient Proof | 29462626063 | failure | `2d01a7dc5a9d` | 2026-07-16T01:10:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29462626063 |
| Dashboard Visible Proof Current | 29462459856 | failure | `ea5541abe590` | 2026-07-16T01:00:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29462459856 |
| Dashboard Visible Settle Proof | 29462532100 | failure | `ea5541abe590` | 2026-07-16T00:56:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29462532100 |
| System3 Windows Self-Hosted Full Proof | 29462559917 | failure | `ea5541abe590` | 2026-07-16T00:55:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29462559917 |
| Dashboard Visible Proof Warmed | 29462656449 | failure | `2d01a7dc5a9d` | 2026-07-16T00:53:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29462656449 |
| System3 Backend Live Simulation Proof | 29462638996 | failure | `2d01a7dc5a9d` | 2026-07-16T00:52:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29462638996 |
| Dashboard Deploy Provenance Gate | 29462592678 | failure | `ea5541abe590` | 2026-07-16T00:52:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29462592678 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29464417826 | in_progress | 2026-07-16T01:34:06Z |
| System3 Autopilot Proof Board | 29464436669 | in_progress | 2026-07-16T01:34:05Z |
| Dashboard Shell Diagnostic | 29464417897 | in_progress | 2026-07-16T01:33:36Z |
| Dashboard Visible Issue Tracker | 29463969102 | in_progress | 2026-07-16T01:33:34Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 503 | HTTP status 503 | `none` |
| `/ui/` | 503 | HTTP status 503 | `none` |
| `/api/health` | 503 | HTTP status 503 | `none` |
| `/api/state` | 503 | HTTP status 503 | `none` |
| `/api/deploy/info` | 503 | HTTP status 503 | `none` |
| `/api/broker/diagnose` | 503 | HTTP status 503 | `none` |
| `/api/broker/funds` | 503 | HTTP status 503 | `none` |
| `/api/broker/holdings` | 503 | HTTP status 503 | `none` |
| `/api/broker/positions/live` | 503 | HTTP status 503 | `none` |
| `/api/scanner/top_contract_gainers` | 503 | HTTP status 503 | `none` |
| `/api/paper` | 503 | HTTP status 503 | `none` |
| `/api/ml/performance` | 503 | HTTP status 503 | `none` |
