# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T16:21:20.982568Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `15`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `27`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30210083810 conclusion=failure commit=a56b28d1a1a9
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30209712334 conclusion=failure commit=a56b28d1a1a9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30209833211 conclusion=failure commit=a56b28d1a1a9
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30209813231 conclusion=failure commit=a56b28d1a1a9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30209644948 conclusion=failure commit=a56b28d1a1a9
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30209271523 conclusion=failure commit=8025812a6510
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30209283461 conclusion=failure commit=81cf157edba9
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30209293084 conclusion=failure commit=2ace0c4723ed
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30209283455 conclusion=failure commit=81cf157edba9
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30209271526 conclusion=failure commit=8025812a6510
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30209249282 conclusion=failure commit=8c769aa28227
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30209271502 conclusion=failure commit=8025812a6510
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30208796577 conclusion=failure commit=ae8ff11b96c8
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30208770681 conclusion=failure commit=ae8ff11b96c8
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30208691657 conclusion=failure commit=afd19684eb4a
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
| System3 Safe Repair Runner | 30210083810 | failure | `a56b28d1a1a9` | 2026-07-26T16:19:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30210083810 |
| System3 Windows Self-Hosted Full Proof | 30209712334 | failure | `a56b28d1a1a9` | 2026-07-26T16:18:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30209712334 |
| Dashboard Visible Auth-Resilient Proof | 30209833211 | failure | `a56b28d1a1a9` | 2026-07-26T16:12:13Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30209833211 |
| Dashboard Visual Proof Strict Gate | 30209813231 | failure | `a56b28d1a1a9` | 2026-07-26T16:10:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30209813231 |
| Dashboard Visible Settle Proof | 30209644948 | failure | `a56b28d1a1a9` | 2026-07-26T16:06:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30209644948 |
| Dashboard Shell Diagnostic | 30209271523 | failure | `8025812a6510` | 2026-07-26T15:57:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30209271523 |
| Dashboard Visible Issue Tracker | 30209283461 | failure | `81cf157edba9` | 2026-07-26T15:57:30Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30209283461 |
| Dashboard Visible Proof Current | 30209293084 | failure | `2ace0c4723ed` | 2026-07-26T15:57:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30209293084 |
| System3 Experimental Solution Planner | 30209283455 | failure | `81cf157edba9` | 2026-07-26T15:56:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30209283455 |
| System3 Secure Install Credential Audit | 30209271526 | failure | `8025812a6510` | 2026-07-26T15:56:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30209271526 |
| System3 Autopilot Proof Board | 30209249282 | failure | `8c769aa28227` | 2026-07-26T15:56:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30209249282 |
| Dashboard Visual Loading Postflight | 30209271502 | failure | `8025812a6510` | 2026-07-26T15:56:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30209271502 |
| Dashboard Visible Proof Warmed | 30208796577 | failure | `ae8ff11b96c8` | 2026-07-26T15:43:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30208796577 |
| System3 Backend Live Simulation Proof | 30208770681 | failure | `ae8ff11b96c8` | 2026-07-26T15:42:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30208770681 |
| System3 Render Worker Preflight | 30208691657 | failure | `afd19684eb4a` | 2026-07-26T15:40:20Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30208691657 |

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
