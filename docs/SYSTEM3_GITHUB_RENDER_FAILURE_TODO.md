# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T21:19:02.611104Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `15`
GitHub workflows currently queued/in progress: `5`
Render failed endpoints: `12`
TODO count: `27`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30220711729 conclusion=failure commit=9430e9c1326d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30220462686 conclusion=failure commit=9430e9c1326d
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30220445470 conclusion=failure commit=9430e9c1326d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30220353881 conclusion=failure commit=9430e9c1326d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30220012650 conclusion=failure commit=f510ff7aedeb
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30219871824 conclusion=failure commit=b8d3de99b3ff
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30219866756 conclusion=failure commit=4d01049e9d63
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30219871833 conclusion=failure commit=b8d3de99b3ff
- [ ] Fix latest GitHub workflow 'Dashboard Visual Settle Normalizer' run=30219871811 conclusion=failure commit=b8d3de99b3ff
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30219846436 conclusion=failure commit=1826635b9aa6
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30219871817 conclusion=failure commit=b8d3de99b3ff
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30219871818 conclusion=failure commit=b8d3de99b3ff
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30219784671 conclusion=failure commit=fcc50dc6a59d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30219393593 conclusion=failure commit=7b53db9e6ef7
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30219354112 conclusion=failure commit=74ce0c13ca57
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
| System3 Safe Repair Runner | 30220711729 | failure | `9430e9c1326d` | 2026-07-26T21:18:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30220711729 |
| Dashboard Visible Auth-Resilient Proof | 30220462686 | failure | `9430e9c1326d` | 2026-07-26T21:10:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30220462686 |
| Dashboard Visual Proof Strict Gate | 30220445470 | failure | `9430e9c1326d` | 2026-07-26T21:08:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30220445470 |
| Dashboard Visible Settle Proof | 30220353881 | failure | `9430e9c1326d` | 2026-07-26T21:06:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30220353881 |
| Dashboard Visible Proof Current | 30220012650 | failure | `f510ff7aedeb` | 2026-07-26T20:56:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30220012650 |
| Dashboard Shell Diagnostic | 30219871824 | failure | `b8d3de99b3ff` | 2026-07-26T20:53:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30219871824 |
| Dashboard Visible Issue Tracker | 30219866756 | failure | `4d01049e9d63` | 2026-07-26T20:52:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30219866756 |
| System3 Secure Install Credential Audit | 30219871833 | failure | `b8d3de99b3ff` | 2026-07-26T20:52:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30219871833 |
| Dashboard Visual Settle Normalizer | 30219871811 | failure | `b8d3de99b3ff` | 2026-07-26T20:52:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30219871811 |
| System3 Autopilot Proof Board | 30219846436 | failure | `1826635b9aa6` | 2026-07-26T20:52:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30219846436 |
| System3 Experimental Solution Planner | 30219871817 | failure | `b8d3de99b3ff` | 2026-07-26T20:52:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30219871817 |
| Dashboard Visual Loading Postflight | 30219871818 | failure | `b8d3de99b3ff` | 2026-07-26T20:52:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30219871818 |
| .github/workflows/options-ml-training-proof.yml | 30219784671 | failure | `fcc50dc6a59d` | 2026-07-26T20:49:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30219784671 |
| Dashboard Visible Proof Warmed | 30219393593 | failure | `7b53db9e6ef7` | 2026-07-26T20:38:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30219393593 |
| System3 Backend Live Simulation Proof | 30219354112 | failure | `74ce0c13ca57` | 2026-07-26T20:37:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30219354112 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Windows Self-Hosted Full Proof | 30220364900 | in_progress | 2026-07-26T21:12:26Z |
| Options Big-Data Full History | 30219786428 | in_progress | 2026-07-26T20:49:45Z |
| Genesis System3 Global Safety CI | 30219786433 | queued | 2026-07-26T20:49:23Z |
| Options Big-Data Self-Hosted Model | 30219786458 | queued | 2026-07-26T20:49:22Z |
| Options Big-Data Research | 30219786438 | queued | 2026-07-26T20:49:22Z |

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
