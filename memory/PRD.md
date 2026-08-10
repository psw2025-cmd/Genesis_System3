# PRD — GENESIS SYSTEM 3 (GCP debugging engagement)

## Original problem statement
User's automated Indian F&O trading system (pre-existing, large codebase) deployed on Google Cloud Run
was stuck in a "Token Paradox" churn loop: Dhan broker invalidates all prior access tokens whenever a
new PIN+TOTP login occurs. The web service's self-heal kept minting new tokens, invalidating the one
just stored, causing infinite DH-906 failures and Secret Manager hammering (~4 reads/sec, reload_count 25k+).
User also accidentally overwrote GCP secret `dhan-pin` with the literal string "NEW_VALUE".

## Deployment reality (CRITICAL for future agents)
- App does NOT run in this pod. It runs on Google Cloud Run.
- Project: `system3-openalgo-safe` (number 802404398783), region `asia-south1`
- Web service: `genesis-system3-web` → https://genesis-system3-web-doq2wplepa-el.a.run.app
- Token rotation: Cloud Run Job `genesis-system3-dhan-token-rotate`
- Deploy script: `scripts/gcp_cloud_run_auto_deploy.py` (forces safe env incl. BROKER_SELF_HEAL_TOKEN_REFRESH=0)
- Test backend changes via curl against the live GCP URL; user executes gcloud commands in Cloud Shell.

## Implemented (2026-08-11)
1. **Secret recovery** (user-executed script): restored dhan-pin (v10), disabled corrupt v9, re-ran rotation
   job → token v35, /fundlimit HTTP 200, live `/api/broker/status` shows connected:true. VERIFIED.
2. **SYS3-BLK-011 permanent fix (code, awaiting redeploy):**
   - `core/brokers/dhan/token_manager.py`: `_validate_token_live()` + `_validated_persist()` — every
     generated/renewed token is proven against /fundlimit BEFORE persisting to Secret Manager.
   - `core/brokers/dhan/cloud_token_provider.py`: `force_reload()` throttled to 1 per 30s (stops SM hammering).
   - `dashboard/backend/app.py`: BROKER_SELF_HEAL_TOKEN_REFRESH default flipped "1"→"0"; fixed busy-loop
     bug where `continue` skipped `asyncio.sleep` in the self-heal watchdog.
   - Local mocked tests: 5/5 passed.
3. **SYSTEM_STATE.md** updated: GCP reality (was falsely claiming Render/Windows), token management SSOT rules.

## User actions pending
- Run gcloud: set BROKER_SELF_HEAL_TOKEN_REFRESH=0 on live service (immediate, no redeploy).
- Create Cloud Scheduler cron 07:30 IST daily for rotation job.
- Redeploy web service to activate code fixes.
- SECURITY: user posted Dhan PIN (197819) in chat — must change PIN on Dhan platform.

## Implemented round 2 (2026-08-11) — all locally tested (endpoint smoke tests via TestClient, 200 OK)
4. **SYS3-BLK-001 fixed**: new `dashboard/backend/connection_stability.py` — shared tracker with
   3-consecutive-failure confirmation + 120s DEGRADED grace window + flap/uptime stats. Wired into
   `/api/broker/status` (adds `stability` block) and `broker_truth_validator.py` (single transient
   failure now reports DEGRADED_TRANSIENT instead of BROKER_OFFLINE). Alert dedup (threshold=3)
   already existed in broker_alert_deduplicator.py and is used by state_sync_service.
5. **Rotation Health Card API**: new `GET /api/broker/token-health` — token metadata (no raw token),
   connection stability snapshot, policy block (single-writer, validate-before-persist), health verdict.
6. **SYS3-BLK-003 upgraded**: `/api/audit/option-visibility` now fetches LIVE Dhan option chains
   (via DataSourceManager + chain_adapter.fetch_chain_for_api, 45s cap, ≤8 underlyings) when no local
   cache exists — proves real PE/CE strikes + security tokens on Cloud Run. Response includes
   `chain_source` and `live_chain_symbols`.
7. **Doc cleanup**: README.md rewritten for GCP Cloud Run reality (Render/Windows refs removed);
   SYSTEM_STATE.md updated earlier.

## Implemented round 3 (2026-08-11) — "make everything real" (all tested: TestClient + UI screenshots)
8. **Multibagger Equity tab made REAL** (was 100% placeholder): new `dashboard/backend/multibagger_engine.py`
   — screens NSE F&O equity universe (211 real symbols) using Dhan /v2/charts/historical daily candles
   (~400 sessions). Real metrics: 1Y/6M/3M returns, 52w-high distance, volume expansion, 200DMA, max
   drawdown → composite score 0-100. 6h cache + state persistence. Endpoint `GET /api/equity/multibagger`.
   `MultibaggerResearch.tsx` fully rewritten: ranked table, refresh, honest NOT_READY state (never fake data).
9. **SYS3-BLK-004**: `GET /api/equity/fo-eligibility?symbols=A,B` — FOEligibilityFilter singleton
   bootstrapped from Dhan security master OPTSTK (222 symbols); fo_eligible flag also on every multibagger row.
10. **Daily Health Digest**: `GET /api/health/digest` — broker stability, token status, active alerts,
    screen freshness, F&O universe size. Real data only.
11. **Token Health Card UI**: new `TokenHealthCard.tsx` in System tab — consumes /api/broker/token-health,
    60s auto-refresh.
12. **Auth UX bug fixed**: /api/auth/status now returns authenticated:true when REQUIRE_API_KEY=false
    (prod unaffected — key still required there).
13. **Hardened prod real-only**: deploy script now forces SYSTEM3_REAL_ONLY=1 (synthetic data generators
    can never activate in production).
14. Frontend rebuilt (`dashboard/frontend/dist` updated — deploy image serves new bundle).

## Real-money trading status (honest)
- Order placement remains BLOCKED by design (dhan_readonly blocks orders; deploy script forces
  LIVE_TRADING_ENABLED=0). Real money flow requires the proof gates (/api/auto_gates: ML Spearman ≥0.70
  over 5 days, positive net expectancy, paper lifecycle proof) plus explicit user-enabled live flags.
  Do NOT silently enable. All data paths are now real (no synthetic in prod).
