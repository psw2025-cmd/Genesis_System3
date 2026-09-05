# Lane E — Data lineage forensic

**Worktree:** `C:\System3\Genesis_System3_audit_main_c763ecf`  
**SHA:** `c763ecf048478842688373cf674eb56a7dc04aa9`  
**Mode:** READ-ONLY code forensic  
**Blueprint reference:** `docs/architecture/INSTITUTIONAL_AUTONOMOUS_ML_TRADING_BLUEPRINT.md`

---

## 1. Executive verdict

Lineage is **file-path oriented** (CSV/JSON under `storage/`, `state/`, `outputs/`, `reports/`), not an immutable partitioned lake with data/feature/model version IDs. Most runtime market artifacts are **EPHEMERAL** or **SESSION_DURABLE**. Training CSVs and model pickles are **LOCAL_ARTIFACT** durable on a host that keeps the volume; Cloud Run does not make them **PRODUCTION_DURABLE** unless explicitly synced to GCS/Secret/volume. Blueprint Prefect/Parquet/MLflow lineage is **PLANNED_ONLY / MISSING**.

---

## 2. Durability taxonomy (used below)

| Class | Meaning |
|-------|---------|
| **PRODUCTION_DURABLE** | Survives instance recycle; multi-revision SSOT (e.g. GCS, Secret Manager, managed DB) with explicit version |
| **REPO_DURABLE** | Checked into git or bundled with deploy image |
| **LOCAL_ARTIFACT** | Written under `storage/` / `core/models/` on a persistent disk (laptop/VM); may vanish on Cloud Run |
| **SESSION_DURABLE** | Survives process restart on same filesystem; not multi-instance SSOT |
| **EPHEMERAL** | In-memory / TTL / process-only |
| **PROOF_ONLY** | `reports/latest/**` evidence; not runtime feed SSOT |
| **MISSING** | Blueprint requires it; code/path absent |

---

## 3. Instruments / security master

```text
Dhan CDN / fetch_security_list
        → scripts/sync_dhan_instruments_master.py (scheduled ~08:35 IST per docs)
        → storage/instruments/OpenAPIScripMaster.json  [SESSION_DURABLE / LOCAL_ARTIFACT]
        → api-scrip-master-detailed.csv (synced)       [LOCAL_ARTIFACT]
        → security_id_list.csv (bundled fallback)      [REPO_DURABLE]
        → core/data/instruments_cache.get_instruments_df()
        → equity_fo_universe / routers/chain discovery
```

| Node | Class | Notes |
|------|-------|-------|
| Bundled CSV | **REPO_DURABLE** | Emergency fallback |
| Runtime JSON | **SESSION_DURABLE** | Rebuildable; Cloud Run ephemeral unless volume |
| In-memory InstrumentsCache singleton | **EPHEMERAL** | Per process |
| Versioned master diffs / GCS lake | **MISSING** | Issue #188 + blueprint |

Consumers: `core/brokers/dhan/instruments.py`, `equity_fo_universe.py`, `DataSourceManager._resolve_underlying`, `dashboard/backend/routers/chain.py`.

---

## 4. Option chains

```text
Dhan option_chain API
  → DataSourceManager (paced 3.4s) 
  → chain_adapter / app._get_chain_uncached
  → _PUSHED_CHAIN_CACHE + TTL                        [EPHEMERAL]
  → optional write state/chain_cache/{SYM}.json       [SESSION_DURABLE]
  → optional storage/live/option_chain_cache.json     [SESSION_DURABLE]
  → /api/chain, /api/batch/chains, /ws/stream fan-out
```

Alternate EOD path:

```text
NSE FO bhavcopy → storage/bhavcopy/*_fo_bhavcopy.csv  [LOCAL_ARTIFACT]
  → run_signal_engine_from_bhavcopy.py
```

| Node | Class |
|------|-------|
| Live OC responses | **EPHEMERAL_REMOTE** (no raw Parquet partition) |
| Pushed/TTL cache | **EPHEMERAL** |
| `state/chain_cache/` | **SESSION_DURABLE** |
| Bhavcopy files | **LOCAL_ARTIFACT** |
| Immutable daily Parquet OC lake | **MISSING** |

---

## 5. Signals

```text
bhavcopy (or live signal engine)
  → storage/live/dhan_index_ai_signals.csv            [LOCAL_ARTIFACT]
  → curated/forward variants (tools/quick_inspector)  [LOCAL_ARTIFACT]
  → src/ranking/ml_signal_aggregator.load_ml_confidence()
  → GainRankEngine factor ml_confidence (15%)
  → state/gain_rank_history.json                      [SESSION_DURABLE]
```

| Artifact | Path | Class |
|----------|------|-------|
| Raw signals | `storage/live/dhan_index_ai_signals.csv` | **LOCAL_ARTIFACT** |
| Curated / forward | `storage/live/dhan_index_ai_signals_curated.csv`, `…_with_forward.csv` | **LOCAL_ARTIFACT** |
| Rank history | `state/gain_rank_history.json` | **SESSION_DURABLE** |
| IV history | `state/iv_history.json` | **SESSION_DURABLE** |
| Retrain flag | `state/retrain_signal.json` | **SESSION_DURABLE** (deleted after retrain) |

Signal engine hard-filters to `NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY` — lineage **does not** include full OPTSTK universe.

