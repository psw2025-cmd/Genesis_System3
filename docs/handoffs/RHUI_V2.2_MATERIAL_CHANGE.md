# RHUI V2.2 — Material change detected

**Status:** `NOT_ACCEPTED`  
**Rule:** `docs/RUHI_RULE_V2.md` (RHUI_RULE_V2.2)  
**Captured:** 2026-08-26 ~13:37–13:40 IST (cross-verify #3) · prior multi-verify #2 ~11:50 IST  
**HUMAN_ACTION_REQUIRED:** NO (no token/IAM/LIVE/order work)

## Cross-verify (GitHub × Cloud × Laptop)

| Plane | Value | Authority |
|---|---|---|
| GitHub `origin/main` | `afd28722e25d3e66c894c2fc6487722c698a1206` (#365 docs/tools) | YES (code history) |
| GCP serving (runtime) | `fb4772f9d52b67a31b55ee85aab8604e525bbad6` (#367) · `00617-vif` · 100% | YES (serving) |
| Classification | **DOCS_ONLY_LAG** — Auto Deploy skipped #365 path-filter | — |
| Laptop HEAD | `146eb69…` / `fix/p0-188…` | NO — non-auth |
| Banned workspace | `C:\System3\Genesis_System3` | NEVER edit |

Evidence: `reports/latest/rhui_v22_verify/cross_verify_20260826T080731Z/` + `reports/latest/repo_path_audit/cloud_github_vs_laptop.json`

## Gate board (after multi-verify)

| Gate | State |
|---|---|
| Runtime serving pin (#367) | PASS (`fb4772f9` / `00617-vif` @ 100%) |
| Main tip vs serving | **DOCS_ONLY_LAG** (`afd28722` #365 — no Auto Deploy) |
| Broker same-session | PASS (`AUTH_OK`, LIVE OFF) |
| 4/4 chains API | PASS (`required_symbols_ready=true`) |
| health ↔ state QC | PASS_BOTH_NOT_READY (converged; not false-green) |
| Scheduler health | FAIL — `alert_severity=warning` from **`genesis-system3-signals` stale** |
| #367 signals effectiveness | PENDING (18:45 IST) |
| 22-tab visual | PASS (historical on 00617) |
| 22-tab semantic | NOT_PROVEN |
| 60-min stability | NOT_PROVEN |
| **Overall** | **NOT_ACCEPTED** |

Machine SSOT: `reports/coordination/RHUI_V2.2_Verification_Checklist.json`  
CSV: `reports/coordination/RHUI_V2.2_GATE_BOARD.csv`  
Image: `reports/coordination/RHUI_V2.2_Material_Change_Status.png`

## Root causes (three domains)

1. **Prediction/ML** — signals raced NSE BhavCopy → HTTP 404. Fix #367 deployed; prove at scheduled run.  
2. **Scheduler severity** — `observability.alert_severity_none` fails because severity=`warning`; attributed to stale `genesis-system3-signals` (not Dhan auth).  
3. **Option-chain pre-market** — earlier fail-closed NOT READY; cleared on market-open recheck.

## Missing required (implement + document)

- Semantic 22-tab API↔UI parity harness (exact serving SHA)  
- Post-#367 genuine Cloud Run signals proof + new prediction evidence  
- Scheduler health green after signals cadence restored  
- Same-session Option Chain UI vs `/api/batch/chains` timestamp parity  
- 60-minute market stability after shorter gates green  
- Verified-contracts path so QC can leave NOT_READY when truthful  

## Next batch (ordered)

1. Pin SHA/revision/traffic again before each proof window  
2. 18:45 IST — observe first post-#367 signals execution  
3. Re-GET `/api/scheduler/health` — confirm severity returns to `none` only with evidence  
4. Continuous semantic session: broker + chains API + UI values  
5. Only then 60-minute stability  

## Agent agreement

- **Cursor (GCP MRI):** live API multi-verify, runbook/CSV/SSOT, #188 bus  
- **ChatGPT (controller):** keep RHUI mail/ledger reconciled to this SSOT; do not invent ACCEPTED  
- **Claude (forensic):** adversarial check of scheduler attribution + signals logs after 18:45; no duplicate QC PR  
- **All:** preserve `00617-vif`; no blind redeploy; no laptop token mint  

Coordination marker: `SYSTEM3_COORDINATION_V1` on Issue #188.
