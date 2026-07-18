# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T10:29:47.200190Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29640903614 conclusion=failure commit=5f607c391728
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29640903648 conclusion=failure commit=5f607c391728
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29640903620 conclusion=failure commit=5f607c391728
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29640893239 conclusion=failure commit=30fb51ebef9b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29640893198 conclusion=failure commit=30fb51ebef9b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29640211220 conclusion=failure commit=03171de0ed24
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29639824503 conclusion=failure commit=0ba3d92076b9
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29639745143 conclusion=failure commit=a06f6f69e7a7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29639826131 conclusion=failure commit=ee39531697c7
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29639797957 conclusion=failure commit=0ba3d92076b9
- [ ] Fix Render endpoint /: HTTP status 502 status=502
- [ ] Fix Render endpoint /ui/: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/health: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/state: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/paper: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 502 status=502

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Autopilot Proof Board | 29640903614 | failure | `5f607c391728` | 2026-07-18T10:29:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29640903614 |
| System3 Secure Install Credential Audit | 29640903648 | failure | `5f607c391728` | 2026-07-18T10:29:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29640903648 |
| System3 Experimental Solution Planner | 29640903620 | failure | `5f607c391728` | 2026-07-18T10:28:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29640903620 |
| Dashboard Visual Loading Postflight | 29640893239 | failure | `30fb51ebef9b` | 2026-07-18T10:28:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29640893239 |
| Dashboard Visual Proof Strict Gate | 29640893198 | failure | `30fb51ebef9b` | 2026-07-18T10:28:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29640893198 |
| Dashboard Visible Proof Current | 29640211220 | failure | `03171de0ed24` | 2026-07-18T10:15:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29640211220 |
| Dashboard Visible Auth-Resilient Proof | 29639824503 | failure | `0ba3d92076b9` | 2026-07-18T10:08:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29639824503 |
| System3 Windows Self-Hosted Full Proof | 29639745143 | failure | `a06f6f69e7a7` | 2026-07-18T09:54:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29639745143 |
| Dashboard Visible Proof Warmed | 29639826131 | failure | `ee39531697c7` | 2026-07-18T09:50:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29639826131 |
| System3 Backend Live Simulation Proof | 29639797957 | failure | `0ba3d92076b9` | 2026-07-18T09:49:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29639797957 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29640893217 | in_progress | 2026-07-18T10:28:54Z |
| Dashboard Shell Diagnostic | 29640893207 | in_progress | 2026-07-18T10:28:21Z |
| Dashboard Visible Issue Tracker | 29640603343 | in_progress | 2026-07-18T10:28:18Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 502 | HTTP status 502 | `none` |
| `/ui/` | 502 | HTTP status 502 | `none` |
| `/api/health` | 502 | HTTP status 502 | `none` |
| `/api/state` | 502 | HTTP status 502 | `none` |
| `/api/deploy/info` | 502 | HTTP status 502 | `none` |
| `/api/broker/diagnose` | 502 | HTTP status 502 | `none` |
| `/api/broker/funds` | 502 | HTTP status 502 | `none` |
| `/api/broker/holdings` | 502 | HTTP status 502 | `none` |
| `/api/broker/positions/live` | 502 | HTTP status 502 | `none` |
| `/api/scanner/top_contract_gainers` | 502 | HTTP status 502 | `none` |
| `/api/paper` | 502 | HTTP status 502 | `none` |
| `/api/ml/performance` | 502 | HTTP status 502 | `none` |
