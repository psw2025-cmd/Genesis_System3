# Genesis System3 Live Diagnostic Report

**Request start UTC:** `2026-08-27T17:51:43.1705002Z`  
**Inspected code:** working tree at `146eb69b697f86559d50519f8eaee3c8fbb8a82c`, branch `fix/p0-188-bankex-paced-cache-20260824`  
**Method:** fresh source inspection and read-only Cloud Run commands. Existing reports/logs were not used as runtime truth. No LIVE/order mutation occurred.

## Diagnosis

1. Cloud Run reports **no volume or volume mount** (`null`). Ordinary files written inside the container are ephemeral across instance replacement and deployment.
2. The service sets `SYSTEM3_STATE_BACKEND=firestore` and `SYSTEM3_STATE_BACKEND_REQUIRED=1`, but ML persistence is split between durable Firestore worker artifacts and local-file readers.
3. The durable worker rank lane publishes Firestore `artifact_rank`. `system3_model_accuracy_tracker.py` never reads it; it searches three APIs plus local JSON files. `/api/gain_rank` also reads local `state/gain_rank_history.json`. After a fresh instance, this yields `NO_PREDICTION_SOURCE_FOUND` even when a durable rank artifact exists.
4. `dashboard/backend/app.py` live gates count only local validation files and read only `spearman_correlation`. The validator writes `rank_correlation_spearman`. This local-only reader and key mismatch can keep `validation_days`/`ml_accuracy_rho` locked.
5. Dhan V2 Greeks are mapped by the primary parser and rendered by the UI, but missing/malformed Greeks are silently converted to zero, and the legacy flat-list parser omits them.
6. No common liquidity filter exists. The API appends every CE/PE contract, the UI maps every returned strike, and the ranker scores the unfiltered chain. Zero-OI/zero-volume legs therefore survive.

## ML and validation paths

| Purpose | Exact code | Storage/search behavior |
|---|---|---|
| Morning prediction writer | `src/ranking/gain_rank_engine.py:468-485` | `_save_snapshot()` rewrites `state/gain_rank_history.json` (ephemeral on Cloud Run). |
| IV history writer | `src/ranking/gain_rank_engine.py:57-59, 456-462` | Writes `state/iv_history.json` (ephemeral). |
| Older scanner output | `src/ranking/daily_gain_scanner.py:89-104` | Writes `state/daily_scan_reports/prediction_<date>_<time>.json`; it does not populate the canonical history file. |
| Durable rank producer | `scripts/gcp_worker_job.py`, `_run_rank_lane()` and `_artifact()` | Publishes Firestore `artifact_rank`. |
| Post-market orchestrator | `scripts/system3_post_market_auto_pipeline.py` | Runs `system3_model_accuracy_tracker.py --api-base ...` before gate evaluation. |
| Accuracy source search | `scripts/system3_model_accuracy_tracker.py:150-203` | Searches `/api/state`, `/api/gain_rank`, `/api/accuracy_trend`, `state/gain_rank_history.json`, one hard-coded 2026-06-12 validation file, option-visibility report, two signal JSONs, and recent local validation files. It does **not** load Firestore `artifact_rank`. |
| Legacy prediction lookup | `src/validation/market_result_validator.py:380-391` | Reads today's predictions only from `state/gain_rank_history.json`. |
| Legacy validation writer | `src/validation/market_result_validator.py:393-399` | Writes `state/market_validations/market_validation_<date>.json`. |
| Written rho key | `src/validation/market_result_validator.py:75-90` | `rank_correlation_spearman`. |
| Durable validation lane | `scripts/gcp_worker_job.py:260-311` | Reads Firestore `artifact_rank`, validates an explicit snapshot, then calls `upsert_validation_day()`. |
| Durable validation store | `dashboard/backend/firestore_state_backend.py:151-222` | Writes `validation_day_<date>` and `validation_days_index`; `list_validation_days()` reads them. |
| Seven-gate evaluator | `scripts/system3_gate_evaluator.py:64-125` | Firestore-aware and accepts `rank_correlation_spearman`, `spearman_correlation`, `spearman_rho`, or `rho`; requires five passing days at rho >= 0.70. |
| Dashboard live gates | `dashboard/backend/app.py:2429-2454` | Counts local `market_validation_*.json` files and reads only `spearman_correlation`; not Firestore-aware. |
| ML performance router | `dashboard/backend/routers/ml.py:18-125` | Merges Firestore validation days with local files, but prediction-day count remains local-history based. |

