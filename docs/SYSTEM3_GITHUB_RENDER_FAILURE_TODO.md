# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-15T05:01:03.498942Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `2`
TODO count: `14`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=29389880053 conclusion=failure commit=28724dfa1e49
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=29389876057 conclusion=failure commit=28724dfa1e49
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29389651186 conclusion=failure commit=092cb41daba3
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29389880028 conclusion=failure commit=28724dfa1e49
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29389880040 conclusion=failure commit=28724dfa1e49
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29389880020 conclusion=failure commit=28724dfa1e49
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29389880075 conclusion=failure commit=28724dfa1e49
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29389880033 conclusion=failure commit=28724dfa1e49
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29389514960 conclusion=failure commit=edf0ac5d7c65
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29389269131 conclusion=failure commit=00f9b131d5b5
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29389607635 conclusion=failure commit=887c934096e4
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=29389074867 conclusion=failure commit=5ee520c9ea24
- [ ] Fix Render endpoint /api/broker/diagnose: authentication error classification detected status=200
- [ ] Fix Render endpoint /api/broker/funds: authentication error classification detected status=200

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Safe Repair Runner | 29389880053 | failure | `28724dfa1e49` | 2026-07-15T04:58:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389880053 |
| System3 Market Session Proof Runner | 29389876057 | failure | `28724dfa1e49` | 2026-07-15T04:53:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389876057 |
| Dashboard Visible Issue Tracker | 29389651186 | failure | `092cb41daba3` | 2026-07-15T04:51:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389651186 |
| Dashboard Shell Diagnostic | 29389880028 | failure | `28724dfa1e49` | 2026-07-15T04:49:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389880028 |
| System3 Secure Install Credential Audit | 29389880040 | failure | `28724dfa1e49` | 2026-07-15T04:49:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389880040 |
| System3 Experimental Solution Planner | 29389880020 | failure | `28724dfa1e49` | 2026-07-15T04:49:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389880020 |
| Dashboard Visual Loading Postflight | 29389880075 | failure | `28724dfa1e49` | 2026-07-15T04:49:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389880075 |
| Dashboard Visual Proof Strict Gate | 29389880033 | failure | `28724dfa1e49` | 2026-07-15T04:49:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389880033 |
| System3 Windows Self-Hosted Full Proof | 29389514960 | failure | `edf0ac5d7c65` | 2026-07-15T04:46:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389514960 |
| Dashboard Visible Proof Current | 29389269131 | failure | `00f9b131d5b5` | 2026-07-15T04:45:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389269131 |
| System3 Autopilot Proof Board | 29389607635 | failure | `887c934096e4` | 2026-07-15T04:43:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389607635 |
| System3 Windows Self-Hosted Workflow Migration | 29389074867 | failure | `5ee520c9ea24` | 2026-07-15T04:31:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29389074867 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/broker/diagnose` | 200 | authentication error classification detected | `mentions_auth_error` |
| `/api/broker/funds` | 200 | authentication error classification detected | `mentions_auth_error` |
