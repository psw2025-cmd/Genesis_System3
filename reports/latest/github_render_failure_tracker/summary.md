# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T09:31:49.703287Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29639101036 conclusion=failure commit=5d858b24e5a5
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29639113661 conclusion=failure commit=cb0f33284f42
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29639133552 conclusion=failure commit=4d4b7734c2a2
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29639113693 conclusion=failure commit=cb0f33284f42
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29639101075 conclusion=failure commit=5d858b24e5a5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29639101029 conclusion=failure commit=5d858b24e5a5
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29638681069 conclusion=failure commit=a21c249a4ae6
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29638762782 conclusion=failure commit=a21c249a4ae6
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29638759391 conclusion=failure commit=a21c249a4ae6
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
| Dashboard Shell Diagnostic | 29639101036 | failure | `5d858b24e5a5` | 2026-07-18T09:27:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29639101036 |
| System3 Autopilot Proof Board | 29639113661 | failure | `cb0f33284f42` | 2026-07-18T09:25:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29639113661 |
| System3 Experimental Solution Planner | 29639133552 | failure | `4d4b7734c2a2` | 2026-07-18T09:25:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29639133552 |
| System3 Secure Install Credential Audit | 29639113693 | failure | `cb0f33284f42` | 2026-07-18T09:25:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29639113693 |
| Dashboard Visual Proof Strict Gate | 29639101075 | failure | `5d858b24e5a5` | 2026-07-18T09:24:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29639101075 |
| Dashboard Visual Loading Postflight | 29639101029 | failure | `5d858b24e5a5` | 2026-07-18T09:24:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29639101029 |
| Dashboard Visible Proof Current | 29638681069 | failure | `a21c249a4ae6` | 2026-07-18T09:21:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29638681069 |
| System3 Windows Self-Hosted Full Proof | 29638762782 | failure | `a21c249a4ae6` | 2026-07-18T09:18:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29638762782 |
| Dashboard Visible Settle Proof | 29638759391 | failure | `a21c249a4ae6` | 2026-07-18T09:18:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29638759391 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29639214607 | in_progress | 2026-07-18T09:29:05Z |
| Dashboard Visible Issue Tracker | 29639104754 | in_progress | 2026-07-18T09:25:46Z |
| Dashboard Visible Auth-Resilient Proof | 29638833675 | in_progress | 2026-07-18T09:14:37Z |

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
