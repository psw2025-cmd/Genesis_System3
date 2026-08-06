# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-06T07:53:40.969459Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `4`
GitHub workflows currently queued/in progress: `6`
Render failed endpoints: `0`
TODO count: `4`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=31082440921 conclusion=failure commit=9a3bf413994c
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31082439841 conclusion=failure commit=9a3bf413994c
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=31081394855 conclusion=failure commit=ecad60632373
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=31079404649 conclusion=failure commit=be57adf87dc9

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Visible Proof Isolated | 31082440921 | failure | `9a3bf413994c` | 2026-08-06T07:52:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31082440921 |
| .github/workflows/options-ml-training-proof.yml | 31082439841 | failure | `9a3bf413994c` | 2026-08-06T07:50:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31082439841 |
| System3 Broker Chain Semantic Gate | 31081394855 | failure | `ecad60632373` | 2026-08-06T07:34:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31081394855 |
| System3 Full Auto Truth | 31079404649 | failure | `be57adf87dc9` | 2026-08-06T07:18:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31079404649 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 31082539779 | in_progress | 2026-08-06T07:51:39Z |
| Genesis System3 Global Safety CI | 31082441001 | queued | 2026-08-06T07:50:40Z |
| Cloud Runtime Check | 31082440956 | in_progress | 2026-08-06T07:50:09Z |
| Cloud Run Auto Deploy | 31082440902 | in_progress | 2026-08-06T07:50:09Z |
| Dashboard Live UI Proof | 31082441000 | in_progress | 2026-08-06T07:50:08Z |
| Dashboard Visual Production Proof | 31082440955 | in_progress | 2026-08-06T07:50:08Z |

## Render endpoint failures

No Render endpoint failures found in this run.
