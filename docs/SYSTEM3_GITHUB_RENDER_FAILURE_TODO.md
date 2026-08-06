# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-06T14:47:36.732066Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `9`
TODO count: `16`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31112503652 conclusion=failure commit=a03198dde8bf
- [ ] Fix latest GitHub workflow 'System3 1000 Point TODO Status Updater' run=31109982199 conclusion=cancelled commit=9384df8dadbe
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=31108818095 conclusion=failure commit=c64f2f6ad50b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=31108182775 conclusion=failure commit=22f63ca93073
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=31108274718 conclusion=failure commit=22f63ca93073
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=31103063730 conclusion=failure commit=2639a405679d
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=31103064163 conclusion=failure commit=2639a405679d
- [ ] Fix Render endpoint /api/state: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/paper: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 401 status=401

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| .github/workflows/options-ml-training-proof.yml | 31112503652 | failure | `a03198dde8bf` | 2026-08-06T14:46:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31112503652 |
| System3 1000 Point TODO Status Updater | 31109982199 | cancelled | `9384df8dadbe` | 2026-08-06T14:26:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31109982199 |
| Dashboard Visible Proof Warmed | 31108818095 | failure | `c64f2f6ad50b` | 2026-08-06T14:03:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31108818095 |
| Dashboard Visual Production Proof | 31108182775 | failure | `22f63ca93073` | 2026-08-06T14:00:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31108182775 |
| Dashboard Deploy Provenance Gate | 31108274718 | failure | `22f63ca93073` | 2026-08-06T13:56:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31108274718 |
| System3 Latest Truth Publish | 31103063730 | failure | `2639a405679d` | 2026-08-06T13:08:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31103063730 |
| Dashboard Visible Proof Isolated | 31103064163 | failure | `2639a405679d` | 2026-08-06T12:53:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31103064163 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Cloud Run Auto Deploy | 31104163503 | in_progress | 2026-08-06T14:46:34Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/state` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/deploy/info` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/diagnose` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/funds` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/holdings` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/positions/live` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/scanner/top_contract_gainers` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/paper` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/ml/performance` | 401 | HTTP status 401 | `mentions_auth_error` |