---

## 6. Predictions / rankings

```text
GainRankEngine.rank_all(chains, spots, oi_history, ml_confidence)
  → daily_gain_scanner / daily_gain_rank_and_validate
  → state/gain_rank_history.json
  → dashboard /api/gain_rank, /api/accuracy_trend
```

Ensemble path (separate from GainRank heuristics):

```text
Feature frame
  → src/ml/ensemble_predictor.EnsemblePredictor
  → loads pickles under core/models/** and storage/models/**
  → BUY/SELL/HOLD (+ confidence); regression head for % gain called out as gap in AGENTS.md
```

| Output | Class |
|--------|-------|
| Rank JSON history | **SESSION_DURABLE** |
| Ensemble in-memory prediction | **EPHEMERAL** |
| Dashboard API responses | **EPHEMERAL** (+ optional cache) |

No feature-store table or `feature_version` ID in runtime path (**MISSING** vs blueprint).

---

## 7. Paper trades / lifecycle

```text
GainRank / paper selectors
  → src/trading/paper_executor.py, pnl_tracker.py
  → dashboard/backend/paper_pipeline_v8 (worker: scripts/gcp_worker_job.py, scripts/system3_core_pipeline_v8.py)
  → state/paper_pipeline_v8/* (e.g. closed_paper_trade_ledger.jsonl)   [SESSION_DURABLE]
  → storage/live/dhan_virtual_orders.csv, dhan_index_ai_pnl_log.csv, trades_plan.csv  [LOCAL_ARTIFACT]
  → outputs/trade_execution_log.jsonl                                   [LOCAL_ARTIFACT]
  → reports/latest/analyzer_paper_lifecycle_proof/summary.json          [PROOF_ONLY]
```

| Artifact | Class | Notes |
|----------|-------|-------|
| Virtual orders / PnL CSVs | **LOCAL_ARTIFACT** | Analyzer paper, not broker fills |
| Paper pipeline ledger | **SESSION_DURABLE** | JSONL under `state/` |
| Trade execution log | **LOCAL_ARTIFACT** | Often empty → trader history `NOT_FOUND` |
| Lifecycle proof JSON | **PROOF_ONLY** | Gates claim not proven until market-day run |
| Production Postgres/Timescale lifecycle store | **MISSING** | Blueprint Pillar 4 |

Live trading remains disabled; no production order lineage.

---

## 8. Model artifacts

```text
storage/training/dhan_blended_training_preview.csv     [LOCAL_ARTIFACT]
  → core/engine/dhan_blended_model_trainer_v2.py
  → core/models/dhan/{UNDERLYING}_model.pkl + _meta.json
  → backup via backup_existing_models()

Also:
  core/models/{ultra,xgboost,lightgbm,catboost,neural_net,rf}/…
  storage/models/xgboost/phase_391/…
```

| Artifact | Class |
|----------|-------|
| Training CSV | **LOCAL_ARTIFACT** |
| Pickle models + meta JSON | **LOCAL_ARTIFACT** |
| Model backups (trainer) | **LOCAL_ARTIFACT** |
| MLflow registry / signed promotion manifest | **MISSING** |
| GitHub Actions model promotion gate | **PARTIAL** (leaderboard notes “promotion gate not yet implemented”) |

Consumers: `ensemble_predictor.py`, `auto_retrain.py`, phase tools under `tools/run_phase_391_*`.

---

## 9. End-to-end lineage diagram (as implemented)

```text
[REPO] security_id_list.csv ──┐
[SYNC] OpenAPIScripMaster ────┼─→ discovery / equity FO / DSM equity IDs
                              │
Dhan REST OC ─paced─→ EPHEMERAL cache ─→ UI/API
                              │
NSE bhavcopy ─→ LOCAL_ARTIFACT CSV ─→ signals CSV ─→ ml_confidence ─→ GainRank
                              │
training CSV ─→ LOCAL_ARTIFACT pkl ─→ ensemble (optional)
                              │
paper CSVs / state JSONL ─→ PROOF_ONLY reports (lifecycle gates)
```

**Broken / weak joins:**

1. Full master discovery ≠ paced OC / signal / train symbol sets.
2. Cloud ephemeral disk breaks LOCAL_ARTIFACT continuity across revisions.
3. No data_version / model_version / config_version stamped on paper trades.
4. Blueprint nightly validate → feature build → replay → promote loop not wired as one control plane.

---

## 10. Classification matrix (quick)

| Domain | Dominant class | Production-ready SSOT? |
|--------|----------------|------------------------|
| Instruments | REPO + SESSION | Partial (bundled + sync) |
| Live chains | EPHEMERAL | No |
| EOD bhavcopy | LOCAL_ARTIFACT | Host-dependent |
| Signals / ranks | LOCAL + SESSION | No |
| Predictions | EPHEMERAL | No |
| Paper trades | LOCAL + SESSION + PROOF | No |
| Models | LOCAL_ARTIFACT | No registry |
| Blueprint lake/registry | MISSING | No |

---

## 11. Issue #188 linkage

Universe parity requires lineage from **broker master → backend counts → UI counts**. Current lineage stops at discovery for equities; live chain/signal/train paths remain **hardcoded subsets**, so API/UI parity proofs for “full supported equity-derivatives universe” cannot pass without expanding paced acquisition and labeling coverage defects.
