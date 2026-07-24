# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-24T11:33:21.804592Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30089797451 conclusion=failure commit=a6ddffd48bee
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30089018864 conclusion=failure commit=78250c65fad5
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30088860057 conclusion=failure commit=844a81bc62ea
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30088839328 conclusion=failure commit=4113530f65ae
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30088860055 conclusion=failure commit=844a81bc62ea
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30088860155 conclusion=failure commit=844a81bc62ea
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30088860070 conclusion=failure commit=844a81bc62ea
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30088860106 conclusion=failure commit=844a81bc62ea
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30088804258 conclusion=failure commit=16df06be5625
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30088197930 conclusion=failure commit=c3ab6ae2658d
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30088091799 conclusion=failure commit=3defd89669c2
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30088010299 conclusion=failure commit=7b990445014a
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
| System3 Safe Repair Runner | 30089797451 | failure | `a6ddffd48bee` | 2026-07-24T11:32:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30089797451 |
| System3 Broker Chain Semantic Gate | 30089018864 | failure | `78250c65fad5` | 2026-07-24T11:17:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30089018864 |
| Dashboard Shell Diagnostic | 30088860057 | failure | `844a81bc62ea` | 2026-07-24T11:15:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30088860057 |
| Dashboard Visible Issue Tracker | 30088839328 | failure | `4113530f65ae` | 2026-07-24T11:14:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30088839328 |
| System3 Secure Install Credential Audit | 30088860055 | failure | `844a81bc62ea` | 2026-07-24T11:14:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30088860055 |
| Dashboard Visual Proof Strict Gate | 30088860155 | failure | `844a81bc62ea` | 2026-07-24T11:14:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30088860155 |
| System3 Experimental Solution Planner | 30088860070 | failure | `844a81bc62ea` | 2026-07-24T11:14:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30088860070 |
| Dashboard Visual Loading Postflight | 30088860106 | failure | `844a81bc62ea` | 2026-07-24T11:14:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30088860106 |
| System3 Autopilot Proof Board | 30088804258 | failure | `16df06be5625` | 2026-07-24T11:13:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30088804258 |
| Dashboard Visible Proof Warmed | 30088197930 | failure | `c3ab6ae2658d` | 2026-07-24T11:02:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30088197930 |
| System3 Backend Live Simulation Proof | 30088091799 | failure | `3defd89669c2` | 2026-07-24T11:00:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30088091799 |
| Dashboard Visible Auth-Resilient Proof | 30088010299 | failure | `7b990445014a` | 2026-07-24T10:59:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30088010299 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Full Auto Truth | 30088733325 | in_progress | 2026-07-24T11:11:54Z |

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
