# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-04T05:05:43.623850Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `8`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `5`
TODO count: `13`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30878847972 conclusion=failure commit=44a0832b4b8c
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30878032560 conclusion=failure commit=1c1e167acbab
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30876635099 conclusion=failure commit=f4ff64368d0f
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30877188043 conclusion=failure commit=6b4b1e5674f7
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30876524506 conclusion=failure commit=f4ff64368d0f
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30874577485 conclusion=failure commit=9b136f91ba16
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30864904430 conclusion=failure commit=2f8fa0dc30f7
- [ ] Fix latest GitHub workflow 'Dashboard Visual Contract Check' run=30864342499 conclusion=failure commit=310b976c6ea9
- [ ] Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/diagnose: authentication error classification detected status=200
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/paper: HTTP status 429 status=429
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 429 status=429

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Market Session Proof Runner | 30878847972 | failure | `44a0832b4b8c` | 2026-08-04T04:54:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30878847972 |
| System3 Windows Self-Hosted Workflow Migration | 30878032560 | failure | `1c1e167acbab` | 2026-08-04T04:34:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30878032560 |
| System3 Full Auto Truth | 30876635099 | failure | `f4ff64368d0f` | 2026-08-04T04:24:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30876635099 |
| System3 Broker Chain Semantic Gate | 30877188043 | failure | `6b4b1e5674f7` | 2026-08-04T04:17:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30877188043 |
| Dashboard Live UI Proof | 30876524506 | failure | `f4ff64368d0f` | 2026-08-04T04:13:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30876524506 |
| Dashboard Visual Production Proof | 30874577485 | failure | `9b136f91ba16` | 2026-08-04T03:28:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30874577485 |
| .github/workflows/options-ml-training-proof.yml | 30864904430 | failure | `2f8fa0dc30f7` | 2026-08-04T00:13:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30864904430 |
| Dashboard Visual Contract Check | 30864342499 | failure | `310b976c6ea9` | 2026-08-04T00:04:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30864342499 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/state` | 0 | HTTP status 0 | `none` |
| `/api/broker/diagnose` | 200 | authentication error classification detected | `mentions_auth_error` |
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
| `/api/paper` | 429 | HTTP status 429 | `none` |
| `/api/ml/performance` | 429 | HTTP status 429 | `none` |
