# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-15T06:46:29.575100Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `2`
TODO count: `12`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29394342902 conclusion=failure commit=c2f5b88f972c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29394294343 conclusion=failure commit=73c6bcf2e875
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29394080655 conclusion=failure commit=d5f2ddf9ff45
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29394545022 conclusion=failure commit=c2f5b88f972c
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29394566501 conclusion=failure commit=f31008e8f7ff
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29394596262 conclusion=failure commit=6a80219d6394
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29394561057 conclusion=failure commit=f31008e8f7ff
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29394545078 conclusion=failure commit=c2f5b88f972c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29394545073 conclusion=failure commit=c2f5b88f972c
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=29394196735 conclusion=failure commit=32a42f9033a2
- [ ] Fix Render endpoint /api/broker/diagnose: authentication error classification detected status=200
- [ ] Fix Render endpoint /api/broker/funds: authentication error classification detected status=200

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Windows Self-Hosted Full Proof | 29394342902 | failure | `c2f5b88f972c` | 2026-07-15T06:40:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29394342902 |
| Dashboard Visible Issue Tracker | 29394294343 | failure | `73c6bcf2e875` | 2026-07-15T06:39:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29394294343 |
| Dashboard Visible Proof Current | 29394080655 | failure | `d5f2ddf9ff45` | 2026-07-15T06:38:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29394080655 |
| Dashboard Shell Diagnostic | 29394545022 | failure | `c2f5b88f972c` | 2026-07-15T06:36:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29394545022 |
| System3 Autopilot Proof Board | 29394566501 | failure | `f31008e8f7ff` | 2026-07-15T06:34:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29394566501 |
| System3 Experimental Solution Planner | 29394596262 | failure | `6a80219d6394` | 2026-07-15T06:34:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29394596262 |
| System3 Secure Install Credential Audit | 29394561057 | failure | `f31008e8f7ff` | 2026-07-15T06:33:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29394561057 |
| Dashboard Visual Proof Strict Gate | 29394545078 | failure | `c2f5b88f972c` | 2026-07-15T06:33:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29394545078 |
| Dashboard Visual Loading Postflight | 29394545073 | failure | `c2f5b88f972c` | 2026-07-15T06:33:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29394545073 |
| System3 Broker Chain Semantic Gate | 29394196735 | failure | `32a42f9033a2` | 2026-07-15T06:26:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29394196735 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29394853748 | in_progress | 2026-07-15T06:40:09Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/broker/diagnose` | 200 | authentication error classification detected | `mentions_auth_error` |
| `/api/broker/funds` | 200 | authentication error classification detected | `mentions_auth_error` |
