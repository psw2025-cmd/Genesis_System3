# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-20T13:34:48.857244Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29746384730 conclusion=failure commit=fa9c5e8170fc
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29746071319 conclusion=failure commit=94716ee71532
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29746479864 conclusion=failure commit=727d2f2722bb
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29746420507 conclusion=failure commit=727f490bf9c3
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29746080790 conclusion=failure commit=94716ee71532
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29745629681 conclusion=failure commit=da386de74f53
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29746420685 conclusion=failure commit=727f490bf9c3
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29746384584 conclusion=failure commit=fa9c5e8170fc
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29746384691 conclusion=failure commit=fa9c5e8170fc
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=29746378200 conclusion=failure commit=fa9c5e8170fc
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
| Dashboard Shell Diagnostic | 29746384730 | failure | `fa9c5e8170fc` | 2026-07-20T13:31:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29746384730 |
| Dashboard Visible Settle Proof | 29746071319 | failure | `94716ee71532` | 2026-07-20T13:29:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29746071319 |
| System3 Experimental Solution Planner | 29746479864 | failure | `727d2f2722bb` | 2026-07-20T13:29:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29746479864 |
| System3 Autopilot Proof Board | 29746420507 | failure | `727f490bf9c3` | 2026-07-20T13:29:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29746420507 |
| System3 Windows Self-Hosted Full Proof | 29746080790 | failure | `94716ee71532` | 2026-07-20T13:29:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29746080790 |
| Dashboard Visible Proof Current | 29745629681 | failure | `da386de74f53` | 2026-07-20T13:29:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29745629681 |
| System3 Secure Install Credential Audit | 29746420685 | failure | `727f490bf9c3` | 2026-07-20T13:29:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29746420685 |
| Dashboard Visual Loading Postflight | 29746384584 | failure | `fa9c5e8170fc` | 2026-07-20T13:28:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29746384584 |
| Dashboard Visual Proof Strict Gate | 29746384691 | failure | `fa9c5e8170fc` | 2026-07-20T13:28:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29746384691 |
| System3 Workflow Failure Tracker | 29746378200 | failure | `fa9c5e8170fc` | 2026-07-20T13:28:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29746378200 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29746604420 | in_progress | 2026-07-20T13:32:01Z |
| Dashboard Visible Issue Tracker | 29746480079 | pending | 2026-07-20T13:29:44Z |
| Dashboard Visible Auth-Resilient Proof | 29746294779 | in_progress | 2026-07-20T13:27:04Z |

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
