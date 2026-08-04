# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-04T04:54:05.648291Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
Excluded workflows: `System3 GitHub Render Failure Tracker`
GitHub failed workflows: `9`
Render failed endpoints: `12`
TODO count: `21`

## Rule

Every failed GitHub workflow and Render endpoint failure stays in this TODO until a later run proves PASS. The tracker is report-only and must not create a self-failure storm. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30878032560 conclusion=failure commit=1c1e167acbab
- [ ] Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30877188043 conclusion=failure commit=6b4b1e5674f7
- [ ] Fix GitHub workflow 'System3 Full Auto Truth' run=30876635099 conclusion=failure commit=f4ff64368d0f
- [ ] Fix GitHub workflow 'Dashboard Live UI Proof' run=30876524506 conclusion=failure commit=f4ff64368d0f
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30874834600 conclusion=cancelled commit=34a6040ef1a5
- [ ] Fix GitHub workflow 'Dashboard Visual Production Proof' run=30874577485 conclusion=failure commit=9b136f91ba16
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30870485830 conclusion=cancelled commit=9ae1b2dee298
- [ ] Fix GitHub workflow 'Dashboard Visual Production Proof' run=30870199180 conclusion=failure commit=a5c84d510501
- [ ] Fix GitHub workflow 'Dashboard Visual Production Proof' run=30867012854 conclusion=failure commit=9d28ba295cde
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

## GitHub workflow failures

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Windows Self-Hosted Workflow Migration | 30878032560 | failure | `1c1e167acbab` | 2026-08-04T04:34:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30878032560 |
| System3 Broker Chain Semantic Gate | 30877188043 | failure | `6b4b1e5674f7` | 2026-08-04T04:17:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30877188043 |
| System3 Full Auto Truth | 30876635099 | failure | `f4ff64368d0f` | 2026-08-04T04:24:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30876635099 |
| Dashboard Live UI Proof | 30876524506 | failure | `f4ff64368d0f` | 2026-08-04T04:13:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30876524506 |
| System3 1000 Point TODO Status Updater | 30874834600 | cancelled | `34a6040ef1a5` | 2026-08-04T03:28:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30874834600 |
| Dashboard Visual Production Proof | 30874577485 | failure | `9b136f91ba16` | 2026-08-04T03:28:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30874577485 |
| System3 1000 Point TODO Status Updater | 30870485830 | cancelled | `9ae1b2dee298` | 2026-08-04T02:00:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30870485830 |
| Dashboard Visual Production Proof | 30870199180 | failure | `a5c84d510501` | 2026-08-04T02:00:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30870199180 |
| Dashboard Visual Production Proof | 30867012854 | failure | `9d28ba295cde` | 2026-08-04T00:58:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30867012854 |

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