### Required durable correction

Use one shared Firestore-aware contract for the durable morning prediction ledger, validation-day loader, accuracy tracker, accuracy API, and live gates. Normalize rho aliases through one helper. Treat local JSON as a local mirror only.

## Instrument universe loading

1. `scripts/sync_dhan_instruments_master.py` downloads the official `api-scrip-master-detailed.csv` and writes it under `storage/instruments/`, plus `master_meta.json` and normalized `OpenAPIScripMaster.json`.
2. `core/data/instruments_master.py` resolves detailed CSV, compact CSV, then bundled `security_id_list.csv`.
3. `core/data/instruments_cache.py` loads runtime JSON first, then the resolved CSV, and may rebuild runtime JSON.
4. `dashboard/backend/app.py:375-394` may sync on startup, then calls `ensure_instruments_loaded()`.

All downloaded/derived files above are ephemeral on the current Cloud Run template because there is no mount. A cold instance must rebuild them or use the bundled fallback.

## Greeks ingestion

| Stage | Exact code | Finding |
|---|---|---|
| Dhan request | `core/data/datasource_manager.py:378-466` | Calls Dhan option chain and selects the official or compatibility parser. |
| Official map | `core/data/dhan_option_chain_parser.py:31-70` | Maps nested `greeks.delta/gamma/theta/vega`, OI, volume, IV and quotes. |
| Compatibility map | `core/data/dhan_option_chain_parser.py:166-205` | Legacy flat `options_chain` mapping omits all four Greeks. |
| API adapter | `dashboard/backend/chain_adapter.py:68-120` | Copies four Greeks but defaults absent values to numeric zero. |
| UI | `dashboard/frontend/src/components/OptionChain.tsx:28-31, 301-372` | Defines and renders Delta, Gamma, Theta and Vega for CE/PE. |
| Feature path | `core/engine/system3_signal_engine.py:263-283` | Expects/computes Greeks and falls back to zero on failure. |

The hardening point is the Dhan parser, then the chain adapter: preserve `null` for unavailable values, map Greeks in the compatibility branch, and add `greeks_available` plus `greeks_source=dhan_precomputed`. Missing must not become a measured zero in the feature store.

## Strike selection and liquidity filtering

- `dashboard/backend/chain_adapter.py:28-45` limits only by optional count and ATM distance; default is the full broker chain.
- `chain_adapter.py:68-120` has no OI/volume/quote rejection and appends every leg at `contracts.append(base)`.
- `OptionChain.tsx:284-295` groups every contract. The default `range=10` is only an ATM slice; ALL STRIKES exposes the complete set.
- `src/ranking/gain_rank_engine.py:80-149` scores each full input chain without shared liquidity cleanup.

Inject one shared classifier before API append and before rank/feature scoring. Minimum normal-view rejection for an individual leg: `oi <= 0 OR volume <= 0`; optionally require positive LTP/bid/ask, bounded spread, and fresh quote age. Retain a strike when the opposite leg passes; remove the full strike only when both fail. Return raw/liquid/filtered counts and reasons. The dead 18,500 leg currently enters at `chain_adapter.py:120` and `OptionChain.tsx:285-290`.

## Raw Cloud Run output

### Volumes and mounts

```powershell
gcloud run services describe genesis-system3-web --region=asia-south1 --format="yaml(spec.template.spec.volumes, spec.template.spec.containers[0].volumeMounts)"
```

```text
  null
```

### Environment names and plain values

