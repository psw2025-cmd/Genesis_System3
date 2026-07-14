# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-14T20:26:28.983660Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `6`
Render failed endpoints: `10`
TODO count: `20`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=29365391150 conclusion=failure commit=4459f6059888
- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=29365391065 conclusion=failure commit=4459f6059888
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=29365389930 conclusion=failure commit=4459f6059888
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29363793049 conclusion=failure commit=9314339599e8
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29363861736 conclusion=failure commit=3d604b5c5f59
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29363862027 conclusion=failure commit=3d604b5c5f59
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29363861310 conclusion=failure commit=3d604b5c5f59
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=29363044075 conclusion=failure commit=6bf6fbd3478b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29363281686 conclusion=failure commit=59f8725a4108
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29363229376 conclusion=failure commit=59f8725a4108
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
| Permanent Repo Render Safety | 29365391150 | failure | `4459f6059888` | 2026-07-14T20:24:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29365391150 |
| Genesis System3 Global Safety CI | 29365391065 | failure | `4459f6059888` | 2026-07-14T20:22:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29365391065 |
| .github/workflows/options-ml-training-proof.yml | 29365389930 | failure | `4459f6059888` | 2026-07-14T20:21:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29365389930 |
| Dashboard Visible Issue Tracker | 29363793049 | failure | `9314339599e8` | 2026-07-14T20:02:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29363793049 |
| Dashboard Shell Diagnostic | 29363861736 | failure | `3d604b5c5f59` | 2026-07-14T19:59:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29363861736 |
| Dashboard Visual Proof Strict Gate | 29363862027 | failure | `3d604b5c5f59` | 2026-07-14T19:58:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29363862027 |
| Dashboard Visual Loading Postflight | 29363861310 | failure | `3d604b5c5f59` | 2026-07-14T19:58:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29363861310 |
| Dashboard Visual Production Proof | 29363044075 | failure | `6bf6fbd3478b` | 2026-07-14T19:55:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29363044075 |
| Dashboard Visible Proof Warmed | 29363281686 | failure | `59f8725a4108` | 2026-07-14T19:51:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29363281686 |
| System3 Backend Live Simulation Proof | 29363229376 | failure | `59f8725a4108` | 2026-07-14T19:48:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29363229376 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 1000 Point TODO Status Updater | 29365705688 | queued | 2026-07-14T20:26:28Z |
| System3 Secure Install Credential Audit | 29365705621 | queued | 2026-07-14T20:26:28Z |
| System3 Autopilot Proof Board | 29365705598 | queued | 2026-07-14T20:26:28Z |
| System3 Experimental Solution Planner | 29365705589 | queued | 2026-07-14T20:26:28Z |
| System3 Safe Repair Runner | 29365450311 | in_progress | 2026-07-14T20:22:27Z |
| System3 Windows Self-Hosted Full Proof | 29365391169 | in_progress | 2026-07-14T20:22:13Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
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
