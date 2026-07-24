# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-24T09:48:26.269446Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `13`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `25`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30083660770 conclusion=failure commit=2b1f6c046b04
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30082145804 conclusion=failure commit=32951b568efe
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30082863868 conclusion=failure commit=cf8b62649f4c
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30082863814 conclusion=failure commit=cf8b62649f4c
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30082863810 conclusion=failure commit=cf8b62649f4c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30082863890 conclusion=failure commit=cf8b62649f4c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30082863815 conclusion=failure commit=cf8b62649f4c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30082810371 conclusion=failure commit=4f1cefc764dd
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30082695361 conclusion=failure commit=1cb1d5065aa4
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30082188675 conclusion=failure commit=6f72249ce826
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30081556541 conclusion=failure commit=72beaa9a17ca
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30081472375 conclusion=failure commit=b46413bc2960
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30081418637 conclusion=failure commit=144fc3be7890
- [ ] Fix Render endpoint /: HTTP status 0 status=0
- [ ] Fix Render endpoint /ui/: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/health: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/paper: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Safe Repair Runner | 30083660770 | failure | `2b1f6c046b04` | 2026-07-24T09:46:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30083660770 |
| System3 Full Auto Truth | 30082145804 | failure | `32951b568efe` | 2026-07-24T09:44:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30082145804 |
| Dashboard Shell Diagnostic | 30082863868 | failure | `cf8b62649f4c` | 2026-07-24T09:32:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30082863868 |
| System3 Secure Install Credential Audit | 30082863814 | failure | `cf8b62649f4c` | 2026-07-24T09:31:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30082863814 |
| System3 Experimental Solution Planner | 30082863810 | failure | `cf8b62649f4c` | 2026-07-24T09:31:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30082863810 |
| Dashboard Visual Loading Postflight | 30082863890 | failure | `cf8b62649f4c` | 2026-07-24T09:31:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30082863890 |
| Dashboard Visual Proof Strict Gate | 30082863815 | failure | `cf8b62649f4c` | 2026-07-24T09:31:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30082863815 |
| Dashboard Visible Issue Tracker | 30082810371 | failure | `4f1cefc764dd` | 2026-07-24T09:31:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30082810371 |
| System3 Broker Chain Semantic Gate | 30082695361 | failure | `1cb1d5065aa4` | 2026-07-24T09:28:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30082695361 |
| System3 Autopilot Proof Board | 30082188675 | failure | `6f72249ce826` | 2026-07-24T09:21:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30082188675 |
| Dashboard Visible Proof Warmed | 30081556541 | failure | `72beaa9a17ca` | 2026-07-24T09:10:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30081556541 |
| System3 Backend Live Simulation Proof | 30081472375 | failure | `b46413bc2960` | 2026-07-24T09:08:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30081472375 |
| Dashboard Visible Auth-Resilient Proof | 30081418637 | failure | `144fc3be7890` | 2026-07-24T09:08:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30081418637 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30083809257 | in_progress | 2026-07-24T09:46:52Z |
| Permanent Repo Render Safety | 30083677400 | in_progress | 2026-07-24T09:44:40Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 0 | HTTP status 0 | `none` |
| `/ui/` | 0 | HTTP status 0 | `none` |
| `/api/health` | 0 | HTTP status 0 | `none` |
| `/api/state` | 0 | HTTP status 0 | `none` |
| `/api/deploy/info` | 0 | HTTP status 0 | `none` |
| `/api/broker/diagnose` | 0 | HTTP status 0 | `none` |
| `/api/broker/funds` | 0 | HTTP status 0 | `none` |
| `/api/broker/holdings` | 0 | HTTP status 0 | `none` |
| `/api/broker/positions/live` | 0 | HTTP status 0 | `none` |
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
| `/api/paper` | 0 | HTTP status 0 | `none` |
| `/api/ml/performance` | 0 | HTTP status 0 | `none` |
