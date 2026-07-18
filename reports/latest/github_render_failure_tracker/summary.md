# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-18T04:58:24.721265Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `12`
GitHub workflows currently queued/in progress: `1`
Render failed endpoints: `12`
TODO count: `24`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29630716348 conclusion=failure commit=285e015bb648
- [ ] Fix latest GitHub workflow 'System3 Safe Repair Runner' run=29631007076 conclusion=failure commit=ab92b868bd63
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29631007041 conclusion=failure commit=ab92b868bd63
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29630915709 conclusion=failure commit=210e078d202f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Settle Proof' run=29630903168 conclusion=failure commit=210e078d202f
- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Current' run=29630722555 conclusion=failure commit=c67326dfbe32
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29631022370 conclusion=failure commit=8e3995469d8d
- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29631007040 conclusion=failure commit=ab92b868bd63
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29631007033 conclusion=failure commit=ab92b868bd63
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29631007069 conclusion=failure commit=ab92b868bd63
- [ ] Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29630698249 conclusion=failure commit=630ac25b5cde
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=29630608793 conclusion=failure commit=dfbd655d76d2
- [ ] Fix Render endpoint /: HTTP status 502 status=502
- [ ] Fix Render endpoint /ui/: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/health: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/state: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/paper: HTTP status 502 status=502
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 502 status=502

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Visible Issue Tracker | 29630716348 | failure | `285e015bb648` | 2026-07-18T04:54:46Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29630716348 |
| System3 Safe Repair Runner | 29631007076 | failure | `ab92b868bd63` | 2026-07-18T04:51:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29631007076 |
| Dashboard Shell Diagnostic | 29631007041 | failure | `ab92b868bd63` | 2026-07-18T04:45:49Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29631007041 |
| System3 Windows Self-Hosted Full Proof | 29630915709 | failure | `210e078d202f` | 2026-07-18T04:45:33Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29630915709 |
| Dashboard Visible Settle Proof | 29630903168 | failure | `210e078d202f` | 2026-07-18T04:45:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29630903168 |
| Dashboard Visible Proof Current | 29630722555 | failure | `c67326dfbe32` | 2026-07-18T04:44:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29630722555 |
| Dashboard Visual Proof Strict Gate | 29631022370 | failure | `8e3995469d8d` | 2026-07-18T04:43:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29631022370 |
| System3 Secure Install Credential Audit | 29631007040 | failure | `ab92b868bd63` | 2026-07-18T04:43:03Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29631007040 |
| System3 Experimental Solution Planner | 29631007033 | failure | `ab92b868bd63` | 2026-07-18T04:42:55Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29631007033 |
| Dashboard Visual Loading Postflight | 29631007069 | failure | `ab92b868bd63` | 2026-07-18T04:42:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29631007069 |
| System3 Autopilot Proof Board | 29630698249 | failure | `630ac25b5cde` | 2026-07-18T04:32:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29630698249 |
| System3 Windows Self-Hosted Workflow Migration | 29630608793 | failure | `dfbd655d76d2` | 2026-07-18T04:29:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29630608793 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Dashboard Visible Auth-Resilient Proof | 29631039525 | in_progress | 2026-07-18T04:44:00Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 502 | HTTP status 502 | `none` |
| `/ui/` | 502 | HTTP status 502 | `none` |
| `/api/health` | 502 | HTTP status 502 | `none` |
| `/api/state` | 502 | HTTP status 502 | `none` |
| `/api/deploy/info` | 502 | HTTP status 502 | `none` |
| `/api/broker/diagnose` | 502 | HTTP status 502 | `none` |
| `/api/broker/funds` | 502 | HTTP status 502 | `none` |
| `/api/broker/holdings` | 502 | HTTP status 502 | `none` |
| `/api/broker/positions/live` | 502 | HTTP status 502 | `none` |
| `/api/scanner/top_contract_gainers` | 502 | HTTP status 502 | `none` |
| `/api/paper` | 502 | HTTP status 502 | `none` |
| `/api/ml/performance` | 502 | HTTP status 502 | `none` |
