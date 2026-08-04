# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-04T03:03:42.382535Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `4`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `2`
TODO count: `6`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30870199180 conclusion=failure commit=a5c84d510501
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30864904430 conclusion=failure commit=2f8fa0dc30f7
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30864342476 conclusion=failure commit=310b976c6ea9
- [ ] Fix latest GitHub workflow 'Dashboard Visual Contract Check' run=30864342499 conclusion=failure commit=310b976c6ea9
- [ ] Fix Render endpoint /api/broker/diagnose: authentication error classification detected status=200
- [ ] Fix Render endpoint /api/broker/funds: authentication error classification detected status=200

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Visual Production Proof | 30870199180 | failure | `a5c84d510501` | 2026-08-04T02:00:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30870199180 |
| .github/workflows/options-ml-training-proof.yml | 30864904430 | failure | `2f8fa0dc30f7` | 2026-08-04T00:13:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30864904430 |
| System3 Latest Truth Publish | 30864342476 | failure | `310b976c6ea9` | 2026-08-04T00:11:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30864342476 |
| Dashboard Visual Contract Check | 30864342499 | failure | `310b976c6ea9` | 2026-08-04T00:04:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30864342499 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/broker/diagnose` | 200 | authentication error classification detected | `mentions_auth_error` |
| `/api/broker/funds` | 200 | authentication error classification detected | `mentions_auth_error` |
