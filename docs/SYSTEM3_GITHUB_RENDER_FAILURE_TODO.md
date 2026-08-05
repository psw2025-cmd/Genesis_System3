# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-05T10:00:09.764946Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `11`
TODO count: `17`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30993735175 conclusion=failure commit=d183e4c1006a
- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30993053266 conclusion=failure commit=df936070943d
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30992305700 conclusion=failure commit=fb586b832c94
- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=30992339504 conclusion=action_required commit=71572eee7c17
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30986935741 conclusion=failure commit=929dd9f25752
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30975436979 conclusion=failure commit=8e8d5146dbcb
- [ ] Fix Render endpoint /: HTTP status 0 status=0
- [ ] Fix Render endpoint /ui/: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/paper: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 401 status=401

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Broker Chain Semantic Gate | 30993735175 | failure | `d183e4c1006a` | 2026-08-05T09:37:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30993735175 |
| System3 Latest Truth Publish | 30993053266 | failure | `df936070943d` | 2026-08-05T09:31:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30993053266 |
| Dashboard Visual Production Proof | 30992305700 | failure | `fb586b832c94` | 2026-08-05T09:18:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30992305700 |
| Genesis System3 Global Safety CI | 30992339504 | action_required | `71572eee7c17` | 2026-08-05T09:13:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30992339504 |
| System3 Market Session Proof Runner | 30986935741 | failure | `929dd9f25752` | 2026-08-05T08:00:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30986935741 |
| System3 Windows Self-Hosted Workflow Migration | 30975436979 | failure | `8e8d5146dbcb` | 2026-08-05T04:33:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30975436979 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Full Auto Truth | 30993241854 | in_progress | 2026-08-05T09:26:10Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 0 | HTTP status 0 | `none` |
| `/ui/` | 0 | HTTP status 0 | `none` |
| `/api/state` | 0 | HTTP status 0 | `none` |
| `/api/deploy/info` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/diagnose` | 0 | HTTP status 0 | `none` |
| `/api/broker/funds` | 0 | HTTP status 0 | `none` |
| `/api/broker/holdings` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/positions/live` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/scanner/top_contract_gainers` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/paper` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/ml/performance` | 401 | HTTP status 401 | `mentions_auth_error` |
