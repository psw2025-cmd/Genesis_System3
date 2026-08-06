# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-06T06:55:42.694676Z`
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

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=31078655092 conclusion=failure commit=c7ca78a25156
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31078653667 conclusion=failure commit=c7ca78a25156
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=31077677668 conclusion=failure commit=c6d896aabe69

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Visible Proof Isolated | 31078655092 | failure | `c7ca78a25156` | 2026-08-06T06:52:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31078655092 |
| .github/workflows/options-ml-training-proof.yml | 31078653667 | failure | `c7ca78a25156` | 2026-08-06T06:50:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31078653667 |
| System3 Broker Chain Semantic Gate | 31077677668 | failure | `c6d896aabe69` | 2026-08-06T06:35:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31077677668 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 31078798508 | in_progress | 2026-08-06T06:52:54Z |
| Genesis System3 Global Safety CI | 31078655554 | queued | 2026-08-06T06:51:18Z |
| Cloud Runtime Check | 31078655083 | in_progress | 2026-08-06T06:50:28Z |
| Dashboard Visual Production Proof | 31078655344 | in_progress | 2026-08-06T06:50:26Z |
| Dashboard Live UI Proof | 31078655179 | in_progress | 2026-08-06T06:50:23Z |

## Render endpoint failures

No Render endpoint failures found in this run.
