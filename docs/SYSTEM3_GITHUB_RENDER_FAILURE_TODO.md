# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T22:20:49.702947Z`
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

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29782893323 conclusion=failure commit=663d24b30d47
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29782816274 conclusion=failure commit=96e6e35de391
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29782973299 conclusion=failure commit=3c4f4ca8b663
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29783010289 conclusion=failure commit=22872c0acbfc
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29783046394 conclusion=failure commit=985d519c76d1
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29783009767 conclusion=failure commit=22872c0acbfc
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29783000156 conclusion=failure commit=e0d7401a3cda
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29782973295 conclusion=failure commit=3c4f4ca8b663
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=29782968922 conclusion=failure commit=cfac5c1416fe
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29782163216 conclusion=failure commit=13c7fb3dbdf9
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
| System3 Windows Self-Hosted Full Proof | 29782893323 | failure | `663d24b30d47` | 2026-07-20T22:17:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29782893323 |
| Dashboard Visible Settle Proof | 29782816274 | failure | `96e6e35de391` | 2026-07-20T22:14:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29782816274 |
| Dashboard Shell Diagnostic | 29782973299 | failure | `3c4f4ca8b663` | 2026-07-20T22:13:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29782973299 |
| System3 Autopilot Proof Board | 29783010289 | failure | `22872c0acbfc` | 2026-07-20T22:12:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29783010289 |
| System3 Experimental Solution Planner | 29783046394 | failure | `985d519c76d1` | 2026-07-20T22:11:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29783046394 |
| System3 Secure Install Credential Audit | 29783009767 | failure | `22872c0acbfc` | 2026-07-20T22:11:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29783009767 |
| Dashboard Visual Proof Strict Gate | 29783000156 | failure | `e0d7401a3cda` | 2026-07-20T22:10:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29783000156 |
| Dashboard Visual Loading Postflight | 29782973295 | failure | `3c4f4ca8b663` | 2026-07-20T22:10:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29782973295 |
| System3 Workflow Failure Tracker | 29782968922 | failure | `cfac5c1416fe` | 2026-07-20T22:10:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29782968922 |
| Dashboard Visible Proof Current | 29782163216 | failure | `13c7fb3dbdf9` | 2026-07-20T22:09:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29782163216 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29783407727 | in_progress | 2026-07-20T22:18:12Z |
| Dashboard Visible Auth-Resilient Proof | 29783092076 | in_progress | 2026-07-20T22:12:22Z |
| Dashboard Visible Issue Tracker | 29783046374 | pending | 2026-07-20T22:11:36Z |

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
