# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T22:20:13.590024Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Options Big-Data Artifact Model' run=30222845719 conclusion=failure commit=530b4594a21d
- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30222818038 conclusion=failure commit=3a09f7c900c6
- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=30222845708 conclusion=failure commit=530b4594a21d
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30222844042 conclusion=failure commit=530b4594a21d
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30222454774 conclusion=failure commit=3a09f7c900c6
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30222532835 conclusion=failure commit=3a09f7c900c6
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30222529275 conclusion=failure commit=3a09f7c900c6
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30222433609 conclusion=failure commit=3a09f7c900c6
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30222086156 conclusion=failure commit=4efd884ddb87
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
| Options Big-Data Artifact Model | 30222845719 | failure | `530b4594a21d` | 2026-07-26T22:19:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30222845719 |
| System3 Safe Repair Runner | 30222818038 | failure | `3a09f7c900c6` | 2026-07-26T22:19:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30222818038 |
| Genesis System3 Global Safety CI | 30222845708 | failure | `530b4594a21d` | 2026-07-26T22:18:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30222845708 |
| .github/workflows/options-ml-training-proof.yml | 30222844042 | failure | `530b4594a21d` | 2026-07-26T22:17:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30222844042 |
| System3 Windows Self-Hosted Full Proof | 30222454774 | failure | `3a09f7c900c6` | 2026-07-26T22:17:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30222454774 |
| Dashboard Visible Auth-Resilient Proof | 30222532835 | failure | `3a09f7c900c6` | 2026-07-26T22:09:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30222532835 |
| Dashboard Visual Proof Strict Gate | 30222529275 | failure | `3a09f7c900c6` | 2026-07-26T22:08:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30222529275 |
| Dashboard Visible Settle Proof | 30222433609 | failure | `3a09f7c900c6` | 2026-07-26T22:06:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30222433609 |
| Dashboard Visible Proof Current | 30222086156 | failure | `4efd884ddb87` | 2026-07-26T21:56:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30222086156 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Options Big-Data Self-Hosted Model | 30222845703 | in_progress | 2026-07-26T22:18:46Z |
| Options Big-Data Full History | 30222845692 | in_progress | 2026-07-26T22:18:00Z |
| Options Big-Data Research | 30222845711 | queued | 2026-07-26T22:17:41Z |

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
