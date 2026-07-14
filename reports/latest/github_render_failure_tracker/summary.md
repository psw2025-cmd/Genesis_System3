# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-14T23:19:29.842564Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `3`
Render failed endpoints: `1`
TODO count: `8`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'System3 Secure Install Credential Audit' run=29375768651 conclusion=failure commit=78152681e736
- [ ] Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29375768639 conclusion=failure commit=78152681e736
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29375062779 conclusion=failure commit=38243d16f132
- [ ] Fix latest GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29375180757 conclusion=failure commit=38243d16f132
- [ ] Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29374545113 conclusion=failure commit=4402d5390b01
- [ ] Fix latest GitHub workflow 'Dashboard Shell Diagnostic' run=29374659447 conclusion=failure commit=664b04005410
- [ ] Fix latest GitHub workflow 'Dashboard Visual Loading Postflight' run=29374659591 conclusion=failure commit=664b04005410
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| System3 Secure Install Credential Audit | 29375768651 | failure | `78152681e736` | 2026-07-14T23:19:26Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29375768651 |
| System3 Experimental Solution Planner | 29375768639 | failure | `78152681e736` | 2026-07-14T23:19:18Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29375768639 |
| System3 Windows Self-Hosted Full Proof | 29375062779 | failure | `38243d16f132` | 2026-07-14T23:10:44Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29375062779 |
| Dashboard Visual Proof Strict Gate | 29375180757 | failure | `38243d16f132` | 2026-07-14T23:07:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29375180757 |
| Dashboard Visible Issue Tracker | 29374545113 | failure | `4402d5390b01` | 2026-07-14T23:00:54Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29374545113 |
| Dashboard Shell Diagnostic | 29374659447 | failure | `664b04005410` | 2026-07-14T23:00:34Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29374659447 |
| Dashboard Visual Loading Postflight | 29374659591 | failure | `664b04005410` | 2026-07-14T22:57:50Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29374659591 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| System3 Autopilot Proof Board | 29375784190 | queued | 2026-07-14T23:19:28Z |
| System3 1000 Point TODO Status Updater | 29375768641 | in_progress | 2026-07-14T23:19:13Z |
| System3 Safe Repair Runner | 29375630085 | in_progress | 2026-07-14T23:16:27Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/scanner/top_contract_gainers` | 0 | HTTP status 0 | `none` |
