# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-06T13:34:06.547021Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `5`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `9`
TODO count: `14`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=31105759417 conclusion=failure commit=b329a040606b
- [ ] Fix latest GitHub workflow 'Cloud Run Auto Deploy' run=31104163503 conclusion=failure commit=a03198dde8bf
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=31103063730 conclusion=failure commit=2639a405679d
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31104160286 conclusion=failure commit=a03198dde8bf
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
| Dashboard Visual Production Proof | 31105759417 | failure | `b329a040606b` | 2026-08-06T13:30:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31105759417 |
| Cloud Run Auto Deploy | 31104163503 | failure | `a03198dde8bf` | 2026-08-06T13:08:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31104163503 |
| System3 Latest Truth Publish | 31103063730 | failure | `2639a405679d` | 2026-08-06T13:08:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31103063730 |
| .github/workflows/options-ml-training-proof.yml | 31104160286 | failure | `a03198dde8bf` | 2026-08-06T13:03:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31104160286 |
| Dashboard Visible Proof Isolated | 31103064163 | failure | `2639a405679d` | 2026-08-06T12:53:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31103064163 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

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
