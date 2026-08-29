# Phase 2 — Five-Layer Technical Architecture Audit

**Marker:** `PHASE2_FIVE_LAYER_AUDIT_V2026_08_26`  
**Authority:** GitHub `origin/main` + live Cloud Run (laptop non-authoritative)  
**Lane lock:** Cursor = architecture/UI/deploy MRI; Claude QC = [#361](https://github.com/psw2025-cmd/Genesis_System3/pull/361) only  
**LIVE:** OFF (do not enable)

## SHAs

| Plane | SHA |
|---|---|
| `origin/main` | `185ff0f23d5f9da79d498f9a1da4fc94c073df1e` |
| Live `/api/deploy_info` | `185ff0f23d5f9da79d498f9a1da4fc94c073df1e` |
| Match | **YES** |
| Laptop HEAD (non-truth) | `146eb69…` on `fix/p0-188-bankex-paced-cache-20260824` |

## Live snapshot (audit time ~2026-08-26 07:30 IST)

- mode=`PAPER` / broker=`ANALYZER`; `live_trading_enabled=false`; `order_placement_allowed=false`
- market=`closed` (pre-open); signals=`NO_TRADE`; state.qc=`NOT_READY` (`NO_VERIFIED_CONTRACTS`)
- auto_gates=`2/7`; ML model_proof_ready=`false`
- POST `/api/orders/create` → `423 LIVE_MUTATION_LOCKED`

## Layer status (summary)

| Layer | Status | Notes |
|---|---|---|
| 1 Ingestion | PARTIAL | Chains/broker/instruments live; freshness quartet missing; no sentiment API |
| 2 Integrity | PARTIAL | SHA+mode+secrets present; no config_fingerprint unified hard-stop API |
| 3 Analytics | PARTIAL | Path1 IV/Greeks/OI partial; Path2 gain_rank partial; ML registry BLOCKED |
| 4 Synthesis | PARTIAL | NO_TRADE present; calibrated confidence / hedge / TS-align missing |
| 5 Execution | PARTIAL | Paper sim present; LIVE hard-stopped; order SM not proven |

Full narrative: see parent agent final response (same session).
