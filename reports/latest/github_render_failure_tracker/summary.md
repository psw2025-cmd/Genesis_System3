# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-05T06:58:50.135781Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `5`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `6`
TODO count: `11`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30981649158 conclusion=failure commit=abb67e4660ad
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30978378566 conclusion=failure commit=bb8e6733b2a5
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30977879324 conclusion=failure commit=7a037cdf3917
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30977802143 conclusion=failure commit=7a037cdf3917
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30975436979 conclusion=failure commit=8e8d5146dbcb
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/paper: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Broker Chain Semantic Gate | 30981649158 | failure | `abb67e4660ad` | 2026-08-05T06:33:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30981649158 |
| System3 Full Auto Truth | 30978378566 | failure | `bb8e6733b2a5` | 2026-08-05T05:56:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30978378566 |
| Dashboard Visual Production Proof | 30977879324 | failure | `7a037cdf3917` | 2026-08-05T05:37:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30977879324 |
| System3 Market Session Proof Runner | 30977802143 | failure | `7a037cdf3917` | 2026-08-05T05:26:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30977802143 |
| System3 Windows Self-Hosted Workflow Migration | 30975436979 | failure | `8e8d5146dbcb` | 2026-08-05T04:33:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30975436979 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Live UI Proof | 30983156657 | in_progress | 2026-08-05T06:57:23Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/deploy/info` | 0 | HTTP status 0 | `none` |
| `/api/broker/funds` | 0 | HTTP status 0 | `none` |
| `/api/broker/holdings` | 0 | HTTP status 0 | `none` |
| `/api/broker/positions/live` | 0 | HTTP status 0 | `none` |
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
| `/api/paper` | 0 | HTTP status 0 | `none` |
