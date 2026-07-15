# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-15T18:25:27.407804Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `8`
GitHub workflows currently queued/in progress: `7`
Render failed endpoints: `12`
TODO count: `20`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visual Settle Normalizer' run=29440452317 conclusion=failure commit=6df4492ad92c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29440449340 conclusion=failure commit=6df4492ad92c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29440449008 conclusion=failure commit=6df4492ad92c
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29439402537 conclusion=failure commit=1333cbc2588a
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29439304524 conclusion=failure commit=8f019bf524b9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29438906955 conclusion=failure commit=8f019bf524b9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=29437884010 conclusion=failure commit=f81287850213
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=29437815096 conclusion=failure commit=213479463cf6
- [ ] Fix Render endpoint /: HTTP status 503 status=503
- [ ] Fix Render endpoint /ui/: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/health: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/state: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/paper: HTTP status 503 status=503
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 503 status=503

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Visual Settle Normalizer | 29440452317 | failure | `6df4492ad92c` | 2026-07-15T18:25:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29440452317 |
| Dashboard Visual Proof Strict Gate | 29440449340 | failure | `6df4492ad92c` | 2026-07-15T18:25:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29440449340 |
| Dashboard Visual Loading Postflight | 29440449008 | failure | `6df4492ad92c` | 2026-07-15T18:25:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29440449008 |
| Dashboard Visible Settle Proof | 29439402537 | failure | `1333cbc2588a` | 2026-07-15T18:15:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29439402537 |
| System3 Windows Self-Hosted Full Proof | 29439304524 | failure | `8f019bf524b9` | 2026-07-15T18:13:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29439304524 |
| Dashboard Visible Proof Current | 29438906955 | failure | `8f019bf524b9` | 2026-07-15T18:08:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29438906955 |
| Dashboard Visible Proof Warmed | 29437884010 | failure | `f81287850213` | 2026-07-15T17:47:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29437884010 |
| System3 Backend Live Simulation Proof | 29437815096 | failure | `213479463cf6` | 2026-07-15T17:46:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29437815096 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Autopilot Proof Board | 29440477831 | queued | 2026-07-15T18:25:27Z |
| System3 Secure Install Credential Audit | 29440477826 | queued | 2026-07-15T18:25:27Z |
| System3 Experimental Solution Planner | 29440477804 | queued | 2026-07-15T18:25:27Z |
| Dashboard Shell Diagnostic | 29440449080 | in_progress | 2026-07-15T18:25:05Z |
| System3 Safe Repair Runner | 29440448957 | pending | 2026-07-15T18:25:02Z |
| Dashboard Visible Issue Tracker | 29439734502 | in_progress | 2026-07-15T18:25:00Z |
| Dashboard Visible Auth-Resilient Proof | 29439717708 | in_progress | 2026-07-15T18:14:14Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 503 | HTTP status 503 | `none` |
| `/ui/` | 503 | HTTP status 503 | `none` |
| `/api/health` | 503 | HTTP status 503 | `none` |
| `/api/state` | 503 | HTTP status 503 | `none` |
| `/api/deploy/info` | 503 | HTTP status 503 | `none` |
| `/api/broker/diagnose` | 503 | HTTP status 503 | `none` |
| `/api/broker/funds` | 503 | HTTP status 503 | `none` |
| `/api/broker/holdings` | 503 | HTTP status 503 | `none` |
| `/api/broker/positions/live` | 503 | HTTP status 503 | `none` |
| `/api/scanner/top_contract_gainers` | 503 | HTTP status 503 | `none` |
| `/api/paper` | 503 | HTTP status 503 | `none` |
| `/api/ml/performance` | 503 | HTTP status 503 | `none` |
