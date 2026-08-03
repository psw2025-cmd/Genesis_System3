# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T07:08:27.873732Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `9`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30788173526 conclusion=failure commit=eea81b4479b3
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30788427664 conclusion=failure commit=eea81b4479b3
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30788102080 conclusion=failure commit=eea81b4479b3
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30787492950 conclusion=failure commit=eea81b4479b3
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30787393323 conclusion=failure commit=eea81b4479b3
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30787216244 conclusion=failure commit=10d6b2620033
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=30787058658 conclusion=failure commit=c3a4f173ac38
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30787163961 conclusion=failure commit=c3a4f173ac38
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30785078018 conclusion=failure commit=f660e3fc0791
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
| System3 Full Auto Truth | 30788173526 | failure | `eea81b4479b3` | 2026-08-03T06:12:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30788173526 |
| System3 Broker Chain Semantic Gate | 30788427664 | failure | `eea81b4479b3` | 2026-08-03T05:59:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30788427664 |
| Dashboard Live UI Proof | 30788102080 | failure | `eea81b4479b3` | 2026-08-03T05:46:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30788102080 |
| Dashboard Visible Proof Warmed | 30787492950 | failure | `eea81b4479b3` | 2026-08-03T05:34:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30787492950 |
| System3 Backend Live Simulation Proof | 30787393323 | failure | `eea81b4479b3` | 2026-08-03T05:31:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30787393323 |
| Dashboard Deploy Provenance Gate | 30787216244 | failure | `10d6b2620033` | 2026-08-03T05:28:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30787216244 |
| System3 Market Session Proof Runner | 30787058658 | failure | `c3a4f173ac38` | 2026-08-03T05:27:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30787058658 |
| Dashboard Visual Production Proof | 30787163961 | failure | `c3a4f173ac38` | 2026-08-03T05:27:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30787163961 |
| System3 Windows Self-Hosted Workflow Migration | 30785078018 | failure | `f660e3fc0791` | 2026-08-03T04:41:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30785078018 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Latest Truth Publish | 30792336214 | in_progress | 2026-08-03T07:05:11Z |
| Permanent Repo Render Safety | 30792055891 | in_progress | 2026-08-03T07:00:23Z |

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
