# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T19:31:48.566716Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `14`
GitHub workflows currently queued/in progress: `2`
Render failed endpoints: `12`
TODO count: `26`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30845368027 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30845368341 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30845368558 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30845368059 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=30845367981 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30845368287 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Contract Check' run=30845368512 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30845370303 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'System3 Parallel Root-Cause Audit' run=30845369318 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'Dhan Only Data Truth Proof' run=30845368220 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30845365815 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30843334460 conclusion=failure commit=0e24215a50c1
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=30810589818 conclusion=failure commit=509c96d50542
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=30811080508 conclusion=failure commit=509c96d50542
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
| Permanent Repo Render Safety | 30845368027 | failure | `7d317001e66e` | 2026-08-03T19:30:27Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368027 |
| System3 Backend Live Simulation Proof | 30845368341 | failure | `7d317001e66e` | 2026-08-03T19:23:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368341 |
| Dashboard Visible Proof Warmed | 30845368558 | failure | `7d317001e66e` | 2026-08-03T19:21:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368558 |
| Dashboard Visual Production Proof | 30845368059 | failure | `7d317001e66e` | 2026-08-03T19:21:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368059 |
| Dashboard Visible Proof Isolated | 30845367981 | failure | `7d317001e66e` | 2026-08-03T19:21:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845367981 |
| Dashboard Deploy Provenance Gate | 30845368287 | failure | `7d317001e66e` | 2026-08-03T19:21:37Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368287 |
| Dashboard Visual Contract Check | 30845368512 | failure | `7d317001e66e` | 2026-08-03T19:21:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368512 |
| Dashboard Live UI Proof | 30845370303 | failure | `7d317001e66e` | 2026-08-03T19:21:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845370303 |
| System3 Parallel Root-Cause Audit | 30845369318 | failure | `7d317001e66e` | 2026-08-03T19:21:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845369318 |
| Dhan Only Data Truth Proof | 30845368220 | failure | `7d317001e66e` | 2026-08-03T19:21:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368220 |
| .github/workflows/options-ml-training-proof.yml | 30845365815 | failure | `7d317001e66e` | 2026-08-03T19:20:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845365815 |
| System3 Render Worker Preflight | 30843334460 | failure | `0e24215a50c1` | 2026-08-03T18:54:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30843334460 |
| System3 Full Auto Truth | 30810589818 | failure | `509c96d50542` | 2026-08-03T12:07:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30810589818 |
| System3 Broker Chain Semantic Gate | 30811080508 | failure | `509c96d50542` | 2026-08-03T11:50:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30811080508 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Genesis System3 Global Safety CI | 30845368212 | in_progress | 2026-08-03T19:28:04Z |
| System3 Latest Truth Publish | 30845367968 | in_progress | 2026-08-03T19:21:01Z |

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
