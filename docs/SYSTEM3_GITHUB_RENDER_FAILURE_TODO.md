# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-19T18:19:02.135177Z`
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

- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29698483205 conclusion=failure commit=7ae7e37fcc66
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29698483208 conclusion=failure commit=7ae7e37fcc66
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29698483185 conclusion=failure commit=7ae7e37fcc66
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29698483194 conclusion=failure commit=7ae7e37fcc66
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29698049105 conclusion=failure commit=a67bad69e67b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29698046727 conclusion=failure commit=a67bad69e67b
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29697799307 conclusion=failure commit=5619f137007c
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29698147274 conclusion=failure commit=3ec7dfee72e3
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
| System3 Secure Install Credential Audit | 29698483205 | failure | `7ae7e37fcc66` | 2026-07-19T18:18:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29698483205 |
| Dashboard Visual Loading Postflight | 29698483208 | failure | `7ae7e37fcc66` | 2026-07-19T18:18:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29698483208 |
| Dashboard Visual Proof Strict Gate | 29698483185 | failure | `7ae7e37fcc66` | 2026-07-19T18:18:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29698483185 |
| System3 Experimental Solution Planner | 29698483194 | failure | `7ae7e37fcc66` | 2026-07-19T18:18:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29698483194 |
| System3 Windows Self-Hosted Full Proof | 29698049105 | failure | `a67bad69e67b` | 2026-07-19T18:11:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29698049105 |
| Dashboard Visible Settle Proof | 29698046727 | failure | `a67bad69e67b` | 2026-07-19T18:10:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29698046727 |
| Dashboard Visible Proof Current | 29697799307 | failure | `5619f137007c` | 2026-07-19T18:08:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29697799307 |
| System3 Autopilot Proof Board | 29698147274 | failure | `3ec7dfee72e3` | 2026-07-19T18:07:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29698147274 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29698483251 | queued | 2026-07-19T18:19:00Z |
| Dashboard Shell Diagnostic | 29698483232 | in_progress | 2026-07-19T18:18:29Z |
| Dashboard Visible Issue Tracker | 29698168853 | in_progress | 2026-07-19T18:18:27Z |
| Dashboard Visible Auth-Resilient Proof | 29698126786 | in_progress | 2026-07-19T18:06:26Z |

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
