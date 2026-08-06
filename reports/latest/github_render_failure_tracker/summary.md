# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-06T09:58:24.482488Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `1`
TODO count: `8`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=31089608670 conclusion=failure commit=344dd064ab1a
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=31089224979 conclusion=failure commit=1c5a7b8295e3
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=31089608753 conclusion=failure commit=344dd064ab1a
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=31089608188 conclusion=failure commit=344dd064ab1a
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=31089651535 conclusion=failure commit=b4e7a4fa44fb
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31089604982 conclusion=failure commit=344dd064ab1a
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=31082799240 conclusion=failure commit=11aa58cc95af
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Genesis System3 Global Safety CI | 31089608670 | failure | `344dd064ab1a` | 2026-08-06T09:45:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31089608670 |
| System3 Full Auto Truth | 31089224979 | failure | `1c5a7b8295e3` | 2026-08-06T09:40:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31089224979 |
| Dashboard Visual Production Proof | 31089608753 | failure | `344dd064ab1a` | 2026-08-06T09:39:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31089608753 |
| Dashboard Visible Proof Isolated | 31089608188 | failure | `344dd064ab1a` | 2026-08-06T09:38:14Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31089608188 |
| System3 Broker Chain Semantic Gate | 31089651535 | failure | `b4e7a4fa44fb` | 2026-08-06T09:35:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31089651535 |
| .github/workflows/options-ml-training-proof.yml | 31089604982 | failure | `344dd064ab1a` | 2026-08-06T09:33:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31089604982 |
| System3 Market Session Proof Runner | 31082799240 | failure | `11aa58cc95af` | 2026-08-06T07:59:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31082799240 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 31091036476 | in_progress | 2026-08-06T09:54:15Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
