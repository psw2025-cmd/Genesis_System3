# System3 GitHub + Render Failure TODO

Generated UTC: `2026-07-12T12:37:56.630197Z`
Status: **BLOCKED**
Repository: `psw2025-cmd/Genesis_System3`
Render base: `https://genesis-system3-backend.onrender.com`
GitHub failed workflows: `5`
Render failed endpoints: `9`
TODO count: `14`

## Rule

Every failed GitHub workflow and Render endpoint failure stays in this TODO until a later run proves PASS. Do not claim resolved from chat, logs, or file existence; dashboard visual proof is still required for final claims.

## TODO

- [ ] Fix GitHub workflow 'Genesis System3 Global Safety CI' run=29192720288 conclusion=failure commit=cdc00d894f00
- [ ] Fix GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=29192720073 conclusion=failure commit=cdc00d894f00
- [ ] Fix GitHub workflow 'System3 GitHub Render Failure Tracker' run=29192708869 conclusion=failure commit=4986f22102b5
- [ ] Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29192708858 conclusion=failure commit=4986f22102b5
- [ ] Fix GitHub workflow 'System3 Experimental Solution Planner' run=29192708838 conclusion=failure commit=4986f22102b5
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
| Genesis System3 Global Safety CI | 29192720288 | failure | `cdc00d894f00` | 2026-07-12T12:30:29Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29192720288 |
| .github/workflows/options-ml-training-proof.yml | 29192720073 | failure | `cdc00d894f00` | 2026-07-12T12:29:56Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29192720073 |
| System3 GitHub Render Failure Tracker | 29192708869 | failure | `4986f22102b5` | 2026-07-12T12:37:01Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29192708869 |
| System3 Secure Install Credential Audit | 29192708858 | failure | `4986f22102b5` | 2026-07-12T12:37:12Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29192708858 |
| System3 Experimental Solution Planner | 29192708838 | failure | `4986f22102b5` | 2026-07-12T12:37:02Z | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29192708838 |

## Render endpoint failures

| Endpoint | Status | Reason | Sample |
|---|---:|---|---|
| `/api/state` | 401 | HTTP status 401 | `{"detail":"Missing or invalid dashboard API session"}` |
| `/api/deploy/info` | 401 | HTTP status 401 | `{"detail":"Missing or invalid dashboard API session"}` |
| `/api/broker/diagnose` | 401 | HTTP status 401 | `{"detail":"Missing or invalid dashboard API session"}` |
| `/api/broker/funds` | 401 | HTTP status 401 | `{"detail":"Missing or invalid dashboard API session"}` |
| `/api/broker/holdings` | 401 | HTTP status 401 | `{"detail":"Missing or invalid dashboard API session"}` |
| `/api/broker/positions/live` | 401 | HTTP status 401 | `{"detail":"Missing or invalid dashboard API session"}` |
| `/api/scanner/top_contract_gainers` | 401 | HTTP status 401 | `{"detail":"Missing or invalid dashboard API session"}` |
| `/api/paper` | 401 | HTTP status 401 | `{"detail":"Missing or invalid dashboard API session"}` |
| `/api/ml/performance` | 401 | HTTP status 401 | `{"detail":"Missing or invalid dashboard API session"}` |
