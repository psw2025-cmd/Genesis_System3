# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-28T07:52:45.908961Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `13`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `25`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30338874821 conclusion=failure commit=5f1d7a7c89b1
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30338163800 conclusion=failure commit=5f1d7a7c89b1
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30336836891 conclusion=failure commit=95d387aa6d03
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30337748883 conclusion=failure commit=5f1d7a7c89b1
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30337647288 conclusion=failure commit=5f1d7a7c89b1
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30337466788 conclusion=failure commit=f0b5560047a9
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30337434767 conclusion=failure commit=9c02af797bdc
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30337363755 conclusion=failure commit=9c02af797bdc
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30336515381 conclusion=failure commit=95d387aa6d03
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30331346641 conclusion=failure commit=9bbbc6754d7d
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30329029225 conclusion=failure commit=8cb5155b40be
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30316443824 conclusion=failure commit=dcd6da9169a4
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30316428933 conclusion=failure commit=dcd6da9169a4
- [ ] Fix Render endpoint /: HTTP status 0 status=0
- [ ] Fix Render endpoint /ui/: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/health: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/paper: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Broker Chain Semantic Gate | 30338874821 | failure | `5f1d7a7c89b1` | 2026-07-28T07:34:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30338874821 |
| Permanent Repo Render Safety | 30338163800 | failure | `5f1d7a7c89b1` | 2026-07-28T07:32:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30338163800 |
| System3 Full Auto Truth | 30336836891 | failure | `95d387aa6d03` | 2026-07-28T07:26:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30336836891 |
| Dashboard Visible Proof Warmed | 30337748883 | failure | `5f1d7a7c89b1` | 2026-07-28T07:16:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30337748883 |
| System3 Backend Live Simulation Proof | 30337647288 | failure | `5f1d7a7c89b1` | 2026-07-28T07:14:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30337647288 |
| System3 Render Worker Preflight | 30337466788 | failure | `f0b5560047a9` | 2026-07-28T07:11:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30337466788 |
| Dashboard Deploy Provenance Gate | 30337434767 | failure | `9c02af797bdc` | 2026-07-28T07:11:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30337434767 |
| Dashboard Visual Production Proof | 30337363755 | failure | `9c02af797bdc` | 2026-07-28T07:10:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30337363755 |
| Dashboard Live UI Proof | 30336515381 | failure | `95d387aa6d03` | 2026-07-28T06:56:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30336515381 |
| System3 Market Session Proof Runner | 30331346641 | failure | `9bbbc6754d7d` | 2026-07-28T05:23:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30331346641 |
| System3 Windows Self-Hosted Workflow Migration | 30329029225 | failure | `8cb5155b40be` | 2026-07-28T04:33:10Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30329029225 |
| Dashboard Visible Auth-Resilient Proof | 30316443824 | failure | `dcd6da9169a4` | 2026-07-28T00:10:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30316443824 |
| Dashboard Visual Proof Strict Gate | 30316428933 | failure | `dcd6da9169a4` | 2026-07-28T00:09:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30316428933 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30339993434 | in_progress | 2026-07-28T07:51:17Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 0 | HTTP status 0 | `none` |
| `/ui/` | 0 | HTTP status 0 | `none` |
| `/api/health` | 0 | HTTP status 0 | `none` |
| `/api/state` | 0 | HTTP status 0 | `none` |
| `/api/deploy/info` | 0 | HTTP status 0 | `none` |
| `/api/broker/diagnose` | 0 | HTTP status 0 | `none` |
| `/api/broker/funds` | 0 | HTTP status 0 | `none` |
| `/api/broker/holdings` | 0 | HTTP status 0 | `none` |
| `/api/broker/positions/live` | 0 | HTTP status 0 | `none` |
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
| `/api/paper` | 0 | HTTP status 0 | `none` |
| `/api/ml/performance` | 0 | HTTP status 0 | `none` |
