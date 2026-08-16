# Lane F — Prediction / ML forensic vs institutional blueprint

**Worktree:** `C:\System3\Genesis_System3_audit_main_c763ecf`  
**SHA:** `c763ecf048478842688373cf674eb56a7dc04aa9`  
**Mode:** READ-ONLY code forensic  
**Blueprint:** `docs/architecture/INSTITUTIONAL_AUTONOMOUS_ML_TRADING_BLUEPRINT.md`

Labels used: **IMPLEMENTED_AND_PROVEN** | **PARTIAL** | **PLANNED_ONLY** | **MISSING**

---

## 1. Executive verdict

Production ranking is primarily **multi-factor heuristics** (`GainRankEngine`) with an optional **ML confidence** factor fed from `dhan_index_ai_signals.csv` (often bhavcopy-driven). A real **ensemble of pickled classifiers** exists (`src/ml/ensemble_predictor.py`) and a **blended trainer** + **auto_retrain** script exist, but there is **no MLflow registry, no gated promotion, no institutional nightly control plane**, and backtest readiness is **mechanics/partial**, not blueprint-complete. Most blueprint pillars remain **PLANNED_ONLY / MISSING**.

---

## 2. Real model vs heuristic

| Component | Nature | Evidence |
|-----------|--------|----------|
| `GainRankEngine` | **Heuristic** weighted scores (OI, IV proxy, volume, PCR, premium, momentum, ml_confidence) | `src/ranking/gain_rank_engine.py` `FACTOR_WEIGHTS`; ml_confidence default weight **0.15** |
| `ml_signal_aggregator` | **Bridge**, not a model | Averages `prob_BUY_CE` / move scores from CSV → 0–100 |
| `run_signal_engine_from_bhavcopy` | **Feature/signal writer** from EOD bhavcopy | Hardcoded 4 indices; activates ml_confidence without live Data API |
| `EnsemblePredictor` | **Real ML ensemble** (Ultra, XGB, LGBM, CatBoost, RF, NN, Delta) if pickles present | `src/ml/ensemble_predictor.py`; graceful degrade if libs/models missing |
| `dhan_blended_model_trainer_v2` | **Real training** on blended CSV → `core/models/dhan/{U}_model.pkl` | Docstring historically “MANUAL ONLY”; `auto_retrain.py` also invokes it |
| Regime / Optuna / Ray / HMM | **Not production path** | Ultra menu / phase modules; not the daily GainRank SSOT |

**Runtime truth for dashboard gain-rank:** heuristic + optional CSV ML factor. Ensemble is available for phases/tools but is **not** the sole production ranker.

---

## 3. Training scripts & artifacts

| Script / module | Role | Status |
|-----------------|------|--------|
| `core/engine/dhan_blended_model_trainer_v2.py` | Train blended models; backup; write pickles | **PARTIAL** (code present; host data dependent) |
| `core/engine/dhan_blended_model_trainer.py` | Legacy trainer | **PARTIAL** |
| `core/engine/train_dhan_models.py` | Per-underlying train helper used by v2 | **PARTIAL** |
| `scripts/auto_retrain.py` | Consumes `state/retrain_signal.json`; trains; clears signal | **PARTIAL** (prereq: ≥500 rows in blended CSV) |
| `scripts/run_signal_engine_from_bhavcopy.py` | Daily signal CSV from bhavcopy | **PARTIAL** |
| `scripts/daily_gain_rank_and_validate.py` | Rank + validate ρ | **PARTIAL** |
| `scripts/calibrate_factor_weights.py` | Weight calibration after 5+ days (referenced) | **PARTIAL / PLANNED** usage |
| `scripts/model_training_dryrun_proof.py` | Dry-run inventory proof | **PROOF_ONLY** |
| Phase 391 XGB tools | Isolated phase models under `storage/models/xgboost/` | **PARTIAL** |

**Training data:** `storage/training/dhan_blended_training_preview.csv` (+ related training CSVs).  
**Model dirs:** `core/models/dhan/`, `core/models/{ultra,xgboost,…}/`, `storage/models/…`.

Hardcoded train underlyings: `NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX` — Issue #188 / universe parity gap.

---

## 4. Retrain schedule

Scheduler config (phase82 jobs; observed in live `/api/system_health` snapshots):

| Job ID | Schedule (IST) | Role |
|--------|----------------|------|
| `daily_gain_rank` | 09:15 | Pre-market rank |
| `daily_gain_validate` | 15:35 | Post-market ρ / hit rate |
| `daily_gain_trend` | 15:40 | Accuracy trend |
| `auto_retrain` | 16:00 | Retrain **only if** `retrain_signal.json` exists |
| `bhavcopy_download` | 18:30 | NSE FO bhavcopy |
| `signal_engine_bhavcopy` (documented 18:45) | Post bhavcopy | Signal CSV |
| `datasource_health_check` | ~08:00 | Source health |

Retrain trigger: `src/validation/market_result_validator.py` emits `state/retrain_signal.json` when Spearman ρ &lt; 0.40 for **3 consecutive days** (action text: retrain ensemble + reoptimize factor weights).

Catch-up policy tests assert auto_retrain **never** fires without signal file.

**Cloud caveat:** catchup reports have shown `auto_retrain: SKIPPED_UPSTREAM_MISSING` and import failures on related jobs — schedule exists; **PRODUCTION proven continuous operation = PARTIAL**.

---

## 5. Registry / promotion

