# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-27T15:00:38.989632Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30277520780 conclusion=failure commit=e7e67283984e
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30276005516 conclusion=failure commit=bb9bad59c7ba
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30276362838 conclusion=failure commit=bb9bad59c7ba
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30276414239 conclusion=failure commit=bb9bad59c7ba
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30275959562 conclusion=failure commit=bb9bad59c7ba
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30275169154 conclusion=failure commit=e803281279c4
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30275153173 conclusion=failure commit=cdafd196eaed
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30275169373 conclusion=failure commit=e803281279c4
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30275169171 conclusion=failure commit=e803281279c4
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30275090534 conclusion=failure commit=a7bc5c042f5b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30275169378 conclusion=failure commit=e803281279c4
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30275084887 conclusion=failure commit=a7bc5c042f5b
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
| System3 Safe Repair Runner | 30277520780 | failure | `e7e67283984e` | 2026-07-27T14:59:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30277520780 |
| System3 Windows Self-Hosted Full Proof | 30276005516 | failure | `bb9bad59c7ba` | 2026-07-27T14:49:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30276005516 |
| Dashboard Visible Auth-Resilient Proof | 30276362838 | failure | `bb9bad59c7ba` | 2026-07-27T14:43:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30276362838 |
| Dashboard Visual Proof Strict Gate | 30276414239 | failure | `bb9bad59c7ba` | 2026-07-27T14:43:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30276414239 |
| Dashboard Visible Settle Proof | 30275959562 | failure | `bb9bad59c7ba` | 2026-07-27T14:37:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30275959562 |
| Dashboard Shell Diagnostic | 30275169154 | failure | `e803281279c4` | 2026-07-27T14:29:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30275169154 |
| Dashboard Visible Issue Tracker | 30275153173 | failure | `cdafd196eaed` | 2026-07-27T14:28:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30275153173 |
| System3 Secure Install Credential Audit | 30275169373 | failure | `e803281279c4` | 2026-07-27T14:27:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30275169373 |
| System3 Experimental Solution Planner | 30275169171 | failure | `e803281279c4` | 2026-07-27T14:27:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30275169171 |
| System3 Autopilot Proof Board | 30275090534 | failure | `a7bc5c042f5b` | 2026-07-27T14:27:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30275090534 |
| Dashboard Visual Loading Postflight | 30275169378 | failure | `e803281279c4` | 2026-07-27T14:27:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30275169378 |
| Dashboard Visible Proof Current | 30275084887 | failure | `a7bc5c042f5b` | 2026-07-27T14:27:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30275084887 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

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
