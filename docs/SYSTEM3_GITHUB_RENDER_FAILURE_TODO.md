# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-27T16:42:59.178799Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `13`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `25`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30285720743 conclusion=failure commit=65838d491d6d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30285351597 conclusion=failure commit=65838d491d6d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30285153605 conclusion=failure commit=65838d491d6d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30285017112 conclusion=failure commit=5afb45e4069e
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30285017083 conclusion=failure commit=5afb45e4069e
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30284894826 conclusion=failure commit=930e5ff2f471
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30284894728 conclusion=failure commit=930e5ff2f471
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30284894702 conclusion=failure commit=930e5ff2f471
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30284894891 conclusion=failure commit=930e5ff2f471
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30284835176 conclusion=failure commit=7ff73b26ec19
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30284597251 conclusion=failure commit=b5104065927b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30283439671 conclusion=failure commit=fdb220322700
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30283053978 conclusion=failure commit=b0c3214c87df
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
| System3 Safe Repair Runner | 30285720743 | failure | `65838d491d6d` | 2026-07-27T16:42:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30285720743 |
| Dashboard Visible Auth-Resilient Proof | 30285351597 | failure | `65838d491d6d` | 2026-07-27T16:36:08Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30285351597 |
| Dashboard Visible Settle Proof | 30285153605 | failure | `65838d491d6d` | 2026-07-27T16:32:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30285153605 |
| Dashboard Visible Issue Tracker | 30285017112 | failure | `5afb45e4069e` | 2026-07-27T16:31:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30285017112 |
| System3 Experimental Solution Planner | 30285017083 | failure | `5afb45e4069e` | 2026-07-27T16:30:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30285017083 |
| Dashboard Shell Diagnostic | 30284894826 | failure | `930e5ff2f471` | 2026-07-27T16:30:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30284894826 |
| System3 Secure Install Credential Audit | 30284894728 | failure | `930e5ff2f471` | 2026-07-27T16:29:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30284894728 |
| Dashboard Visual Proof Strict Gate | 30284894702 | failure | `930e5ff2f471` | 2026-07-27T16:29:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30284894702 |
| Dashboard Visual Loading Postflight | 30284894891 | failure | `930e5ff2f471` | 2026-07-27T16:29:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30284894891 |
| System3 Autopilot Proof Board | 30284835176 | failure | `7ff73b26ec19` | 2026-07-27T16:29:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30284835176 |
| Dashboard Visible Proof Current | 30284597251 | failure | `b5104065927b` | 2026-07-27T16:25:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30284597251 |
| Dashboard Visible Proof Warmed | 30283439671 | failure | `fdb220322700` | 2026-07-27T16:10:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30283439671 |
| Dashboard Deploy Provenance Gate | 30283053978 | failure | `b0c3214c87df` | 2026-07-27T16:05:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30283053978 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Windows Self-Hosted Full Proof | 30285190639 | in_progress | 2026-07-27T16:32:53Z |

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
