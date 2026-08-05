# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-05T04:56:01.798681Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
Excluded workflows: `System3 GitHub Render Failure Tracker`
GitHub failed workflows: `11`
Render failed endpoints: `12`
TODO count: `23`

## Rule

Every failed GitHub workflow and Render endpoint failure stays in this TODO until a later run proves PASS. The tracker is report-only and must not create a self-failure storm. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30975436979 conclusion=failure commit=8e8d5146dbcb
- [ ] Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30974642043 conclusion=failure commit=872ab7a222f0
- [ ] Fix GitHub workflow 'System3 Full Auto Truth' run=30974115094 conclusion=failure commit=49bae332ff50
- [ ] Fix GitHub workflow 'Dashboard Live UI Proof' run=30973994003 conclusion=failure commit=49bae332ff50
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30972333072 conclusion=cancelled commit=91eadda9480a
- [ ] Fix GitHub workflow 'Dashboard Visual Production Proof' run=30972069843 conclusion=failure commit=5c3e20aec98d
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30968082251 conclusion=cancelled commit=17286eb9475b
- [ ] Fix GitHub workflow 'Dashboard Visual Production Proof' run=30967807320 conclusion=failure commit=f852e099bfee
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30966772969 conclusion=cancelled commit=d5f35234956a
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30964756403 conclusion=cancelled commit=e63050639525
- [ ] Fix GitHub workflow 'Dashboard Visual Production Proof' run=30964472270 conclusion=failure commit=bc792246d19b
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
| System3 Windows Self-Hosted Workflow Migration | 30975436979 | failure | `8e8d5146dbcb` | 2026-08-05T04:33:21Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30975436979 |
| System3 Broker Chain Semantic Gate | 30974642043 | failure | `872ab7a222f0` | 2026-08-05T04:17:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30974642043 |
| System3 Full Auto Truth | 30974115094 | failure | `49bae332ff50` | 2026-08-05T04:24:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30974115094 |
| Dashboard Live UI Proof | 30973994003 | failure | `49bae332ff50` | 2026-08-05T04:11:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30973994003 |
| System3 1000 Point TODO Status Updater | 30972333072 | cancelled | `91eadda9480a` | 2026-08-05T03:28:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30972333072 |
| Dashboard Visual Production Proof | 30972069843 | failure | `5c3e20aec98d` | 2026-08-05T03:27:59Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30972069843 |
| System3 1000 Point TODO Status Updater | 30968082251 | cancelled | `17286eb9475b` | 2026-08-05T02:00:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30968082251 |
| Dashboard Visual Production Proof | 30967807320 | failure | `f852e099bfee` | 2026-08-05T02:00:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30967807320 |
| System3 1000 Point TODO Status Updater | 30966772969 | cancelled | `d5f35234956a` | 2026-08-05T01:34:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30966772969 |
| System3 1000 Point TODO Status Updater | 30964756403 | cancelled | `e63050639525` | 2026-08-05T00:54:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30964756403 |
| Dashboard Visual Production Proof | 30964472270 | failure | `bc792246d19b` | 2026-08-05T00:54:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30964472270 |

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