```powershell
gcloud run services describe genesis-system3-web --region=asia-south1 --format="table[box](spec.template.spec.containers[0].env.name, spec.template.spec.containers[0].env.value)"
```

The exact raw stdout body was:

```text
NAME
['DHAN_CLIENT_ID', 'WORKER_PUSH_TOKEN', 'SYSTEM3_STARTUP_TOKEN_REFRESH', 'DHAN_CANONICAL_ROTATION_SELF_HEAL', 'LIVE_TRADING_ENABLED', 'SYSTEM3_LIVE_TRADING_ALLOWED', 'AUTO_EXECUTE_TRADES', 'REQUIRE_API_KEY', 'ANALYZE_MODE', 'SYSTEM3_MODE', 'SYSTEM3_REAL_ONLY', 'CLOUD_PAPER_ENGINE', 'DEFER_INSTRUMENT_WARMUP', 'SYSTEM3_STATE_BACKEND', 'SYSTEM3_STATE_BACKEND_REQUIRED', 'SYSTEM3_FIRESTORE_PROJECT', 'SYSTEM3_STATE_REFRESH_S', 'SYSTEM3_SYNC_INTERVAL_S', 'DHAN_TOKEN_SOURCE', 'DHAN_ACCESS_TOKEN_SECRET_ID', 'DHAN_TOKEN_CACHE_TTL_S', 'DHAN_TOKEN_ROTATION_JOB', 'DHAN_TOKEN_ROTATION_SCHEDULE', 'DHAN_STATUS_AUTO_REFRESH', 'DHAN_STATUS_REFRESH_COOLDOWN_S', 'DHAN_PERSIST_TOKEN_TO_SM', 'BROKER_SELF_HEAL_TOKEN_REFRESH', 'DHAN_CANONICAL_ROTATION_COOLDOWN_S', 'DHAN_ROTATE_PUBSUB_TOPIC', 'DHAN_CANONICAL_ROTATION_WAIT_S', 'CLOUD_MODE', 'SYSTEM3_DEPLOY_TARGET', 'MEM_LIMIT_MB', 'MEM_WARN_MB', 'MEM_GC_MB', 'MARKET_TOP_MICRO_STREAM', 'SYSTEM3_PUBLIC_BACKEND_URL', 'SYSTEM3_API_BASE', 'PUBLIC_BACKEND_URL', 'PUBLIC_DASHBOARD_URL', 'DEPLOY_GIT_SHA', 'FORCE_RESTART_TIMESTAMP']

VALUE
['0', '0', '0', '0', '0', 'false', '1', 'ANALYZER', '1', '0', '1', 'firestore', '1', 'system3-openalgo-safe', '5', '60', 'gcp-secret-manager-dynamic', 'dhan-access-token', '30', 'genesis-system3-dhan-token-rotate', '*/5 * * * * Asia/Kolkata', '0', '3600', '0', '0', '900', 'broker-token-rotate', '120', '1', 'gcp-cloud-run', '960', '700', '850', '0', 'https://genesis-system3-web-doq2wplepa-el.a.run.app', 'https://genesis-system3-web-doq2wplepa-el.a.run.app', 'https://genesis-system3-web-doq2wplepa-el.a.run.app', 'https://genesis-system3-web-doq2wplepa-el.a.run.app/ui', 'f9f660e82880e1c96e0e797a5100ffaf0bba827f', '1787324373']
```

The table formatter returns positional arrays; secret-backed entries have no plain `.value`, so the arrays are not one-to-one. No secret payload was printed.

## Verdict

- Ephemeral filesystem risk: **PROVEN** by the live `null` mounts response.
- ML proof continuity: **FAIL** due to durable-producer/local-reader disconnect.
- Live gate rho/day continuity: **FAIL** due to local-only input plus rho-key mismatch.
- Dhan Greeks: **primary mapping exists; missing/legacy semantics are lossy**.
- Liquidity filtering: **absent from the shared API/ranker path**.

No real order, LIVE change, IAM mutation, secret read, or data deletion was performed.
