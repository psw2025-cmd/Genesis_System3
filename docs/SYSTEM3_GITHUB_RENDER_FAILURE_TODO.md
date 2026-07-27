# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-27T22:23:29.907411Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `14`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `26`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30310338607 conclusion=failure commit=c882f2dd300d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30309811300 conclusion=failure commit=c882f2dd300d
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30309850664 conclusion=failure commit=c882f2dd300d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30309583007 conclusion=failure commit=c882f2dd300d
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30308922276 conclusion=failure commit=7a1aab3d0ef4
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30308882557 conclusion=failure commit=256903d599ef
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30308922283 conclusion=failure commit=7a1aab3d0ef4
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30308899855 conclusion=failure commit=f574d572d682
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30308922253 conclusion=failure commit=7a1aab3d0ef4
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30308922295 conclusion=failure commit=7a1aab3d0ef4
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30308846753 conclusion=failure commit=256903d599ef
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30308028263 conclusion=failure commit=94635ae11a02
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30307954018 conclusion=failure commit=94635ae11a02
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30307822508 conclusion=failure commit=6f7088f5adab
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
| System3 Safe Repair Runner | 30310338607 | failure | `c882f2dd300d` | 2026-07-27T22:22:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30310338607 |
| Dashboard Visible Auth-Resilient Proof | 30309811300 | failure | `c882f2dd300d` | 2026-07-27T22:12:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30309811300 |
| Dashboard Visual Proof Strict Gate | 30309850664 | failure | `c882f2dd300d` | 2026-07-27T22:12:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30309850664 |
| Dashboard Visible Settle Proof | 30309583007 | failure | `c882f2dd300d` | 2026-07-27T22:08:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30309583007 |
| Dashboard Shell Diagnostic | 30308922276 | failure | `7a1aab3d0ef4` | 2026-07-27T21:59:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30308922276 |
| Dashboard Visible Issue Tracker | 30308882557 | failure | `256903d599ef` | 2026-07-27T21:58:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30308882557 |
| System3 Secure Install Credential Audit | 30308922283 | failure | `7a1aab3d0ef4` | 2026-07-27T21:57:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30308922283 |
| Dashboard Visible Proof Current | 30308899855 | failure | `f574d572d682` | 2026-07-27T21:57:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30308899855 |
| System3 Experimental Solution Planner | 30308922253 | failure | `7a1aab3d0ef4` | 2026-07-27T21:57:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30308922253 |
| Dashboard Visual Loading Postflight | 30308922295 | failure | `7a1aab3d0ef4` | 2026-07-27T21:57:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30308922295 |
| System3 Autopilot Proof Board | 30308846753 | failure | `256903d599ef` | 2026-07-27T21:57:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30308846753 |
| Dashboard Visible Proof Warmed | 30308028263 | failure | `94635ae11a02` | 2026-07-27T21:44:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30308028263 |
| System3 Backend Live Simulation Proof | 30307954018 | failure | `94635ae11a02` | 2026-07-27T21:42:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30307954018 |
| System3 Render Worker Preflight | 30307822508 | failure | `6f7088f5adab` | 2026-07-27T21:40:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30307822508 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Windows Self-Hosted Full Proof | 30309731925 | in_progress | 2026-07-27T22:10:22Z |

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
