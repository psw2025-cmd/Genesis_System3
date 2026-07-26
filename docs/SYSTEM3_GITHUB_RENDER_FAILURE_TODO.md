# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T23:20:43.792175Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `6`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30224922928 conclusion=failure commit=2a21c2814e3c
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30224931518 conclusion=failure commit=36dbb854dfc9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30224609634 conclusion=failure commit=2a21c2814e3c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30224595708 conclusion=failure commit=2a21c2814e3c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30224495387 conclusion=failure commit=2a21c2814e3c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30224133800 conclusion=failure commit=3acb3fc58100
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30224031406 conclusion=failure commit=808724639188
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30224031411 conclusion=failure commit=808724639188
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30224031412 conclusion=failure commit=808724639188
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
| System3 Safe Repair Runner | 30224922928 | failure | `2a21c2814e3c` | 2026-07-26T23:19:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30224922928 |
| .github/workflows/options-ml-training-proof.yml | 30224931518 | failure | `36dbb854dfc9` | 2026-07-26T23:17:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30224931518 |
| Dashboard Visible Auth-Resilient Proof | 30224609634 | failure | `2a21c2814e3c` | 2026-07-26T23:09:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30224609634 |
| Dashboard Visual Proof Strict Gate | 30224595708 | failure | `2a21c2814e3c` | 2026-07-26T23:08:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30224595708 |
| Dashboard Visible Settle Proof | 30224495387 | failure | `2a21c2814e3c` | 2026-07-26T23:05:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30224495387 |
| Dashboard Visible Proof Current | 30224133800 | failure | `3acb3fc58100` | 2026-07-26T22:56:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30224133800 |
| System3 Secure Install Credential Audit | 30224031406 | failure | `808724639188` | 2026-07-26T22:53:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30224031406 |
| System3 Experimental Solution Planner | 30224031411 | failure | `808724639188` | 2026-07-26T22:53:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30224031411 |
| Dashboard Visual Loading Postflight | 30224031412 | failure | `808724639188` | 2026-07-26T22:53:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30224031412 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Options Big-Data Artifact Model | 30224933108 | in_progress | 2026-07-26T23:17:40Z |
| Options Big-Data Full History | 30224933124 | in_progress | 2026-07-26T23:17:38Z |
| Genesis System3 Global Safety CI | 30224933128 | queued | 2026-07-26T23:17:36Z |
| Options Big-Data Self-Hosted Model | 30224933112 | pending | 2026-07-26T23:17:36Z |
| Options Big-Data Research | 30224933113 | queued | 2026-07-26T23:17:35Z |
| System3 Windows Self-Hosted Full Proof | 30224506359 | queued | 2026-07-26T23:05:40Z |

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
