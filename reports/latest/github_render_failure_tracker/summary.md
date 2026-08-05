# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-05T07:54:19.713848Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `1`
TODO count: `7`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30984828519 conclusion=failure commit=9394792e893c
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30985502041 conclusion=failure commit=9394792e893c
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30983968945 conclusion=failure commit=8262ef37f0c9
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30983489689 conclusion=failure commit=8262ef37f0c9
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30977802143 conclusion=failure commit=7a037cdf3917
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30975436979 conclusion=failure commit=8e8d5146dbcb
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Latest Truth Publish | 30984828519 | failure | `9394792e893c` | 2026-08-05T07:36:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30984828519 |
| System3 Broker Chain Semantic Gate | 30985502041 | failure | `9394792e893c` | 2026-08-05T07:34:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30985502041 |
| Dashboard Visual Production Proof | 30983968945 | failure | `8262ef37f0c9` | 2026-08-05T07:20:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30983968945 |
| System3 Full Auto Truth | 30983489689 | failure | `8262ef37f0c9` | 2026-08-05T07:07:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30983489689 |
| System3 Market Session Proof Runner | 30977802143 | failure | `7a037cdf3917` | 2026-08-05T05:26:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30977802143 |
| System3 Windows Self-Hosted Workflow Migration | 30975436979 | failure | `8e8d5146dbcb` | 2026-08-05T04:33:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30975436979 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
