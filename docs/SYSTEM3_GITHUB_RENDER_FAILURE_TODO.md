# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T19:25:50.605753Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29700008847 conclusion=failure commit=e63c0fa19aac
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29700103900 conclusion=failure commit=0e194b990a98
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29699987549 conclusion=failure commit=bbc43087c7de
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29700119576 conclusion=failure commit=bce5a0fe836b
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29700103895 conclusion=failure commit=0e194b990a98
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29700079260 conclusion=failure commit=6db78c233730
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29700105638 conclusion=failure commit=0e194b990a98
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29700103875 conclusion=failure commit=0e194b990a98
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29699629314 conclusion=failure commit=525e9b82efe9
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
| System3 Windows Self-Hosted Full Proof | 29700008847 | failure | `e63c0fa19aac` | 2026-07-19T19:14:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29700008847 |
| Dashboard Shell Diagnostic | 29700103900 | failure | `0e194b990a98` | 2026-07-19T19:14:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29700103900 |
| Dashboard Visible Settle Proof | 29699987549 | failure | `bbc43087c7de` | 2026-07-19T19:13:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29699987549 |
| Dashboard Visual Proof Strict Gate | 29700119576 | failure | `bce5a0fe836b` | 2026-07-19T19:11:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29700119576 |
| System3 Secure Install Credential Audit | 29700103895 | failure | `0e194b990a98` | 2026-07-19T19:11:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29700103895 |
| System3 Autopilot Proof Board | 29700079260 | failure | `6db78c233730` | 2026-07-19T19:10:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29700079260 |
| System3 Experimental Solution Planner | 29700105638 | failure | `0e194b990a98` | 2026-07-19T19:10:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29700105638 |
| Dashboard Visual Loading Postflight | 29700103875 | failure | `0e194b990a98` | 2026-07-19T19:10:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29700103875 |
| Dashboard Visible Proof Current | 29699629314 | failure | `525e9b82efe9` | 2026-07-19T19:09:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29699629314 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Workflow Failure Tracker | 29700573648 | queued | 2026-07-19T19:25:49Z |
| System3 Safe Repair Runner | 29700480252 | in_progress | 2026-07-19T19:23:08Z |
| Dashboard Visible Issue Tracker | 29700105641 | in_progress | 2026-07-19T19:21:29Z |
| Dashboard Visible Auth-Resilient Proof | 29700134132 | in_progress | 2026-07-19T19:11:47Z |

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
