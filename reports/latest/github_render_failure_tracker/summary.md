# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-03T20:31:08.436848Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `13`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `25`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Latest Truth Publish' run=30849643271 conclusion=failure commit=dc6589d15396
- [ ] Fix latest GitHub workflow 'Permanent Repo Render Safety' run=30849641954 conclusion=failure commit=dc6589d15396
- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=30849641964 conclusion=failure commit=dc6589d15396
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30849641578 conclusion=failure commit=dc6589d15396
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30849641842 conclusion=failure commit=dc6589d15396
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=30849641883 conclusion=failure commit=dc6589d15396
- [ ] Fix latest GitHub workflow 'Dashboard Live UI Proof' run=30849642276 conclusion=failure commit=dc6589d15396
- [ ] Fix latest GitHub workflow 'System3 Parallel Root-Cause Audit' run=30849641875 conclusion=failure commit=dc6589d15396
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30849640128 conclusion=failure commit=dc6589d15396
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30847599319 conclusion=failure commit=09ee4fae0d6f
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30847753059 conclusion=failure commit=3adbfc7f5d38
- [ ] Fix latest GitHub workflow 'Dashboard Visual Contract Check' run=30845368512 conclusion=failure commit=7d317001e66e
- [ ] Fix latest GitHub workflow 'Dhan Only Data Truth Proof' run=30845368220 conclusion=failure commit=7d317001e66e
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
| System3 Latest Truth Publish | 30849643271 | failure | `dc6589d15396` | 2026-08-03T20:30:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30849643271 |
| Permanent Repo Render Safety | 30849641954 | failure | `dc6589d15396` | 2026-08-03T20:28:19Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30849641954 |
| Genesis System3 Global Safety CI | 30849641964 | failure | `dc6589d15396` | 2026-08-03T20:26:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30849641964 |
| Dashboard Visual Production Proof | 30849641578 | failure | `dc6589d15396` | 2026-08-03T20:22:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30849641578 |
| Dashboard Visible Proof Warmed | 30849641842 | failure | `dc6589d15396` | 2026-08-03T20:19:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30849641842 |
| Dashboard Visible Proof Isolated | 30849641883 | failure | `dc6589d15396` | 2026-08-03T20:19:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30849641883 |
| Dashboard Live UI Proof | 30849642276 | failure | `dc6589d15396` | 2026-08-03T20:19:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30849642276 |
| System3 Parallel Root-Cause Audit | 30849641875 | failure | `dc6589d15396` | 2026-08-03T20:19:16Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30849641875 |
| .github/workflows/options-ml-training-proof.yml | 30849640128 | failure | `dc6589d15396` | 2026-08-03T20:18:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30849640128 |
| Dashboard Deploy Provenance Gate | 30847599319 | failure | `09ee4fae0d6f` | 2026-08-03T19:55:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30847599319 |
| System3 Backend Live Simulation Proof | 30847753059 | failure | `3adbfc7f5d38` | 2026-08-03T19:54:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30847753059 |
| Dashboard Visual Contract Check | 30845368512 | failure | `7d317001e66e` | 2026-08-03T19:21:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368512 |
| Dhan Only Data Truth Proof | 30845368220 | failure | `7d317001e66e` | 2026-08-03T19:21:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30845368220 |

## Pending workflow runs

No queued or in-progress workflow runs in the latest query.

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
