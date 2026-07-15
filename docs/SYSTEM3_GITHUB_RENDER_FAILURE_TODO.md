# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-15T21:21:34.415412Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29450729350 conclusion=failure commit=36e6bbd39cf2
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29450763270 conclusion=failure commit=36e6bbd39cf2
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29450865323 conclusion=failure commit=f10af027c5ca
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29450937574 conclusion=failure commit=9fc9764b7678
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29450890259 conclusion=failure commit=ccfcc2005115
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29450923348 conclusion=failure commit=b064f7d144bf
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29450890567 conclusion=failure commit=ccfcc2005115
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29450865288 conclusion=failure commit=f10af027c5ca
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29450151147 conclusion=failure commit=601ea5c2914b
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
| Dashboard Visible Settle Proof | 29450729350 | failure | `36e6bbd39cf2` | 2026-07-15T21:12:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29450729350 |
| System3 Windows Self-Hosted Full Proof | 29450763270 | failure | `36e6bbd39cf2` | 2026-07-15T21:12:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29450763270 |
| Dashboard Shell Diagnostic | 29450865323 | failure | `f10af027c5ca` | 2026-07-15T21:10:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29450865323 |
| Dashboard Visual Proof Strict Gate | 29450937574 | failure | `9fc9764b7678` | 2026-07-15T21:09:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29450937574 |
| System3 Autopilot Proof Board | 29450890259 | failure | `ccfcc2005115` | 2026-07-15T21:09:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29450890259 |
| System3 Experimental Solution Planner | 29450923348 | failure | `b064f7d144bf` | 2026-07-15T21:09:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29450923348 |
| System3 Secure Install Credential Audit | 29450890567 | failure | `ccfcc2005115` | 2026-07-15T21:09:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29450890567 |
| Dashboard Visual Loading Postflight | 29450865288 | failure | `f10af027c5ca` | 2026-07-15T21:08:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29450865288 |
| Dashboard Visible Proof Current | 29450151147 | failure | `601ea5c2914b` | 2026-07-15T21:02:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29450151147 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Safe Repair Runner | 29451463737 | in_progress | 2026-07-15T21:18:40Z |
| Dashboard Visible Issue Tracker | 29450867861 | in_progress | 2026-07-15T21:16:02Z |
| Dashboard Visible Auth-Resilient Proof | 29450985398 | in_progress | 2026-07-15T21:10:36Z |

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
