# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-05T08:00:30.925444Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
Excluded workflows: `System3 GitHub Render Failure Tracker`
GitHub failed workflows: `12`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Every failed GitHub workflow and Render endpoint failure stays in this TODO until a later run proves PASS. The tracker is report-only and must not create a self-failure storm. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30985502041 conclusion=failure commit=9394792e893c
- [ ] Fix GitHub workflow 'System3 Latest Truth Publish' run=30984828519 conclusion=failure commit=9394792e893c
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30984661000 conclusion=cancelled commit=d7d2a3286e99
- [ ] Fix GitHub workflow 'Dashboard Visual Production Proof' run=30983968945 conclusion=failure commit=8262ef37f0c9
- [ ] Fix GitHub workflow 'System3 Full Auto Truth' run=30983489689 conclusion=failure commit=8262ef37f0c9
- [ ] Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30981649158 conclusion=failure commit=abb67e4660ad
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30978681834 conclusion=cancelled commit=f3e1691619ce
- [ ] Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30978521783 conclusion=failure commit=bb8e6733b2a5
- [ ] Fix GitHub workflow 'System3 Full Auto Truth' run=30978378566 conclusion=failure commit=bb8e6733b2a5
- [ ] Fix GitHub workflow 'System3 Latest Truth Publish' run=30978284089 conclusion=failure commit=bb8e6733b2a5
- [ ] Fix GitHub workflow 'Dashboard Visual Production Proof' run=30977879324 conclusion=failure commit=7a037cdf3917
- [ ] Fix GitHub workflow 'System3 Market Session Proof Runner' run=30977802143 conclusion=failure commit=7a037cdf3917
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
| System3 Broker Chain Semantic Gate | 30985502041 | failure | `9394792e893c` | 2026-08-05T07:34:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30985502041 |
| System3 Latest Truth Publish | 30984828519 | failure | `9394792e893c` | 2026-08-05T07:36:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30984828519 |
| System3 1000 Point TODO Status Updater | 30984661000 | cancelled | `d7d2a3286e99` | 2026-08-05T07:21:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30984661000 |
| Dashboard Visual Production Proof | 30983968945 | failure | `8262ef37f0c9` | 2026-08-05T07:20:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30983968945 |
| System3 Full Auto Truth | 30983489689 | failure | `8262ef37f0c9` | 2026-08-05T07:07:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30983489689 |
| System3 Broker Chain Semantic Gate | 30981649158 | failure | `abb67e4660ad` | 2026-08-05T06:33:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30981649158 |
| System3 1000 Point TODO Status Updater | 30978681834 | cancelled | `f3e1691619ce` | 2026-08-05T05:37:48Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30978681834 |
| System3 Broker Chain Semantic Gate | 30978521783 | failure | `bb8e6733b2a5` | 2026-08-05T05:37:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30978521783 |
| System3 Full Auto Truth | 30978378566 | failure | `bb8e6733b2a5` | 2026-08-05T05:56:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30978378566 |
| System3 Latest Truth Publish | 30978284089 | failure | `bb8e6733b2a5` | 2026-08-05T05:57:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30978284089 |
| Dashboard Visual Production Proof | 30977879324 | failure | `7a037cdf3917` | 2026-08-05T05:37:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30977879324 |
| System3 Market Session Proof Runner | 30977802143 | failure | `7a037cdf3917` | 2026-08-05T05:26:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30977802143 |

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
