# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-04T18:34:16.349108Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `5`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `2`
TODO count: `7`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30938562823 conclusion=cancelled commit=f396ee799182
- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=30938562499 conclusion=failure commit=f396ee799182
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30938562764 conclusion=failure commit=f396ee799182
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=30938562701 conclusion=failure commit=f396ee799182
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30938561152 conclusion=failure commit=f396ee799182
- [ ] Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Deploy Provenance Gate | 30938562823 | cancelled | `f396ee799182` | 2026-08-04T18:34:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30938562823 |
| Genesis System3 Global Safety CI | 30938562499 | failure | `f396ee799182` | 2026-08-04T18:33:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30938562499 |
| Dashboard Visual Production Proof | 30938562764 | failure | `f396ee799182` | 2026-08-04T18:31:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30938562764 |
| Dashboard Visible Proof Isolated | 30938562701 | failure | `f396ee799182` | 2026-08-04T18:29:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30938562701 |
| .github/workflows/options-ml-training-proof.yml | 30938561152 | failure | `f396ee799182` | 2026-08-04T18:25:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30938561152 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 1000 Point TODO Status Updater | 30939064824 | in_progress | 2026-08-04T18:32:12Z |
| System3 Latest Truth Publish | 30938562469 | in_progress | 2026-08-04T18:25:55Z |
| Dashboard Live UI Proof | 30938562879 | in_progress | 2026-08-04T18:25:49Z |
| Cloud Runtime Check | 30938562726 | in_progress | 2026-08-04T18:25:49Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/state` | 0 | HTTP status 0 | `none` |
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
