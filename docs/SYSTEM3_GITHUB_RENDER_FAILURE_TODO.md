# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-04T20:33:10.056660Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `2`
TODO count: `8`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30947514689 conclusion=failure commit=0afce386fe11
- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=30947514852 conclusion=failure commit=0afce386fe11
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30947514717 conclusion=failure commit=0afce386fe11
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=30947515181 conclusion=failure commit=0afce386fe11
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30947513277 conclusion=failure commit=0afce386fe11
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30945188947 conclusion=cancelled commit=509022c9cf04
- [ ] Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Latest Truth Publish | 30947514689 | failure | `0afce386fe11` | 2026-08-04T20:31:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30947514689 |
| Genesis System3 Global Safety CI | 30947514852 | failure | `0afce386fe11` | 2026-08-04T20:26:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30947514852 |
| Dashboard Visual Production Proof | 30947514717 | failure | `0afce386fe11` | 2026-08-04T20:25:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30947514717 |
| Dashboard Visible Proof Isolated | 30947515181 | failure | `0afce386fe11` | 2026-08-04T20:24:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30947515181 |
| .github/workflows/options-ml-training-proof.yml | 30947513277 | failure | `0afce386fe11` | 2026-08-04T20:21:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30947513277 |
| Dashboard Deploy Provenance Gate | 30945188947 | cancelled | `509022c9cf04` | 2026-08-04T19:59:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30945188947 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/state` | 0 | HTTP status 0 | `none` |
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
