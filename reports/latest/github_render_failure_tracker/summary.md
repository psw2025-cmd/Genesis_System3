# System3 GitHub + Render Failure TODO

Generated UTC: `2026-08-06T05:08:41.563296Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
GitHub workflows whose newest observed run failed: `7`
GitHub workflows currently queued/in progress: `7`
Render failed endpoints: `12`
TODO count: `19`

## Rule

Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix latest GitHub workflow 'Dashboard Visible Proof Isolated' run=31073017980 conclusion=failure commit=752ecf2bb477
- [ ] Fix latest GitHub workflow 'Dhan Only Data Truth Proof' run=31073018007 conclusion=failure commit=752ecf2bb477
- [ ] Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31073017568 conclusion=failure commit=752ecf2bb477
- [ ] Fix latest GitHub workflow 'System3 Market Session Proof Runner' run=31072377770 conclusion=failure commit=380f04d7971d
- [ ] Fix latest GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=31071564183 conclusion=failure commit=7383995be877
- [ ] Fix latest GitHub workflow 'System3 Broker Chain Semantic Gate' run=31070786177 conclusion=failure commit=9b2e1cb3f646
- [ ] Fix latest GitHub workflow 'System3 Full Auto Truth' run=31070258869 conclusion=failure commit=9b2e1cb3f646
- [ ] Fix Render endpoint /: HTTP status 0 status=0
- [ ] Fix Render endpoint /ui/: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/health: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/state: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/paper: HTTP status 0 status=0
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 0 status=0

## Latest failed run per workflow

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Visible Proof Isolated | 31073017980 | failure | `752ecf2bb477` | 2026-08-06T05:06:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31073017980 |
| Dhan Only Data Truth Proof | 31073018007 | failure | `752ecf2bb477` | 2026-08-06T05:04:25Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31073018007 |
| .github/workflows/options-ml-training-proof.yml | 31073017568 | failure | `752ecf2bb477` | 2026-08-06T05:03:58Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31073017568 |
| System3 Market Session Proof Runner | 31072377770 | failure | `380f04d7971d` | 2026-08-06T04:54:41Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31072377770 |
| System3 Windows Self-Hosted Workflow Migration | 31071564183 | failure | `7383995be877` | 2026-08-06T04:35:09Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31071564183 |
| System3 Broker Chain Semantic Gate | 31070786177 | failure | `9b2e1cb3f646` | 2026-08-06T04:20:47Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31070786177 |
| System3 Full Auto Truth | 31070258869 | failure | `9b2e1cb3f646` | 2026-08-06T04:12:42Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31070258869 |

## Pending workflow runs

| Workflow | Run | Status | Updated |
|---|---:|---|---|
| Genesis System3 Global Safety CI | 31073018004 | in_progress | 2026-08-06T05:07:24Z |
| Dashboard Visible Proof Warmed | 31073018034 | in_progress | 2026-08-06T05:04:08Z |
| Dashboard Live UI Proof | 31073018002 | in_progress | 2026-08-06T05:04:08Z |
| Permanent Repo Render Safety | 31073017996 | in_progress | 2026-08-06T05:04:08Z |
| System3 Latest Truth Publish | 31073017971 | in_progress | 2026-08-06T05:04:07Z |
| Cloud Runtime Check | 31073018037 | in_progress | 2026-08-06T05:04:03Z |
| Dashboard Visual Production Proof | 31073018035 | in_progress | 2026-08-06T05:04:02Z |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/` | 0 | HTTP status 0 | `none` |
| `/ui/` | 0 | HTTP status 0 | `none` |
| `/api/health` | 0 | HTTP status 0 | `none` |
| `/api/state` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/deploy/info` | 0 | HTTP status 0 | `none` |
| `/api/broker/diagnose` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/funds` | 0 | HTTP status 0 | `none` |
| `/api/broker/holdings` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/positions/live` | 0 | HTTP status 0 | `none` |
| `/api/scanner/top_contract_gainers` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/paper` | 0 | HTTP status 0 | `none` |
| `/api/ml/performance` | 0 | HTTP status 0 | `none` |
