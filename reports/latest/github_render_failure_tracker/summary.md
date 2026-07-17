# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-17T20:20:27.897067Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `10`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `22`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29610057739 conclusion=failure commit=c21bfbb44d76
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29610255351 conclusion=failure commit=582de456603b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29610029915 conclusion=failure commit=c21bfbb44d76
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29610351440 conclusion=failure commit=4dcb80536943
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29610284610 conclusion=failure commit=a056dd1bdfd0
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29610229210 conclusion=failure commit=fc2ed06ad7f6
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29610255254 conclusion=failure commit=582de456603b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29610255248 conclusion=failure commit=582de456603b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29609509450 conclusion=failure commit=f2ed64de20b7
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=29610186358 conclusion=failure commit=9b238dc465a5
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
| System3 Windows Self-Hosted Full Proof | 29610057739 | failure | `c21bfbb44d76` | 2026-07-17T20:14:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29610057739 |
| Dashboard Shell Diagnostic | 29610255351 | failure | `582de456603b` | 2026-07-17T20:14:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29610255351 |
| Dashboard Visible Settle Proof | 29610029915 | failure | `c21bfbb44d76` | 2026-07-17T20:13:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29610029915 |
| Dashboard Visual Proof Strict Gate | 29610351440 | failure | `4dcb80536943` | 2026-07-17T20:12:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29610351440 |
| System3 Experimental Solution Planner | 29610284610 | failure | `a056dd1bdfd0` | 2026-07-17T20:11:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29610284610 |
| System3 Autopilot Proof Board | 29610229210 | failure | `fc2ed06ad7f6` | 2026-07-17T20:11:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29610229210 |
| System3 Secure Install Credential Audit | 29610255254 | failure | `582de456603b` | 2026-07-17T20:11:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29610255254 |
| Dashboard Visual Loading Postflight | 29610255248 | failure | `582de456603b` | 2026-07-17T20:10:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29610255248 |
| Dashboard Visible Proof Current | 29609509450 | failure | `f2ed64de20b7` | 2026-07-17T20:10:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29609509450 |
| System3 Workflow Failure Tracker | 29610186358 | failure | `9b238dc465a5` | 2026-07-17T20:09:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29610186358 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29610641082 | in_progress | 2026-07-17T20:17:46Z |
| Dashboard Visible Auth-Resilient Proof | 29610298393 | in_progress | 2026-07-17T20:11:36Z |
| Dashboard Visible Issue Tracker | 29610284626 | pending | 2026-07-17T20:11:19Z |

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
