# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-24T16:33:02.188489Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `13`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `25`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30108456012 conclusion=failure commit=b1b236525ec0
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30108528697 conclusion=failure commit=b1b236525ec0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30107941389 conclusion=failure commit=7c4a0361332f
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30107920580 conclusion=failure commit=7c4a0361332f
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30107931895 conclusion=failure commit=7c4a0361332f
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30107920602 conclusion=failure commit=7c4a0361332f
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30107941442 conclusion=failure commit=7c4a0361332f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30107920597 conclusion=failure commit=7c4a0361332f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30107920748 conclusion=failure commit=7c4a0361332f
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=30107564865 conclusion=failure commit=93af4190d7f0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30106932350 conclusion=failure commit=93af4190d7f0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30106808449 conclusion=failure commit=8602514cd8b2
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30106862980 conclusion=failure commit=a68f302b4c3e
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
| Dashboard Visible Settle Proof | 30108456012 | failure | `b1b236525ec0` | 2026-07-24T16:30:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30108456012 |
| System3 Windows Self-Hosted Full Proof | 30108528697 | failure | `b1b236525ec0` | 2026-07-24T16:26:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30108528697 |
| Dashboard Visible Issue Tracker | 30107941389 | failure | `7c4a0361332f` | 2026-07-24T16:13:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30107941389 |
| Dashboard Shell Diagnostic | 30107920580 | failure | `7c4a0361332f` | 2026-07-24T16:08:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30107920580 |
| System3 Autopilot Proof Board | 30107931895 | failure | `7c4a0361332f` | 2026-07-24T16:07:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30107931895 |
| System3 Secure Install Credential Audit | 30107920602 | failure | `7c4a0361332f` | 2026-07-24T16:06:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30107920602 |
| System3 Experimental Solution Planner | 30107941442 | failure | `7c4a0361332f` | 2026-07-24T16:06:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30107941442 |
| Dashboard Visual Proof Strict Gate | 30107920597 | failure | `7c4a0361332f` | 2026-07-24T16:06:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30107920597 |
| Dashboard Visual Loading Postflight | 30107920748 | failure | `7c4a0361332f` | 2026-07-24T16:06:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30107920748 |
| System3 Workflow Failure Tracker | 30107564865 | failure | `93af4190d7f0` | 2026-07-24T16:00:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30107564865 |
| Dashboard Visible Proof Warmed | 30106932350 | failure | `93af4190d7f0` | 2026-07-24T15:50:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30106932350 |
| Dashboard Visible Auth-Resilient Proof | 30106808449 | failure | `8602514cd8b2` | 2026-07-24T15:48:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30106808449 |
| System3 Backend Live Simulation Proof | 30106862980 | failure | `a68f302b4c3e` | 2026-07-24T15:48:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30106862980 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 30109261569 | in_progress | 2026-07-24T16:29:44Z |

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
