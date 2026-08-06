# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-06T08:57:48.831036Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `8`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `1`
TODO count: `9`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=31085318511 conclusion=failure commit=1ccbfe906df1
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=31084473462 conclusion=failure commit=77703bbc72cd
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=31084152517 conclusion=failure commit=b8bb380c0e11
- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=31084154127 conclusion=failure commit=b8bb380c0e11
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=31084151901 conclusion=failure commit=b8bb380c0e11
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31084148213 conclusion=failure commit=b8bb380c0e11
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=31083410249 conclusion=failure commit=4ac7fb9a85dd
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=31082799240 conclusion=failure commit=11aa58cc95af
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Broker Chain Semantic Gate | 31085318511 | failure | `1ccbfe906df1` | 2026-08-06T08:34:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31085318511 |
| System3 Full Auto Truth | 31084473462 | failure | `77703bbc72cd` | 2026-08-06T08:32:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31084473462 |
| Dashboard Visual Production Proof | 31084152517 | failure | `b8bb380c0e11` | 2026-08-06T08:21:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31084152517 |
| Genesis System3 Global Safety CI | 31084154127 | failure | `b8bb380c0e11` | 2026-08-06T08:18:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31084154127 |
| Dashboard Visible Proof Isolated | 31084151901 | failure | `b8bb380c0e11` | 2026-08-06T08:17:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31084151901 |
| .github/workflows/options-ml-training-proof.yml | 31084148213 | failure | `b8bb380c0e11` | 2026-08-06T08:15:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31084148213 |
| Dashboard Deploy Provenance Gate | 31083410249 | failure | `4ac7fb9a85dd` | 2026-08-06T08:06:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31083410249 |
| System3 Market Session Proof Runner | 31082799240 | failure | `11aa58cc95af` | 2026-08-06T07:59:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31082799240 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 31086890517 | in_progress | 2026-08-06T08:55:22Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
