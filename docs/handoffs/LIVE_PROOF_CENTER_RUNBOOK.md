# Live Proof Center — Runbook addendum

**Marker:** use with `docs/handoffs/SYSTEM3_MASTER_AUTOMATION_RUNBOOK.md`  
**Updated:** 2026-08-26

## Always-on agent proof (solves multi-agent access blindness)

| Item | Value |
|---|---|
| Script | `scripts/system3_live_proof_center.py` |
| Workflow | `.github/workflows/live-proof-center.yml` |
| Cron | `20 */2 * * *` (every 2h UTC) + `workflow_dispatch` |
| Pack | `reports/latest/live_proof_center/LATEST/` |
| Excel | `System3_LIVE_PROOF_CENTER.xlsx` (12 forensic sheets + README) |
| Pointer | `reports/coordination/LIVE_PROOF_CENTER_POINTER.md` |
| Branch mirror | `live-proof-center` (force-updated each run) |
| Doc | `docs/handoffs/LIVE_PROOF_CENTER.md` |

### Hard bans

| Ban | Why |
|---|---|
| Claim “no access to GCP/dashboard” without reading Live Proof Center | Pack is published on GitHub for all agents |
| Treat HTTP 22/22 tab mounts as semantic PASS | Pack marks semantic_proof=NOT_PROVEN |
| Expect Excel missing on GitHub | gitignore allowlists proof-center xlsx |
| Blind redeploy because proof workflow ran | reports/** does not trigger Auto Deploy |

### Operator action

Actions → **Live Proof Center (GCP + Dashboard MRI)** → Run workflow (after merge).
