# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-13T13:16:21.189917Z`
Status: **BLOCKED**
Tracker internal status: **PASS**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
Excluded workflows: `System3 GitHub Render Failure Tracker`
GitHub failed workflows: `9`
Render failed endpoints: `9`
TODO count: `18`

## Rule

Every failed GitHub workflow and Render endpoint failure stays in this TODO until a later run proves PASS. The tracker is report-only and must not create a self-failure storm. Dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29252920225 conclusion=cancelled commit=c9c2b8959a46
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=29252766022 conclusion=cancelled commit=c9c2b8959a46
- [ ] Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29252763238 conclusion=cancelled commit=c9c2b8959a46
- [ ] Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29252761114 conclusion=cancelled commit=c9c2b8959a46
- [ ] Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29252752825 conclusion=cancelled commit=c9c2b8959a46
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=29252687933 conclusion=cancelled commit=c9c2b8959a46
- [ ] Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29252684588 conclusion=cancelled commit=c9c2b8959a46
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=29252632715 conclusion=cancelled commit=c9c2b8959a46
- [ ] Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=29252632028 conclusion=cancelled commit=c9c2b8959a46
- [ ] Fix Render endpoint /api/state: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/deploy/info: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/diagnose: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/funds: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/holdings: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/broker/positions/live: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/paper: HTTP status 401 status=401
- [ ] Fix Render endpoint /api/ml/performance: HTTP status 401 status=401

## GitHub workflow failures

| Workflow | Run | Conclusion | Commit | Updated | Link |
|---|---:|---|---|---|---|
| Dashboard Visible Issue Tracker | 29252920225 | cancelled | `c9c2b8959a46` | 2026-07-13T13:15:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29252920225 |
| System3 1000 Point TODO Status Updater | 29252766022 | cancelled | `c9c2b8959a46` | 2026-07-13T13:13:22Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29252766022 |
| Dashboard Visible Issue Tracker | 29252763238 | cancelled | `c9c2b8959a46` | 2026-07-13T13:13:17Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29252763238 |
| Dashboard Visible Issue Tracker | 29252761114 | cancelled | `c9c2b8959a46` | 2026-07-13T13:11:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29252761114 |
| Dashboard Visible Issue Tracker | 29252752825 | cancelled | `c9c2b8959a46` | 2026-07-13T13:11:00Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29252752825 |
| System3 1000 Point TODO Status Updater | 29252687933 | cancelled | `c9c2b8959a46` | 2026-07-13T13:11:04Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29252687933 |
| Dashboard Visible Issue Tracker | 29252684588 | cancelled | `c9c2b8959a46` | 2026-07-13T13:10:53Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29252684588 |
| System3 1000 Point TODO Status Updater | 29252632715 | cancelled | `c9c2b8959a46` | 2026-07-13T13:10:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29252632715 |
| System3 1000 Point TODO Status Updater | 29252632028 | cancelled | `c9c2b8959a46` | 2026-07-13T13:09:11Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29252632028 |

## Render endpoint failures

| Endpoint | Status | Reason | Classification |
|---|---:|---|---|
| `/api/state` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/deploy/info` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/diagnose` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/funds` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/holdings` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/broker/positions/live` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/scanner/top_contract_gainers` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/paper` | 401 | HTTP status 401 | `mentions_auth_error` |
| `/api/ml/performance` | 401 | HTTP status 401 | `mentions_auth_error` |
