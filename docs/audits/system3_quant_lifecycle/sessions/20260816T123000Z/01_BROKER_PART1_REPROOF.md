# 01 — PART 1 Broker tasks re-proof (instruction lines 1–69)

**Instruction:** `docs/chatgpt_instruction_for_cursar_2.md` (4:53 PM IST executor block)  
**Re-proof time:** 2026-08-16 ~18:00 IST / live API capture in `supporting/`

## Verdict: **PASS** (already implemented earlier today; re-verified)

| Task | Required | Live / GitHub evidence | Status |
|------|----------|------------------------|--------|
| 1 Secret cleanup | Disable `system3-dhan-access-token`, `DHAN_BROKER_TOKEN`; keep `dhan-access-token`; label quarantine | Quarantine labels applied; versions disabled; canonical **v259** ENABLED | **PASS** |
| 2 `docs/BROKER_SETUP.md` | Canonical policy | On `main` via PR #244 / #245 | **PASS** |
| 3 `infra/rotate-job.yaml` | Mutex Job contract | On `main` (documents sole Job + Pub/Sub topic) | **PASS** |
| 4 Auto-heal on DH-906 | Hot-reload via Job invoke | `cloud_runtime_patch.py` + deploy env `SELF_HEAL=1`, cooldown 900s | **PASS** |
| 5 Cloud Run env | `DHAN_ACCESS_TOKEN_SECRET_ID=dhan-access-token` | Live service asia-south1 | **PASS** |
| 6 Live verify | connected=true; no Auth issue | `/api/broker/status` **connected=true** secret **259**; LIVE=false | **PASS** |
| 7 FINAL_REPORT | Audit report | `reports/latest/broker_secret_dup_audit_20260816/FINAL_REPORT.md` | **PASS** |

### LIVE URL VERIFY (this re-proof)
- `connected`: **true**
- `secret_version`: **259**
- `live_trading_enabled`: **false**
- Serving SHA (API): `997daef4cfb3322e317da69b5cbb5b69950dab26`

### Note
Screenshot ~17:04 IST Auth issue was **pre-v259 remint**; see `docs/incidents/BROKER_AUTH_20260816_IST.md`. Storage Insights NHLVNDD remains **UNRELATED**.
