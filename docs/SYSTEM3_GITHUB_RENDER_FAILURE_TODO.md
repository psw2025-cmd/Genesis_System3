# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T09:35:05.674877Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `8`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `12`
TODO count: `20`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29681703325 conclusion=failure commit=12ad5b0eaef9
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29681716508 conclusion=failure commit=05a93e5c45a7
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29681734410 conclusion=failure commit=b15f7b2874e8
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29681716459 conclusion=failure commit=05a93e5c45a7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29681703318 conclusion=failure commit=12ad5b0eaef9
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29681703333 conclusion=failure commit=12ad5b0eaef9
- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=29681579289 conclusion=failure commit=d5aa63885894
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=29681578851 conclusion=failure commit=d5aa63885894
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
| Dashboard Shell Diagnostic | 29681703325 | failure | `12ad5b0eaef9` | 2026-07-19T09:33:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29681703325 |
| System3 Autopilot Proof Board | 29681716508 | failure | `05a93e5c45a7` | 2026-07-19T09:32:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29681716508 |
| System3 Experimental Solution Planner | 29681734410 | failure | `b15f7b2874e8` | 2026-07-19T09:31:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29681734410 |
| System3 Secure Install Credential Audit | 29681716459 | failure | `05a93e5c45a7` | 2026-07-19T09:31:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29681716459 |
| Dashboard Visual Proof Strict Gate | 29681703318 | failure | `12ad5b0eaef9` | 2026-07-19T09:30:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29681703318 |
| Dashboard Visual Loading Postflight | 29681703333 | failure | `12ad5b0eaef9` | 2026-07-19T09:30:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29681703333 |
| Genesis System3 Global Safety CI | 29681579289 | failure | `d5aa63885894` | 2026-07-19T09:27:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29681579289 |
| .github/workflows/options-ml-training-proof.yml | 29681578851 | failure | `d5aa63885894` | 2026-07-19T09:26:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29681578851 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29681751245 | in_progress | 2026-07-19T09:32:27Z |
| Dashboard Visible Issue Tracker | 29681703220 | pending | 2026-07-19T09:30:38Z |
| Cloud Runtime Check | 29681579298 | in_progress | 2026-07-19T09:26:31Z |
| Permanent Repo Render Safety | 29681579285 | in_progress | 2026-07-19T09:26:31Z |

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
