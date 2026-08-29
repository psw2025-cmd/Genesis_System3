## SYSTEM3_COORDINATION_V1 — RHUI V2.2 material change (multi-verify)

**Overall:** NOT_ACCEPTED · **HUMAN_ACTION_REQUIRED:** NO

### Cross-verify
| Plane | Value |
|---|---|
| GitHub `origin/main` | `fb4772f9d52b67a31b55ee85aab8604e525bbad6` (#367) |
| GCP serving | exact same SHA · `genesis-system3-web-00617-vif` @ 100% |
| Laptop | NON-AUTH (`146eb69…` branch) — ignore for PASS |
| Deploy run | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/32923767070 (deploy PASS; control-plane severity predicate red) |

### Multi-verify delta (market open ~11:50 IST)
- Broker same-session: **PASS** `connected=true` AUTH_OK v320 · LIVE OFF · orders OFF
- 4/4 chains API: **PASS** `required_symbols_ready=true` (NIFTY/BN/FN/MID populated, stale=false) — clears earlier pre-market NOT READY
- `/api/health` ↔ `/api/state` QC: both **NOT_READY** (converged; no false-green PASS)
- Scheduler: **FAIL** `alert_severity=warning` — **attributed** to `genesis-system3-signals` stale beyond cadence grace (collector/contract OK; not Dhan auth)
- #367 effectiveness: **PENDING** until genuine **18:45 IST** signals run
- 22-tab visual PASS ≠ semantic API↔UI (**NOT_PROVEN**)
- 60-min stability: **NOT_PROVEN**

### Artifacts (agents read these)
- `docs/handoffs/RHUI_V2.2_MATERIAL_CHANGE.md`
- `docs/RUHI_RULE_V2.md` §0 acceptance lock
- `docs/handoffs/SYSTEM3_MASTER_AUTOMATION_RUNBOOK.md` §0A + Hard bans / Live mistakes
- `reports/coordination/RHUI_V2.2_GATE_BOARD.csv`
- `reports/coordination/RHUI_V2.2_Verification_Checklist.json`
- `reports/coordination/COMMAND_CENTER.md`
- Ledger: RUHI-023..026 (B003)
- Status image: `reports/coordination/RHUI_V2.2_Material_Change_Status.png`

### Agent agreement
- **Cursor:** keep pin on 00617-vif; no blind redeploy/token/IAM/LIVE
- **Claude:** adversarial verify signals-stale attribution + post-18:45 #367 logs
- **ChatGPT:** reconcile mail/ledger to this SSOT; do not claim ACCEPTED from visual 22/22

### Next
1. 18:45 IST observe post-#367 signals execution
2. Re-GET `/api/scheduler/health` for severity=none only with evidence
3. Semantic continuous session (API↔UI)
4. Only then 60-min stability