| Blueprint requirement | Code reality | Label |
|----------------------|--------------|-------|
| MLflow model registry | No MLflow integration in core training path | **MISSING** |
| Signed model manifest (sha256 + metrics) | Meta JSON beside pickles only | **PARTIAL** |
| Candidate promotion gates (data quality, backtest, walk-forward, paper, risk, calibration, governance) | `tools/model_benchmark_leaderboard.py` explicitly: walk-forward / promotion gate **not yet implemented** | **MISSING** / **PLANNED_ONLY** |
| Rollback target | Backup folders via trainer | **PARTIAL** |
| Deploy cannot enable live mode | Hard safety locks elsewhere | **IMPLEMENTED_AND_PROVEN** (safety, not ML registry) |

---

## 6. Backtest readiness

| Capability | Location | Label |
|------------|----------|-------|
| Synthetic / ultra backtest menu | `core.engine.dhan_synthetic_backtester`, `system3_ultra.py` options | **PARTIAL** |
| Legacy costed walk-forward mechanics | `src/quant/alpha_truth.py` `evaluate_legacy_costed_walkforward` — explicitly **not** AlphaTruth performance proof | **PARTIAL** |
| Lifetime research walk-forward | `tests/test_lifetime_research_engine.py` | **PARTIAL** (unit/research) |
| Nightly replay vs active model bundle with version stamps | Blueprint Pillar 1 | **MISSING** |
| Costed walk-forward + slippage proven in production gate | `system3_maximum_safe_production_probe.py` flags `walk_forward_cost_slippage_proven: false` | **MISSING** |
| Paper lifecycle as promotion gate | `scripts/paper_lifecycle_proof.py` + reports | **PARTIAL** (often not market-day proven) |

**Verdict:** backtest **tooling exists**; institutional **gated nightly replay + promote** does **not**.

---

## 7. Blueprint pillar scorecard

Mapped to `INSTITUTIONAL_AUTONOMOUS_ML_TRADING_BLUEPRINT.md`:

### Pillar 1 — Workflow automation

| Item | Label | Notes |
|------|-------|-------|
| Nightly ingestion after close | **PARTIAL** | Bhavcopy + jobs; not full OHLCV/tick/OC Parquet partitions |
| Immutable Parquet raw store | **MISSING** | CSV/JSON files |
| Schema validation (Pandera/GE) | **MISSING** | Ad-hoc checks |
| Feature tables from validated data | **PARTIAL** | Ad-hoc DataFrames / CSVs |
| Prefect orchestration | **PLANNED_ONLY** | Phase82 JSON scheduler instead |
| Automated nightly replay + metrics store | **MISSING** |
| Model lifecycle promotion gates | **MISSING** |
| MLflow + signed manifest | **MISSING** / **PARTIAL** meta JSON |

### Pillar 2 — Self-learning / optimization

| Item | Label | Notes |
|------|-------|-------|
| After-cost objective | **PARTIAL** | AlphaTruth / expectancy probes; not continuous trainer objective |
| Optuna / Ray Tune | **PLANNED_ONLY** | Not wired to auto_retrain |
| Walk-forward / purged splits / embargo | **PARTIAL** research tests; **MISSING** in promotion |
| Factor weight calibration | **PARTIAL** | Manual/grid notes; 5+ day auto-calibrate aspirational |

### Pillar 3 — Market regime

| Item | Label | Notes |
|------|-------|-------|
| Regime engine outputs (trend/vol/…) | **PARTIAL** | Ultra phases (`ultra_regime_classifier`, phase217/302) exist as modules |
| Production ranker regime gating | **MISSING** | GainRank does not consume HMM/regime classifier as SSOT |
| Online change-point / HMM / temporal NN | **PLANNED_ONLY** | Blueprint aspirational |

### Pillar 4 — Execution / infrastructure

| Item | Label | Notes |
|------|-------|-------|
| Async stream → queue → predict → risk → persist | **MISSING** | Paced REST + dashboard loops |
| Postgres/Timescale lifecycle store | **MISSING** |
| GCS data lake | **MISSING** (GCP used for app/token, not ML lake) |
| Analyzer/paper safety locks | **IMPLEMENTED_AND_PROVEN** | Live flags off; readonly broker |

### Safety policy (blueprint)

| Item | Label |
|------|-------|
| Live disabled until multi-week proof | **IMPLEMENTED_AND_PROVEN** |
| Promotion cannot enable live | **IMPLEMENTED_AND_PROVEN** (no promotion plane; flags hardcoded) |

---

## 8. Issue #188 intersection (ML)

- Signal + train universes are **hardcoded index subsets**, not full broker master → ML features/labels **cannot** claim full equity-option universe coverage.
- Without full chain lineage (Lane D/E), model inputs inherit coverage defects (silent omission vs explicit defect labels).

---

## 9. What is IMPLEMENTED_AND_PROVEN (narrow)

Only items with both code **and** durable safety/proof character:

1. Live trading disabled / paper-analyzer posture.
2. GainRank heuristic pipeline code + factor weights + history file writers.
3. Retrain **signal contract** (emit/clear) and scheduler job definitions.
4. Ensemble + blended trainer **code paths** (not continuous cloud proof).

Everything else ML/control-plane: **PARTIAL**, **PLANNED_ONLY**, or **MISSING**.

---

## 10. Recommended proof next (read-only note)

To move labels forward without enabling live:

1. Inventory pickles + blended CSV row counts on the production host/volume.
2. Dry-run `python scripts/auto_retrain.py --dry-run`.
3. Run `scripts/model_training_dryrun_proof.py` and attach under `reports/latest/`.
4. Separate heuristic ρ proof from ensemble accuracy proof in dashboards (label sources).
5. Do not claim blueprint “autonomous ML platform” until Parquet lineage + registry + promotion gates exist.
