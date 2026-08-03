# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T23:41:31.817477Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `3`
GitHub workflows currently queued/in progress: `11`
Render failed endpoints: `9`
TODO count: `12`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30863099438 conclusion=failure commit=7fe876a1469b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Contract Check' run=30862677478 conclusion=failure commit=32f201c606a7
- [ ] Fix latest GitHub workflow 'System3 Render Worker Issue Proof' run=30862677460 conclusion=failure commit=32f201c606a7
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
| .github/workflows/options-ml-training-proof.yml | 30863099438 | failure | `7fe876a1469b` | 2026-08-03T23:41:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30863099438 |
| Dashboard Visual Contract Check | 30862677478 | failure | `32f201c606a7` | 2026-08-03T23:34:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30862677478 |
| System3 Render Worker Issue Proof | 30862677460 | failure | `32f201c606a7` | 2026-08-03T23:33:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30862677460 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visual Production Proof | 30863100141 | in_progress | 2026-08-03T23:41:25Z |
| Permanent Repo Render Safety | 30863100152 | in_progress | 2026-08-03T23:41:24Z |
| System3 Broker Chain Semantic Gate | 30863100107 | in_progress | 2026-08-03T23:41:24Z |
| System3 Backend Live Simulation Proof | 30863105264 | pending | 2026-08-03T23:41:22Z |
| Dashboard Visible Proof Isolated | 30863100178 | in_progress | 2026-08-03T23:41:19Z |
| Dashboard Visible Proof Warmed | 30863100145 | in_progress | 2026-08-03T23:41:19Z |
| Dashboard Deploy Provenance Gate | 30863100100 | in_progress | 2026-08-03T23:41:19Z |
| System3 Latest Truth Publish | 30863100184 | in_progress | 2026-08-03T23:41:18Z |
| Dashboard Live UI Proof | 30863100175 | in_progress | 2026-08-03T23:41:18Z |
| Genesis System3 Global Safety CI | 30863100149 | pending | 2026-08-03T23:41:16Z |
| Cloud Runtime Check | 30863100097 | pending | 2026-08-03T23:41:16Z |

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
