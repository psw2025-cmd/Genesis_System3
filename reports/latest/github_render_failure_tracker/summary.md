# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-21T07:48:42.164580Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29811333396 conclusion=failure commit=dabdd4fd38ad
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29811360426 conclusion=failure commit=22682b24f389
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29811402300 conclusion=failure commit=c6d872c0f1d6
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29811354868 conclusion=failure commit=22682b24f389
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29811333646 conclusion=failure commit=dabdd4fd38ad
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29811333413 conclusion=failure commit=dabdd4fd38ad
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=29810814168 conclusion=failure commit=dbf159e0c500
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
| Dashboard Shell Diagnostic | 29811333396 | failure | `dabdd4fd38ad` | 2026-07-21T07:43:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29811333396 |
| System3 Autopilot Proof Board | 29811360426 | failure | `22682b24f389` | 2026-07-21T07:42:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29811360426 |
| System3 Experimental Solution Planner | 29811402300 | failure | `c6d872c0f1d6` | 2026-07-21T07:41:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29811402300 |
| System3 Secure Install Credential Audit | 29811354868 | failure | `22682b24f389` | 2026-07-21T07:41:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29811354868 |
| Dashboard Visual Proof Strict Gate | 29811333646 | failure | `dabdd4fd38ad` | 2026-07-21T07:40:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29811333646 |
| Dashboard Visual Loading Postflight | 29811333413 | failure | `dabdd4fd38ad` | 2026-07-21T07:40:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29811333413 |
| System3 Broker Chain Semantic Gate | 29810814168 | failure | `dbf159e0c500` | 2026-07-21T07:32:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29810814168 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Issue Tracker | 29811366977 | in_progress | 2026-07-21T07:47:41Z |
| System3 Latest Truth Publish | 29811749745 | in_progress | 2026-07-21T07:47:19Z |
| System3 Safe Repair Runner | 29811703908 | in_progress | 2026-07-21T07:47:07Z |
| Permanent Repo Render Safety | 29811654165 | in_progress | 2026-07-21T07:45:46Z |

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
