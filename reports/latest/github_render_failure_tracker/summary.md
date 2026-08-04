# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-04T08:58:18.766179Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `1`
TODO count: `7`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30892384283 conclusion=failure commit=f8cfe895f848
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30891570278 conclusion=failure commit=f8cfe895f848
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30890745930 conclusion=failure commit=4fc211e5489e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30890439513 conclusion=failure commit=1082a5490f62
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30889750672 conclusion=failure commit=b0f9ec535b7c
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30878032560 conclusion=failure commit=1c1e167acbab
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Broker Chain Semantic Gate | 30892384283 | failure | `f8cfe895f848` | 2026-08-04T08:32:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30892384283 |
| System3 Full Auto Truth | 30891570278 | failure | `f8cfe895f848` | 2026-08-04T08:26:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30891570278 |
| Dashboard Visible Proof Warmed | 30890745930 | failure | `4fc211e5489e` | 2026-08-04T08:14:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30890745930 |
| Dashboard Visual Production Proof | 30890439513 | failure | `1082a5490f62` | 2026-08-04T08:09:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30890439513 |
| System3 Market Session Proof Runner | 30889750672 | failure | `b0f9ec535b7c` | 2026-08-04T07:58:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30889750672 |
| System3 Windows Self-Hosted Workflow Migration | 30878032560 | failure | `1c1e167acbab` | 2026-08-04T04:34:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30878032560 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30894061045 | in_progress | 2026-08-04T08:56:01Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
