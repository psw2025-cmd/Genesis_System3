# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-26T14:31:38.780046Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `http://127.0.0.1:8000`
GitHub workflows whose newest observed run failed: `19`
GitHub workflows currently queued/in progress: `0`
Render failed endpoints: `12`
TODO count: `31`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=30206152335 conclusion=failure commit=62bdf022ed96
- [ ] Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=30206169185 conclusion=failure commit=31c7f55f9ccd
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30206168188 conclusion=failure commit=31c7f55f9ccd
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30204820023 conclusion=failure commit=ebf552ee744e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Warmed' run=30205003852 conclusion=failure commit=62bdf022ed96
- [ ] Fix latest GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30204959227 conclusion=failure commit=03922fd012a4
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30204990962 conclusion=failure commit=62bdf022ed96
- [ ] Fix latest GitHub workflow 'System3 Backend Live Simulation Proof' run=30204961709 conclusion=failure commit=03922fd012a4
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=30204923805 conclusion=failure commit=8cff209f72df
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=30204904245 conclusion=failure commit=6cc20c76fdda
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=30204919061 conclusion=failure commit=8cff209f72df
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=30204934943 conclusion=failure commit=00c53340a192
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=30204919036 conclusion=failure commit=8cff209f72df
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=30204904264 conclusion=failure commit=6cc20c76fdda
- [ ] Fix latest GitHub workflow 'System3 Workflow Failure Tracker' run=30204881654 conclusion=failure commit=9506a91bb38e
- [ ] Fix latest GitHub workflow 'System3 Render Worker Preflight' run=30204877999 conclusion=failure commit=ebf552ee744e
- [ ] Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=30204864760 conclusion=failure commit=ebf552ee744e
- [ ] Fix latest GitHub workflow 'Dashboard Visual Production Proof' run=30204846257 conclusion=failure commit=ebf552ee744e
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=30204803283 conclusion=failure commit=ebf552ee744e
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
| System3 Safe Repair Runner | 30206152335 | failure | `62bdf022ed96` | 2026-07-26T14:30:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30206152335 |
| Genesis System3 Global Safety CI | 30206169185 | failure | `31c7f55f9ccd` | 2026-07-26T14:29:36Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30206169185 |
| .github/workflows/options-ml-training-proof.yml | 30206168188 | failure | `31c7f55f9ccd` | 2026-07-26T14:29:05Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30206168188 |
| System3 Windows Self-Hosted Full Proof | 30204820023 | failure | `ebf552ee744e` | 2026-07-26T13:56:45Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204820023 |
| Dashboard Visible Proof Warmed | 30205003852 | failure | `62bdf022ed96` | 2026-07-26T13:55:39Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30205003852 |
| Dashboard Visible Auth-Resilient Proof | 30204959227 | failure | `03922fd012a4` | 2026-07-26T13:54:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204959227 |
| Dashboard Visual Proof Strict Gate | 30204990962 | failure | `62bdf022ed96` | 2026-07-26T13:54:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204990962 |
| System3 Backend Live Simulation Proof | 30204961709 | failure | `03922fd012a4` | 2026-07-26T13:53:57Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204961709 |
| Dashboard Visible Issue Tracker | 30204923805 | failure | `8cff209f72df` | 2026-07-26T13:53:35Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204923805 |
| Dashboard Shell Diagnostic | 30204904245 | failure | `6cc20c76fdda` | 2026-07-26T13:53:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204904245 |
| System3 Autopilot Proof Board | 30204919061 | failure | `8cff209f72df` | 2026-07-26T13:53:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204919061 |
| System3 Experimental Solution Planner | 30204934943 | failure | `00c53340a192` | 2026-07-26T13:52:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204934943 |
| System3 Secure Install Credential Audit | 30204919036 | failure | `8cff209f72df` | 2026-07-26T13:52:38Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204919036 |
| Dashboard Visual Loading Postflight | 30204904264 | failure | `6cc20c76fdda` | 2026-07-26T13:52:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204904264 |
| System3 Workflow Failure Tracker | 30204881654 | failure | `9506a91bb38e` | 2026-07-26T13:51:24Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204881654 |
| System3 Render Worker Preflight | 30204877999 | failure | `ebf552ee744e` | 2026-07-26T13:51:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204877999 |
| Dashboard Deploy Provenance Gate | 30204864760 | failure | `ebf552ee744e` | 2026-07-26T13:51:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204864760 |
| Dashboard Visual Production Proof | 30204846257 | failure | `ebf552ee744e` | 2026-07-26T13:51:07Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204846257 |
| Dashboard Visible Settle Proof | 30204803283 | failure | `ebf552ee744e` | 2026-07-26T13:49:15Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/30204803283 |

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
