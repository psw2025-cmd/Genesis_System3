# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-04T17:33:05.947882Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `3`
GitHub workflows currently queued/in progress: `5`
Render failed endpoints: `0`
TODO count: `3`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=30933913051 conclusion=failure commit=5a6ba9e2d866
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30933907901 conclusion=failure commit=5a6ba9e2d866
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30931374822 conclusion=cancelled commit=16dfb18ed3e7

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Visible Proof Isolated | 30933913051 | failure | `5a6ba9e2d866` | 2026-08-04T17:31:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30933913051 |
| .github/workflows/options-ml-training-proof.yml | 30933907901 | failure | `5a6ba9e2d866` | 2026-08-04T17:26:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30933907901 |
| Dashboard Deploy Provenance Gate | 30931374822 | cancelled | `16dfb18ed3e7` | 2026-08-04T17:02:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30931374822 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Genesis System3 Global Safety CI | 30933913100 | queued | 2026-08-04T17:27:08Z |
| System3 Latest Truth Publish | 30933916949 | in_progress | 2026-08-04T17:26:37Z |
| Cloud Runtime Check | 30933913165 | in_progress | 2026-08-04T17:26:35Z |
| Dashboard Visual Production Proof | 30933913038 | in_progress | 2026-08-04T17:26:35Z |
| Dashboard Live UI Proof | 30933913147 | in_progress | 2026-08-04T17:26:34Z |

## Render endpoint failures

No Render endpoint failures found in this run.
