# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-14T21:22:10.237223Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `6`
GitHub workflows currently queued/in progress: `4`
Render failed endpoints: `1`
TODO count: `7`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29369248907 conclusion=failure commit=e17654d0a474
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29368364220 conclusion=failure commit=d37330e5e152
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29368174220 conclusion=failure commit=64299c679b65
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29368491164 conclusion=failure commit=d85a5762ced5
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29368324170 conclusion=failure commit=901aad25b95b
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29368324117 conclusion=failure commit=901aad25b95b
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Experimental Solution Planner | 29369248907 | failure | `e17654d0a474` | 2026-07-14T21:22:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29369248907 |
| System3 Windows Self-Hosted Full Proof | 29368364220 | failure | `d37330e5e152` | 2026-07-14T21:16:23Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29368364220 |
| Dashboard Visible Issue Tracker | 29368174220 | failure | `64299c679b65` | 2026-07-14T21:10:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29368174220 |
| Dashboard Visual Proof Strict Gate | 29368491164 | failure | `d85a5762ced5` | 2026-07-14T21:09:43Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29368491164 |
| Dashboard Shell Diagnostic | 29368324170 | failure | `901aad25b95b` | 2026-07-14T21:08:28Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29368324170 |
| Dashboard Visual Loading Postflight | 29368324117 | failure | `901aad25b95b` | 2026-07-14T21:07:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29368324117 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Secure Install Credential Audit | 29369248664 | in_progress | 2026-07-14T21:21:58Z |
| System3 1000 Point TODO Status Updater | 29369248463 | in_progress | 2026-07-14T21:21:58Z |
| System3 Autopilot Proof Board | 29369248404 | in_progress | 2026-07-14T21:21:58Z |
| System3 Safe Repair Runner | 29369036235 | in_progress | 2026-07-14T21:18:55Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
