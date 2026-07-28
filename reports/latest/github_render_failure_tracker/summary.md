# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-28T01:33:18.869109Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `17`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `29`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30318608038 conclusion=failure commit=30a2096bc44e
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30318606627 conclusion=failure commit=30a2096bc44e
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30318546881 conclusion=failure commit=7d73a6c33498
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30318549692 conclusion=failure commit=7d73a6c33498
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30318511226 conclusion=failure commit=7d73a6c33498
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30316318294 conclusion=failure commit=dcd6da9169a4
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30316443824 conclusion=failure commit=dcd6da9169a4
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30316428933 conclusion=failure commit=dcd6da9169a4
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30316280635 conclusion=failure commit=dcd6da9169a4
- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30315700854 conclusion=failure commit=b38b57681ca2
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=30315779823 conclusion=failure commit=1ae05042d19a
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30315693812 conclusion=failure commit=b38b57681ca2
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30315700833 conclusion=failure commit=b38b57681ca2
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30315693878 conclusion=failure commit=b38b57681ca2
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30315662242 conclusion=failure commit=91896c76df08
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30315700871 conclusion=failure commit=b38b57681ca2
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30315693831 conclusion=failure commit=b38b57681ca2
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
| Dashboard Visible Proof Warmed | 30318608038 | failure | `30a2096bc44e` | 2026-07-28T00:53:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30318608038 |
| System3 Backend Live Simulation Proof | 30318606627 | failure | `30a2096bc44e` | 2026-07-28T00:52:51Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30318606627 |
| Dashboard Deploy Provenance Gate | 30318546881 | failure | `7d73a6c33498` | 2026-07-28T00:51:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30318546881 |
| System3 Render Worker Preflight | 30318549692 | failure | `7d73a6c33498` | 2026-07-28T00:51:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30318549692 |
| Dashboard Visual Production Proof | 30318511226 | failure | `7d73a6c33498` | 2026-07-28T00:51:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30318511226 |
| System3 Windows Self-Hosted Full Proof | 30316318294 | failure | `dcd6da9169a4` | 2026-07-28T00:29:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30316318294 |
| Dashboard Visible Auth-Resilient Proof | 30316443824 | failure | `dcd6da9169a4` | 2026-07-28T00:10:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30316443824 |
| Dashboard Visual Proof Strict Gate | 30316428933 | failure | `dcd6da9169a4` | 2026-07-28T00:09:06Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30316428933 |
| Dashboard Visible Settle Proof | 30316280635 | failure | `dcd6da9169a4` | 2026-07-28T00:06:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30316280635 |
| System3 Safe Repair Runner | 30315700854 | failure | `b38b57681ca2` | 2026-07-27T23:57:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30315700854 |
| Dashboard Visible Proof Current | 30315779823 | failure | `1ae05042d19a` | 2026-07-27T23:57:32Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30315779823 |
| Dashboard Shell Diagnostic | 30315693812 | failure | `b38b57681ca2` | 2026-07-27T23:57:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30315693812 |
| Dashboard Visible Issue Tracker | 30315700833 | failure | `b38b57681ca2` | 2026-07-27T23:56:31Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30315700833 |
| System3 Secure Install Credential Audit | 30315693878 | failure | `b38b57681ca2` | 2026-07-27T23:55:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30315693878 |
| System3 Autopilot Proof Board | 30315662242 | failure | `91896c76df08` | 2026-07-27T23:55:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30315662242 |
| System3 Experimental Solution Planner | 30315700871 | failure | `b38b57681ca2` | 2026-07-27T23:55:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30315700871 |
| Dashboard Visual Loading Postflight | 30315693831 | failure | `b38b57681ca2` | 2026-07-27T23:55:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30315693831 |

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
