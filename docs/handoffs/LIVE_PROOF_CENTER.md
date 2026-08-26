# Live Proof Center — agent access (no laptop / gcloud required)

**Status:** ACTIVE when merged  
**Workflow:** `.github/workflows/live-proof-center.yml`  
**Triggers:** `push` to `main` + `workflow_dispatch` (**no GitHub `schedule:`** — repo policy)  
**Pack:** `reports/latest/live_proof_center/LATEST/`  
**Pointer:** `reports/coordination/LIVE_PROOF_CENTER_POINTER.md`  
**Artifacts:** each Actions run uploads `live-proof-center-<run_id>` (30-day retention)

## Why this exists

Agents (ChatGPT / Claude / Cursor Cloud / Codex) repeatedly fail because they lack laptop / `gcloud` / Dhan access. This workflow publishes a **sanitized** live forensic MRI (Excel + JSON) so every agent can share one proof pack.

## Policy-compliant recurrence

GitHub Actions cron is **prohibited**. Refresh happens when:

1. Something merges to `main`, or  
2. Operator runs **Actions → Live Proof Center → Run workflow**, or  
3. (Optional later) GCP Cloud Scheduler calls GitHub `workflow_dispatch` via API — still no Actions `schedule:` block.

## What it collects

Public API matrix, 22 dashboard tab HTTP forensics, FE↔BE map, broker token **metadata**, QC, chains, scheduler obs, auto gates, GCP inventory (WIF), gaps sheet, Excel `System3_LIVE_PROOF_CENTER.xlsx`.

## Safety

- `contents: read` only — no repo write-back / no issue spam  
- Keyless WIF inventory + public HTTP probes  
- No secret values, no LIVE, no orders  
- Bandit-safe: `gcloud` via argv only (`shell=False`)
