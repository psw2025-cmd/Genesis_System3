# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-05T05:08:05.045568Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `6`
TODO count: `13`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30976302634 conclusion=failure commit=e7af8bdab719
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30975436979 conclusion=failure commit=8e8d5146dbcb
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30974115094 conclusion=failure commit=49bae332ff50
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30974642043 conclusion=failure commit=872ab7a222f0
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30973994003 conclusion=failure commit=49bae332ff50
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30972069843 conclusion=failure commit=5c3e20aec98d
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30953443498 conclusion=failure commit=1e22833f14b3
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/paper: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Market Session Proof Runner | 30976302634 | failure | `e7af8bdab719` | 2026-08-05T04:56:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30976302634 |
| System3 Windows Self-Hosted Workflow Migration | 30975436979 | failure | `8e8d5146dbcb` | 2026-08-05T04:33:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30975436979 |
| System3 Full Auto Truth | 30974115094 | failure | `49bae332ff50` | 2026-08-05T04:24:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30974115094 |
| System3 Broker Chain Semantic Gate | 30974642043 | failure | `872ab7a222f0` | 2026-08-05T04:17:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30974642043 |
| Dashboard Live UI Proof | 30973994003 | failure | `49bae332ff50` | 2026-08-05T04:11:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30973994003 |
| Dashboard Visual Production Proof | 30972069843 | failure | `5c3e20aec98d` | 2026-08-05T03:27:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30972069843 |
| .github/workflows/options-ml-training-proof.yml | 30953443498 | failure | `1e22833f14b3` | 2026-08-04T21:42:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30953443498 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/broker/funds` | 0 | HTTP status 0 | `none` |
| `/api/broker/holdings` | 0 | HTTP status 0 | `none` |
| `/api/broker/positions/live` | 0 | HTTP status 0 | `none` |
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
| `/api/paper` | 0 | HTTP status 0 | `none` |
| `/api/ml/performance` | 0 | HTTP status 0 | `none` |
