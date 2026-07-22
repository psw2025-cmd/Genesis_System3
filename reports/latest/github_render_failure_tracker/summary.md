# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-22T09:49:31.029468Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `5`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29908923814 conclusion=failure commit=aab7ca4e3d20
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29909016278 conclusion=failure commit=8bf5e32336bc
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29908966540 conclusion=failure commit=caf2257568e7
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29908966483 conclusion=failure commit=caf2257568e7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29908924053 conclusion=failure commit=aab7ca4e3d20
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29908923762 conclusion=failure commit=aab7ca4e3d20
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=29908280422 conclusion=failure commit=3c69208f6795
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
| Dashboard Shell Diagnostic | 29908923814 | failure | `aab7ca4e3d20` | 2026-07-22T09:43:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29908923814 |
| System3 Experimental Solution Planner | 29909016278 | failure | `8bf5e32336bc` | 2026-07-22T09:42:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29909016278 |
| System3 Autopilot Proof Board | 29908966540 | failure | `caf2257568e7` | 2026-07-22T09:42:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29908966540 |
| System3 Secure Install Credential Audit | 29908966483 | failure | `caf2257568e7` | 2026-07-22T09:41:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29908966483 |
| Dashboard Visual Loading Postflight | 29908924053 | failure | `aab7ca4e3d20` | 2026-07-22T09:40:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29908924053 |
| Dashboard Visual Proof Strict Gate | 29908923762 | failure | `aab7ca4e3d20` | 2026-07-22T09:40:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29908923762 |
| System3 Broker Chain Semantic Gate | 29908280422 | failure | `3c69208f6795` | 2026-07-22T09:31:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29908280422 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 29909401177 | in_progress | 2026-07-22T09:48:04Z |
| System3 Safe Repair Runner | 29909254532 | in_progress | 2026-07-22T09:46:23Z |
| Permanent Repo Render Safety | 29909271016 | in_progress | 2026-07-22T09:46:04Z |
| Dashboard Visible Issue Tracker | 29908943635 | in_progress | 2026-07-22T09:44:27Z |
| System3 Full Auto Truth | 29907595289 | in_progress | 2026-07-22T09:20:54Z |

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
