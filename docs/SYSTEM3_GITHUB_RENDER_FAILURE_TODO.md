# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T13:33:25.523978Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29923305237 conclusion=failure commit=bf10ba69e1d5
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29923337686 conclusion=failure commit=91437325dd1c
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29923391040 conclusion=failure commit=4232f381a91d
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29923332265 conclusion=failure commit=91437325dd1c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29923305155 conclusion=failure commit=bf10ba69e1d5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29923305392 conclusion=failure commit=bf10ba69e1d5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29921124717 conclusion=failure commit=1153dc3c5e61
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29921296190 conclusion=failure commit=1153dc3c5e61
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29921211015 conclusion=failure commit=1153dc3c5e61
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
| Dashboard Shell Diagnostic | 29923305237 | failure | `bf10ba69e1d5` | 2026-07-22T13:21:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29923305237 |
| System3 Autopilot Proof Board | 29923337686 | failure | `91437325dd1c` | 2026-07-22T13:19:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29923337686 |
| System3 Experimental Solution Planner | 29923391040 | failure | `4232f381a91d` | 2026-07-22T13:19:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29923391040 |
| System3 Secure Install Credential Audit | 29923332265 | failure | `91437325dd1c` | 2026-07-22T13:19:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29923332265 |
| Dashboard Visual Loading Postflight | 29923305155 | failure | `bf10ba69e1d5` | 2026-07-22T13:18:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29923305155 |
| Dashboard Visual Proof Strict Gate | 29923305392 | failure | `bf10ba69e1d5` | 2026-07-22T13:18:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29923305392 |
| Dashboard Visible Auth-Resilient Proof | 29921124717 | failure | `1153dc3c5e61` | 2026-07-22T13:06:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29921124717 |
| Dashboard Visible Proof Warmed | 29921296190 | failure | `1153dc3c5e61` | 2026-07-22T12:51:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29921296190 |
| System3 Backend Live Simulation Proof | 29921211015 | failure | `1153dc3c5e61` | 2026-07-22T12:49:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29921211015 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29924162765 | in_progress | 2026-07-22T13:30:10Z |
| Dashboard Visible Issue Tracker | 29923320329 | in_progress | 2026-07-22T13:26:27Z |

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
