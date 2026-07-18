# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T00:28:28.400116Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `11`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=29622703157 conclusion=failure commit=4c0c1c3bb8fd
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=29622345696 conclusion=failure commit=5305e9cb9b18
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29622485261 conclusion=failure commit=f459fdf86b7f
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29622460524 conclusion=failure commit=77bed56de9a5
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29622488681 conclusion=failure commit=8660bd947c30
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29622485231 conclusion=failure commit=f459fdf86b7f
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29622252385 conclusion=failure commit=9c4ee8e5ea79
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29622485221 conclusion=failure commit=f459fdf86b7f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29622485215 conclusion=failure commit=f459fdf86b7f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29622219754 conclusion=failure commit=84f243901ee0
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29621881813 conclusion=failure commit=44b6bc4dfa4b
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
| System3 Safe Repair Runner | 29622703157 | failure | `4c0c1c3bb8fd` | 2026-07-18T00:25:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29622703157 |
| Dashboard Visible Auth-Resilient Proof | 29622345696 | failure | `5305e9cb9b18` | 2026-07-18T00:25:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29622345696 |
| Dashboard Shell Diagnostic | 29622485261 | failure | `f459fdf86b7f` | 2026-07-18T00:13:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29622485261 |
| System3 Autopilot Proof Board | 29622460524 | failure | `77bed56de9a5` | 2026-07-18T00:10:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29622460524 |
| System3 Experimental Solution Planner | 29622488681 | failure | `8660bd947c30` | 2026-07-18T00:10:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29622488681 |
| System3 Secure Install Credential Audit | 29622485231 | failure | `f459fdf86b7f` | 2026-07-18T00:10:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29622485231 |
| System3 Windows Self-Hosted Full Proof | 29622252385 | failure | `9c4ee8e5ea79` | 2026-07-18T00:10:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29622252385 |
| Dashboard Visual Loading Postflight | 29622485221 | failure | `f459fdf86b7f` | 2026-07-18T00:10:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29622485221 |
| Dashboard Visual Proof Strict Gate | 29622485215 | failure | `f459fdf86b7f` | 2026-07-18T00:10:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29622485215 |
| Dashboard Visible Settle Proof | 29622219754 | failure | `84f243901ee0` | 2026-07-18T00:09:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29622219754 |
| Dashboard Visible Proof Current | 29621881813 | failure | `44b6bc4dfa4b` | 2026-07-18T00:07:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29621881813 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29622488655 | in_progress | 2026-07-18T00:20:58Z |

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
