# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-04T06:53:59.562376Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `3`
TODO count: `10`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30884273294 conclusion=failure commit=033bc303c6ec
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30880990985 conclusion=failure commit=764bc2f04682
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30880937571 conclusion=failure commit=764bc2f04682
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30880454597 conclusion=failure commit=e205e884b932
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30880379233 conclusion=failure commit=e205e884b932
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30878032560 conclusion=failure commit=1c1e167acbab
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30864904430 conclusion=failure commit=2f8fa0dc30f7
- [ ] Fix Render endpoint /api/broker/diagnose: authentication error classification detected status=200
- [ ] Fix Render endpoint /api/broker/funds: authentication error classification detected status=200
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Broker Chain Semantic Gate | 30884273294 | failure | `033bc303c6ec` | 2026-08-04T06:31:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30884273294 |
| System3 Full Auto Truth | 30880990985 | failure | `764bc2f04682` | 2026-08-04T05:47:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30880990985 |
| Dashboard Live UI Proof | 30880937571 | failure | `764bc2f04682` | 2026-08-04T05:39:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30880937571 |
| Dashboard Visual Production Proof | 30880454597 | failure | `e205e884b932` | 2026-08-04T05:29:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30880454597 |
| System3 Market Session Proof Runner | 30880379233 | failure | `e205e884b932` | 2026-08-04T05:24:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30880379233 |
| System3 Windows Self-Hosted Workflow Migration | 30878032560 | failure | `1c1e167acbab` | 2026-08-04T04:34:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30878032560 |
| .github/workflows/options-ml-training-proof.yml | 30864904430 | failure | `2f8fa0dc30f7` | 2026-08-04T00:13:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30864904430 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30885429205 | in_progress | 2026-08-04T06:50:25Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/broker/diagnose` | 200 | authentication error classification detected | `mentions_auth_error` |
| `/api/broker/funds` | 200 | authentication error classification detected | `mentions_auth_error` |
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
