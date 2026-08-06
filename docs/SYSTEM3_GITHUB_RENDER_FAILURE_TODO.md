# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-06T22:00:46.881976Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `1`
TODO count: `7`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=31126274857 conclusion=failure commit=3210985a701d
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=31126684637 conclusion=failure commit=3210985a701d
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=31126299559 conclusion=failure commit=3210985a701d
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=31126292635 conclusion=failure commit=3210985a701d
- [ ] Fix latest GitHub workflow 'Cloud Runtime Check' run=31121732358 conclusion=failure commit=3210985a701d
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31113264837 conclusion=failure commit=a03198dde8bf
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Visual Production Proof | 31126274857 | failure | `3210985a701d` | 2026-08-06T21:58:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31126274857 |
| System3 Workflow Failure Tracker | 31126684637 | failure | `3210985a701d` | 2026-08-06T21:55:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31126684637 |
| System3 Render Worker Preflight | 31126299559 | failure | `3210985a701d` | 2026-08-06T21:53:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31126299559 |
| Dashboard Deploy Provenance Gate | 31126292635 | failure | `3210985a701d` | 2026-08-06T21:52:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31126292635 |
| Cloud Runtime Check | 31121732358 | failure | `3210985a701d` | 2026-08-06T18:00:52Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31121732358 |
| .github/workflows/options-ml-training-proof.yml | 31113264837 | failure | `a03198dde8bf` | 2026-08-06T14:55:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31113264837 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Cloud Run Auto Deploy | 31127010137 | queued | 2026-08-06T21:48:19Z |
| Genesis System3 Global Safety CI | 31127089642 | queued | 2026-08-06T21:12:50Z |
| System3 Parallel Root-Cause Audit | 31121732379 | queued | 2026-08-06T20:42:19Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
