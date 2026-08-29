# Live Proof Center — agent access (no laptop / gcloud required)

**Status:** ACTIVE when merged  
**Workflow:** `.github/workflows/live-proof-center.yml`  
**Schedule:** every 2 hours UTC (`20 */2 * * *`) + manual `workflow_dispatch`  
**Pack:** `reports/latest/live_proof_center/LATEST/`  
**Pointer:** `reports/coordination/LIVE_PROOF_CENTER_POINTER.md`  
**Always-on branch mirror:** `live-proof-center` (force-updated each run)

## Why this exists

Agents (ChatGPT / Claude / Cursor Cloud / Codex) repeatedly fail because they lack:

- laptop primary clone access  
- local `gcloud` / WIF  
- Dhan / Secret Manager value access  

This workflow publishes a **sanitized** live forensic MRI to GitHub so every agent shares one proof center.

## What it collects

1. Cross-verify: GitHub `origin/main` tip vs live `/api/deploy_info`  
2. Broker / token **metadata** (no values)  
3. Health ↔ state QC  
4. Option chains (4/4 slim)  
5. Scheduler observability  
6. Auto gates  
7. Full public API probe matrix  
8. All **22** dashboard tabs HTTP forensic (`/ui/?tab=…`)  
9. Frontend tab → backend API map  
10. GCP inventory via WIF (Cloud Run revision/traffic, jobs, scheduler, secret **names**)  
11. Gaps / blockers sheet  
12. Excel workbook `System3_LIVE_PROOF_CENTER.xlsx` (12 forensic sheets + README sheet)

## Safety (hard)

- No secret values / tokens / private keys  
- No LIVE enablement  
- No order / mutation API calls  
- Does **not** trigger Cloud Run Auto Deploy (reports paths excluded)

## Agent contract

Before claiming “no access” or inventing stale MRI:

1. Open `reports/coordination/LIVE_PROOF_CENTER_POINTER.md`  
2. Read `reports/latest/live_proof_center/LATEST/INDEX.md` + `MANIFEST.json`  
3. If main is behind, also read branch `live-proof-center`  
4. HTTP tab OK ≠ semantic acceptance  

## Local run

```bash
pip install openpyxl
python scripts/system3_live_proof_center.py
```

## Manual refresh

GitHub → Actions → **Live Proof Center (GCP + Dashboard MRI)** → Run workflow
