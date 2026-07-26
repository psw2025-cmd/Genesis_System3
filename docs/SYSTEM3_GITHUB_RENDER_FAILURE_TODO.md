# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T15:24:47.786743Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `11`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30208023307 conclusion=failure commit=6c26bf0d8a19
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30207786574 conclusion=failure commit=6c26bf0d8a19
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30207697483 conclusion=failure commit=6c26bf0d8a19
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30207590151 conclusion=failure commit=c93a064f2af3
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30206818010 conclusion=failure commit=df4f16ebf079
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30206813489 conclusion=failure commit=df4f16ebf079
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30206799404 conclusion=failure commit=6d807677f462
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30206816260 conclusion=failure commit=df4f16ebf079
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30206797261 conclusion=failure commit=6d807677f462
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30206793930 conclusion=failure commit=d8a8d4a98e20
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30206784093 conclusion=failure commit=69f467499f86
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
| System3 Safe Repair Runner | 30208023307 | failure | `6c26bf0d8a19` | 2026-07-26T15:24:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30208023307 |
| Dashboard Visible Auth-Resilient Proof | 30207786574 | failure | `6c26bf0d8a19` | 2026-07-26T15:16:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30207786574 |
| Dashboard Visible Settle Proof | 30207697483 | failure | `6c26bf0d8a19` | 2026-07-26T15:12:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30207697483 |
| .github/workflows/options-ml-training-proof.yml | 30207590151 | failure | `c93a064f2af3` | 2026-07-26T15:09:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30207590151 |
| Dashboard Visible Proof Warmed | 30206818010 | failure | `df4f16ebf079` | 2026-07-26T14:48:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30206818010 |
| Dashboard Visible Issue Tracker | 30206813489 | failure | `df4f16ebf079` | 2026-07-26T14:48:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30206813489 |
| System3 Autopilot Proof Board | 30206799404 | failure | `6d807677f462` | 2026-07-26T14:47:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30206799404 |
| System3 Experimental Solution Planner | 30206816260 | failure | `df4f16ebf079` | 2026-07-26T14:47:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30206816260 |
| System3 Secure Install Credential Audit | 30206797261 | failure | `6d807677f462` | 2026-07-26T14:47:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30206797261 |
| System3 Backend Live Simulation Proof | 30206793930 | failure | `d8a8d4a98e20` | 2026-07-26T14:47:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30206793930 |
| Dashboard Visual Loading Postflight | 30206784093 | failure | `69f467499f86` | 2026-07-26T14:46:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30206784093 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Windows Self-Hosted Full Proof | 30207713006 | queued | 2026-07-26T15:12:42Z |
| Options Big-Data Full History | 30207591952 | in_progress | 2026-07-26T15:09:36Z |
| Genesis System3 Global Safety CI | 30207591964 | queued | 2026-07-26T15:09:15Z |
| Options Big-Data Research | 30207591950 | queued | 2026-07-26T15:09:14Z |

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
