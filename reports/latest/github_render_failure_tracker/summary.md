# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-14T12:28:44.303839Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `8`
GitHub workflows currently queued/in progress: `5`
Render failed endpoints: `8`
TODO count: `16`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29332596907 conclusion=failure commit=f1635ea481a7
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29332596840 conclusion=failure commit=f1635ea481a7
- [ ] Fix latest GitHub workflow 'System3 1000 Point TODO Status Updater' run=29332577563 conclusion=failure commit=448dcbc81951
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29332577679 conclusion=failure commit=448dcbc81951
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29332577659 conclusion=failure commit=448dcbc81951
- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=29332229612 conclusion=failure commit=5a61817d2a95
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=29332229647 conclusion=failure commit=5a61817d2a95
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=29332228784 conclusion=failure commit=5a61817d2a95
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
| System3 Secure Install Credential Audit | 29332596907 | failure | `f1635ea481a7` | 2026-07-14T12:28:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29332596907 |
| System3 Experimental Solution Planner | 29332596840 | failure | `f1635ea481a7` | 2026-07-14T12:28:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29332596840 |
| System3 1000 Point TODO Status Updater | 29332577563 | failure | `448dcbc81951` | 2026-07-14T12:28:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29332577563 |
| Dashboard Visual Proof Strict Gate | 29332577679 | failure | `448dcbc81951` | 2026-07-14T12:28:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29332577679 |
| Dashboard Visual Loading Postflight | 29332577659 | failure | `448dcbc81951` | 2026-07-14T12:28:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29332577659 |
| Genesis System3 Global Safety CI | 29332229612 | failure | `5a61817d2a95` | 2026-07-14T12:24:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29332229612 |
| Permanent Repo Render Safety | 29332229647 | failure | `5a61817d2a95` | 2026-07-14T12:22:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29332229647 |
| .github/workflows/options-ml-training-proof.yml | 29332228784 | failure | `5a61817d2a95` | 2026-07-14T12:22:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29332228784 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29332577597 | in_progress | 2026-07-14T12:28:30Z |
| System3 Autopilot Proof Board | 29332601759 | in_progress | 2026-07-14T12:28:19Z |
| Dashboard Shell Diagnostic | 29332577678 | in_progress | 2026-07-14T12:27:56Z |
| Dashboard Visible Issue Tracker | 29332424014 | in_progress | 2026-07-14T12:27:54Z |
| System3 Windows Self-Hosted Full Proof | 29332229636 | in_progress | 2026-07-14T12:24:22Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/deploy/info` | 502 | HTTP status 502 | `none` |
| `/api/broker/diagnose` | 502 | HTTP status 502 | `none` |
| `/api/broker/funds` | 502 | HTTP status 502 | `none` |
| `/api/broker/holdings` | 502 | HTTP status 502 | `none` |
| `/api/broker/positions/live` | 502 | HTTP status 502 | `none` |
| `/api/scanner/top_contract_gainers` | 502 | HTTP status 502 | `none` |
| `/api/paper` | 502 | HTTP status 502 | `none` |
| `/api/ml/performance` | 502 | HTTP status 502 | `none` |
