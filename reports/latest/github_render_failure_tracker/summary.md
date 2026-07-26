# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T20:21:57.681451Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `5`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30218682880 conclusion=failure commit=4db99f038402
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30218759072 conclusion=failure commit=9b7d52c70a57
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30218580459 conclusion=failure commit=4db99f038402
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30218539646 conclusion=failure commit=4db99f038402
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30218344564 conclusion=failure commit=4db99f038402
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30218053923 conclusion=failure commit=adb2bfdc630b
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30217971936 conclusion=failure commit=9fe7aac93298
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30217964701 conclusion=failure commit=c22d356e0a92
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30217971901 conclusion=failure commit=9fe7aac93298
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30217971945 conclusion=failure commit=9fe7aac93298
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30217971915 conclusion=failure commit=9fe7aac93298
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30217942894 conclusion=failure commit=6da903d774a7
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
| System3 Safe Repair Runner | 30218682880 | failure | `4db99f038402` | 2026-07-26T20:20:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30218682880 |
| .github/workflows/options-ml-training-proof.yml | 30218759072 | failure | `9b7d52c70a57` | 2026-07-26T20:20:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30218759072 |
| Dashboard Visual Proof Strict Gate | 30218580459 | failure | `4db99f038402` | 2026-07-26T20:15:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30218580459 |
| Dashboard Visible Auth-Resilient Proof | 30218539646 | failure | `4db99f038402` | 2026-07-26T20:15:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30218539646 |
| Dashboard Visible Settle Proof | 30218344564 | failure | `4db99f038402` | 2026-07-26T20:08:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30218344564 |
| Dashboard Visible Proof Current | 30218053923 | failure | `adb2bfdc630b` | 2026-07-26T20:02:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30218053923 |
| Dashboard Shell Diagnostic | 30217971936 | failure | `9fe7aac93298` | 2026-07-26T19:59:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30217971936 |
| Dashboard Visible Issue Tracker | 30217964701 | failure | `c22d356e0a92` | 2026-07-26T19:58:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30217964701 |
| System3 Secure Install Credential Audit | 30217971901 | failure | `9fe7aac93298` | 2026-07-26T19:58:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30217971901 |
| Dashboard Visual Loading Postflight | 30217971945 | failure | `9fe7aac93298` | 2026-07-26T19:58:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30217971945 |
| System3 Experimental Solution Planner | 30217971915 | failure | `9fe7aac93298` | 2026-07-26T19:58:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30217971915 |
| System3 Autopilot Proof Board | 30217942894 | failure | `6da903d774a7` | 2026-07-26T19:58:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30217942894 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Options Big-Data Full History | 30218760386 | in_progress | 2026-07-26T20:20:47Z |
| System3 Full Non-Live Proof | 30218760369 | in_progress | 2026-07-26T20:20:38Z |
| Genesis System3 Global Safety CI | 30218760377 | queued | 2026-07-26T20:20:28Z |
| Options Big-Data Research | 30218760371 | queued | 2026-07-26T20:20:27Z |
| System3 Windows Self-Hosted Full Proof | 30218362360 | queued | 2026-07-26T20:08:58Z |

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
