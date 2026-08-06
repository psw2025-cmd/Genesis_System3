# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-06T12:39:10.352270Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `3`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `1`
TODO count: `4`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31102258798 conclusion=failure commit=4b0442430855
- [ ] Fix latest GitHub workflow 'Deploy Genesis System3 to Cloud Run (Unified)' run=31101002913 conclusion=failure commit=e330c1d200ef
- [ ] Fix latest GitHub workflow 'Deploy Genesis System3 to Cloud Run' run=31100205424 conclusion=failure commit=fd21dd354963
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| .github/workflows/options-ml-training-proof.yml | 31102258798 | failure | `4b0442430855` | 2026-08-06T12:38:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31102258798 |
| Deploy Genesis System3 to Cloud Run (Unified) | 31101002913 | failure | `e330c1d200ef` | 2026-08-06T12:21:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31101002913 |
| Deploy Genesis System3 to Cloud Run | 31100205424 | failure | `fd21dd354963` | 2026-08-06T12:09:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31100205424 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| GCP Dhan Token Fix CI | 31102296215 | in_progress | 2026-08-06T12:39:04Z |
| Genesis System3 Global Safety CI | 31102296205 | in_progress | 2026-08-06T12:39:01Z |
| GCP Stage 2 Safety Checks | 31102296157 | in_progress | 2026-08-06T12:38:59Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
