# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T11:01:47.541358Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `5`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29735981001 conclusion=failure commit=c2b9c7e1ba29
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29735806454 conclusion=failure commit=922f1091a8ba
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29735823520 conclusion=failure commit=922f1091a8ba
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29735364928 conclusion=failure commit=fa85545680bc
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29736038703 conclusion=failure commit=796f60779f20
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29735947942 conclusion=failure commit=4d514042d9cf
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29735989963 conclusion=failure commit=6dfb2a0c3776
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29735980960 conclusion=failure commit=c2b9c7e1ba29
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29735980935 conclusion=failure commit=c2b9c7e1ba29
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
| Dashboard Shell Diagnostic | 29735981001 | failure | `c2b9c7e1ba29` | 2026-07-20T10:45:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29735981001 |
| Dashboard Visible Settle Proof | 29735806454 | failure | `922f1091a8ba` | 2026-07-20T10:45:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29735806454 |
| System3 Windows Self-Hosted Full Proof | 29735823520 | failure | `922f1091a8ba` | 2026-07-20T10:44:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29735823520 |
| Dashboard Visible Proof Current | 29735364928 | failure | `fa85545680bc` | 2026-07-20T10:43:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29735364928 |
| Dashboard Visual Proof Strict Gate | 29736038703 | failure | `796f60779f20` | 2026-07-20T10:43:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29736038703 |
| System3 Autopilot Proof Board | 29735947942 | failure | `4d514042d9cf` | 2026-07-20T10:43:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29735947942 |
| System3 Experimental Solution Planner | 29735989963 | failure | `6dfb2a0c3776` | 2026-07-20T10:42:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29735989963 |
| System3 Secure Install Credential Audit | 29735980960 | failure | `c2b9c7e1ba29` | 2026-07-20T10:42:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29735980960 |
| Dashboard Visual Loading Postflight | 29735980935 | failure | `c2b9c7e1ba29` | 2026-07-20T10:42:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29735980935 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 29736962205 | in_progress | 2026-07-20T10:59:52Z |
| Permanent Repo Render Safety | 29736872642 | in_progress | 2026-07-20T10:58:15Z |
| System3 Safe Repair Runner | 29736859174 | in_progress | 2026-07-20T10:58:00Z |
| Dashboard Visible Issue Tracker | 29735990001 | in_progress | 2026-07-20T10:53:16Z |
| Dashboard Visible Auth-Resilient Proof | 29736074322 | in_progress | 2026-07-20T10:44:12Z |

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
