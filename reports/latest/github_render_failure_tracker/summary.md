# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-25T15:23:37.875620Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `16`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `28`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30163426691 conclusion=failure commit=534de77a36b9
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30163100385 conclusion=failure commit=663b4f56457b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30163189226 conclusion=failure commit=663b4f56457b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30163211124 conclusion=failure commit=663b4f56457b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30163065684 conclusion=failure commit=663b4f56457b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30162305363 conclusion=failure commit=663b4f56457b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30162261359 conclusion=failure commit=080b70414833
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30162257445 conclusion=failure commit=080b70414833
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30162241006 conclusion=failure commit=22070f758af1
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30162258175 conclusion=failure commit=080b70414833
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30162276409 conclusion=failure commit=1ecfd465f7fd
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30162258193 conclusion=failure commit=080b70414833
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30162241018 conclusion=failure commit=22070f758af1
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30162179733 conclusion=failure commit=b4ae0b13cfc0
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30162190629 conclusion=failure commit=b4ae0b13cfc0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30162064561 conclusion=failure commit=6db6ec3f4ead
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
| System3 Safe Repair Runner | 30163426691 | failure | `534de77a36b9` | 2026-07-25T15:23:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30163426691 |
| System3 Windows Self-Hosted Full Proof | 30163100385 | failure | `663b4f56457b` | 2026-07-25T15:18:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30163100385 |
| Dashboard Visible Auth-Resilient Proof | 30163189226 | failure | `663b4f56457b` | 2026-07-25T15:14:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30163189226 |
| Dashboard Visual Proof Strict Gate | 30163211124 | failure | `663b4f56457b` | 2026-07-25T15:14:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30163211124 |
| Dashboard Visible Settle Proof | 30163065684 | failure | `663b4f56457b` | 2026-07-25T15:10:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30163065684 |
| Dashboard Visible Proof Warmed | 30162305363 | failure | `663b4f56457b` | 2026-07-25T14:47:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30162305363 |
| Dashboard Visible Issue Tracker | 30162261359 | failure | `080b70414833` | 2026-07-25T14:46:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30162261359 |
| System3 Backend Live Simulation Proof | 30162257445 | failure | `080b70414833` | 2026-07-25T14:46:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30162257445 |
| Dashboard Shell Diagnostic | 30162241006 | failure | `22070f758af1` | 2026-07-25T14:46:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30162241006 |
| System3 Autopilot Proof Board | 30162258175 | failure | `080b70414833` | 2026-07-25T14:46:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30162258175 |
| System3 Experimental Solution Planner | 30162276409 | failure | `1ecfd465f7fd` | 2026-07-25T14:46:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30162276409 |
| System3 Secure Install Credential Audit | 30162258193 | failure | `080b70414833` | 2026-07-25T14:45:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30162258193 |
| Dashboard Visual Loading Postflight | 30162241018 | failure | `22070f758af1` | 2026-07-25T14:44:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30162241018 |
| Dashboard Visual Production Proof | 30162179733 | failure | `b4ae0b13cfc0` | 2026-07-25T14:44:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30162179733 |
| Dashboard Deploy Provenance Gate | 30162190629 | failure | `b4ae0b13cfc0` | 2026-07-25T14:43:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30162190629 |
| Dashboard Visible Proof Current | 30162064561 | failure | `6db6ec3f4ead` | 2026-07-25T14:40:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30162064561 |

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
