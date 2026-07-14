# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-14T22:21:55.732739Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `1`
TODO count: `7`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 1000 Point TODO Status Updater' run=29372717476 conclusion=failure commit=b05b9a518544
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29371868626 conclusion=failure commit=1ae1057f52d7
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29371859451 conclusion=failure commit=1ae1057f52d7
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29371981107 conclusion=failure commit=3f0aca9eeb7b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29372003880 conclusion=failure commit=cb8be7d4ee92
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29371980914 conclusion=failure commit=3f0aca9eeb7b
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 1000 Point TODO Status Updater | 29372717476 | failure | `b05b9a518544` | 2026-07-14T22:21:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29372717476 |
| System3 Windows Self-Hosted Full Proof | 29371868626 | failure | `1ae1057f52d7` | 2026-07-14T22:20:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29371868626 |
| Dashboard Visible Issue Tracker | 29371859451 | failure | `1ae1057f52d7` | 2026-07-14T22:11:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29371859451 |
| Dashboard Shell Diagnostic | 29371981107 | failure | `3f0aca9eeb7b` | 2026-07-14T22:11:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29371981107 |
| Dashboard Visual Proof Strict Gate | 29372003880 | failure | `cb8be7d4ee92` | 2026-07-14T22:08:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29372003880 |
| Dashboard Visual Loading Postflight | 29371980914 | failure | `3f0aca9eeb7b` | 2026-07-14T22:08:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29371980914 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Experimental Solution Planner | 29372734329 | in_progress | 2026-07-14T22:21:53Z |
| System3 Secure Install Credential Audit | 29372734352 | in_progress | 2026-07-14T22:21:52Z |
| System3 Autopilot Proof Board | 29372734219 | in_progress | 2026-07-14T22:21:52Z |
| System3 Safe Repair Runner | 29372524564 | in_progress | 2026-07-14T22:18:09Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
