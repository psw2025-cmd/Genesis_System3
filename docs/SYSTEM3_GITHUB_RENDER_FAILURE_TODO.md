# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-06T10:56:59.031086Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `10`
TODO count: `16`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=31093382909 conclusion=failure commit=ebbad34c555c
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=31093185936 conclusion=failure commit=52563f981a4c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=31093382271 conclusion=failure commit=ebbad34c555c
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=31093704198 conclusion=failure commit=c86522f76a5f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=31093382964 conclusion=failure commit=ebbad34c555c
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31093380978 conclusion=failure commit=ebbad34c555c
- [ ] Fix Render endpoint /: HTTP status 0 status=0
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
| Genesis System3 Global Safety CI | 31093382909 | failure | `ebbad34c555c` | 2026-08-06T10:39:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31093382909 |
| System3 Full Auto Truth | 31093185936 | failure | `52563f981a4c` | 2026-08-06T10:38:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31093185936 |
| Dashboard Visual Production Proof | 31093382271 | failure | `ebbad34c555c` | 2026-08-06T10:36:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31093382271 |
| System3 Broker Chain Semantic Gate | 31093704198 | failure | `c86522f76a5f` | 2026-08-06T10:34:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31093704198 |
| Dashboard Visible Proof Isolated | 31093382964 | failure | `ebbad34c555c` | 2026-08-06T10:31:40Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31093382964 |
| .github/workflows/options-ml-training-proof.yml | 31093380978 | failure | `ebbad34c555c` | 2026-08-06T10:28:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31093380978 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Market Session Proof Runner | 31095251949 | in_progress | 2026-08-06T10:56:38Z |
| System3 Latest Truth Publish | 31094922215 | in_progress | 2026-08-06T10:51:45Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 0 | HTTP status 0 | `none` |
| `/api/state` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/deploy/info` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/diagnose` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/funds` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/holdings` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/positions/live` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/scanner/top_contract_gainers` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/paper` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/ml/performance` | 401 | HTTP status 401 | `mentions_auth_error` |
