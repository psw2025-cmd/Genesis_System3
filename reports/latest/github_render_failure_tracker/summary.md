# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-05T08:59:45.785841Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `5`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `3`
TODO count: `8`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30988600970 conclusion=failure commit=4314268b3c70
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30988397418 conclusion=failure commit=bdc011685bca
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30987581480 conclusion=failure commit=b45eef47330f
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30986935741 conclusion=failure commit=929dd9f25752
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30975436979 conclusion=failure commit=8e8d5146dbcb
- [ ] Fix Render endpoint /api/health: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/paper: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Full Auto Truth | 30988600970 | failure | `4314268b3c70` | 2026-08-05T08:27:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30988600970 |
| System3 Latest Truth Publish | 30988397418 | failure | `bdc011685bca` | 2026-08-05T08:25:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30988397418 |
| Dashboard Visual Production Proof | 30987581480 | failure | `b45eef47330f` | 2026-08-05T08:18:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30987581480 |
| System3 Market Session Proof Runner | 30986935741 | failure | `929dd9f25752` | 2026-08-05T08:00:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30986935741 |
| System3 Windows Self-Hosted Workflow Migration | 30975436979 | failure | `8e8d5146dbcb` | 2026-08-05T04:33:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30975436979 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/health` | 0 | HTTP status 0 | `none` |
| `/api/state` | 0 | HTTP status 0 | `none` |
| `/api/paper` | 0 | HTTP status 0 | `none` |
