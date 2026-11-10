# Genesis System3 — Q4–Q10 Quant Audit (ChatGPT handoff)

**Audit root:** `C:\System3\Genesis_System3` (branch `main`)  
**Preferred worktree:** `C:\System3\Genesis_System3_broker_permfix` **exists** but tracks `fix/broker-canonical-autoheal-20260816`, **not** `main` → not used as source of truth.  
**Date:** 2026-08-16  
**Live trading:** OFF (not evaluated here)  
**Status legend:** `WORKING` | `PARTIAL` | `NOT_PROVEN` | `MISSING`

---

## Audit scope decision

| Path | Branch | Used? |
|------|--------|-------|
| `C:\System3\Genesis_System3` | `main` (local ahead 1 / behind origin 606) | **Yes** |
| `C:\System3\Genesis_System3_broker_permfix` | `fix/broker-canonical-autoheal-20260816` | No (not main) |

---

## Q4 — FEATURE ENGINEERING INVENTORY

### A. GainRankEngine factors (production ranking path)

**File:** `C:\System3\Genesis_System3\src\ranking\gain_rank_engine.py`  
**Consumer:** `C:\System3\Genesis_System3\scripts\daily_gain_rank_and_validate.py`  
**UI:** `dashboard/backend/app.py` → `/api/gain_rank`  
**Status:** **PARTIAL** (code present; live Dhan chain often blocked; ML factor often redistributed)

| Feature | Formula (as coded) | Source fields | Lookback / TF | Null / fallback | Used by | Leakage risk |
|---------|-------------------|---------------|---------------|-----------------|---------|--------------|
| `oi_change_pct` | `abs((curr-prev)/prev)*100 * 6`, capped 100 | `state/dhan_oi_cache.json` prev + live chain OI sum | session-vs-session | if no hist: OI concentration `min(100, total_oi/1e6*10)` else 50 | GainRank | Low if prev is prior session; **medium** if same-day overwrite |
| `iv_percentile` | Prefer real IV col; else ATM straddle proxy `(CE+PE)/spot/sqrt(T)` vs last ≤5 days history | chain LTP/strike/expiry/spot; `state/iv_history.json` | ~5d rolling | 50 if no proxy; absolute `proxy*500` if hist&lt;2 | GainRank | Medium: history includes today after save; short hist unstable |
| `volume_surge` | `(curr/avg5 - 1)*50 + 50` | chain volume; optional `vol_history` | 5d avg if provided | absolute vol/1e6*10 or 50 | GainRank | Low; **avg_vol often unset** → weak signal |
| `pcr_divergence` | PCR=`PE_OI/CE_OI`; buckets → 90/70/55/45 | OI + option_type | same bar | 50 if cols missing | GainRank | Low (contemporaneous) |
| `atm_premium_ratio` | `expected_move=(ATM_LTP*2)/spot`; score=`move*1000` | LTP, strike, spot | same bar | 50, 0.02 | GainRank | Low |
| `momentum_score` | `50 + mean(change_pct)*10` | `change_pct`/`pct_change`/… | same bar | **50 hardcoded** if no col | GainRank | Low; often dead |
| `ml_confidence` | From aggregator (below); weight 0.15; if 0 → weight redistributed | signal CSV | ≤24h freshness | 0 → redistribute | GainRank | Depends on CSV provenance |

**Weights (`FACTOR_WEIGHTS`):**  
OI 0.20, IV 0.15, Vol 0.15, PCR 0.22, ATM prem 0.08, Momentum 0.05, ML 0.15  
**Calibration:** `C:\System3\Genesis_System3\scripts\calibrate_factor_weights.py` (auto-write only if ≥5 validation days) — **NOT_PROVEN** (only 1 validation day on disk)

### B. ML signal bridge features

**File:** `C:\System3\Genesis_System3\src\ranking\ml_signal_aggregator.py`  
**Expected CSV:** `storage/live/dhan_index_ai_signals.csv`  
**Expected columns:** `underlying`, `prob_BUY_CE`, `expected_move_score`, `ts`  
**Formula:**  
`directional = max(0,(avg_prob_CE-0.5)*200)`; `magnitude = clip(avg_move*50+50,0,100)`;  
`ml_conf = 0.6*directional + 0.4*magnitude`

**Observed CSV (2026-07-21):** different schema — `symbol,signal,confidence,...,data_source=PAPER` — **no** `prob_BUY_CE` / `underlying` → aggregator returns `{}` → ML factor inactive.  
**Status:** **NOT_PROVEN** (bridge code WORKING; live schema mismatch)

### C. Classifier training feature sets (model artifacts)

| Set | Features | File |
|-----|----------|------|
| Baseline GB / `*_model.pkl` | moneyness, ce_pe_ratio, atm_dist_*, ltp, strike, spot, chg_1_pct, roll_std_5, … | `core/engine/train_dhan_models.py` + `core/models/dhan/*_model_meta.json` |
| RF `*_rf.pkl` | similar + `side_enc` | `core/models/dhan/*_rf_meta.json` |
| Ultra RF | ~40 feats incl. `u_momentum_*`, `u_vol_*`, `u_rolling_win_rate_*`, hour/minute | `core/models/dhan_ultra/*_ultra_model_meta.json` |
| Blended v3 | 11 core price/moneyness feats | `core/models/dhan_real_blended/*_meta.json` |
| XGB v1 | 129 features (meta); classes BUY/HOLD/SELL | `models/xgboost_v1/*_xgb_meta.json` |

### D. Category coverage vs Q4 checklist

| Category | Status | Notes |
|----------|--------|-------|
| PRICE / momentum | PARTIAL | roll std, 1-step chg; no EMA/ROC/gap suite in GainRank |
| VOLATILITY | PARTIAL | ATM straddle IV proxy; real IV only if column present |
| VOLUME | PARTIAL | surge; VWAP missing |
| DERIVATIVES OI/PCR | PARTIAL | OI change + PCR; Greeks in signal engine path, not GainRank |
| MARKET REGIME | PARTIAL | `dhan_market_regime_classifier` optional in signal engine |
| LIQUIDITY | MISSING / PARTIAL | phase141 spread heuristic exists; not in GainRank |
| MULTI-TF | PARTIAL | `dhan_multi_timeframe_confirmation` optional; not GainRank |

**High-value gaps (inventory only):** purged IV rank with ≥20d, true session OI Δ, RVOL, cost-aware labels, walk-forward features. Do not add for novelty alone.

---

## Q5 — FEATURE VALIDATION

| Check | Status | Evidence |
|-------|--------|----------|
| Leakage / lookahead tests for GainRank factors | **MISSING** | No dedicated GainRank leakage tests found |
| Walk-forward leakage test (other engine) | PARTIAL | `tests/test_lifetime_research_engine.py::test_walk_forward_has_no_future_leakage` |
| Timestamp alignment (signal CSV ↔ ranker) | **NOT_PROVEN** | Schema mismatch; stale paper CSV |
| Expiry-day OI guard | WORKING (code) | `daily_gain_rank_and_validate.is_expiry_day()` disables OI Δ on Thu |
| Feature drift / correlation / sample size | **MISSING** | No production drift suite for these 7 factors |
| Perfect train accuracy red flag | **NOT_PROVEN** | Many metas show `accuracy`/`test_accuracy` = **1.0** on ~600 rows → likely leakage, label leakage, or toy data |

**Verdict Q5:** **NOT_PROVEN**

---

## Q6 — LABELS / TARGETS

| Label system | Definition | Horizon | File | Status |
|--------------|------------|---------|------|--------|
| GainRank target (implicit) | Rank underlyings by predicted % gain potential | Same-day / next validation vs NSE movers | `gain_rank_engine.py` + validator | PARTIAL |
| Market validation labels | Actual NSE top movers (volume/pChange composite) | EOD validation | `src/validation/market_result_validator.py` | PARTIAL (1 day) |
| `label_3class` / BUY_CE/BUY_PE/HOLD | Classifier target for `*_model.pkl` | Unclear vs forward return | `train_dhan_models.py` | NOT_PROVEN |
| Multi-res forward labels | `label_1/2/3/5` from `ltp.shift(-k)` → STRONG_BUY…STRONG_SELL | 1–5 steps | `core/engine/dhan_multi_resolution_labels.py` | PARTIAL (code); **lookahead by design** for training — must not be used as features |
| Ultra / RF labels | `label` / `pred_label` / `signal_label` | Mixed | `ultra_train_models.py` | NOT_PROVEN — risk of training on `pred_label` |
| Signal CSV `signal` | BUY/SELL + PAPER | Unclear | `storage/live/dhan_index_ai_signals.csv` | NOT_PROVEN |
| XGB BUY/HOLD/SELL | 3-class | Meta only | `models/xgboost_v1/*_xgb_meta.json` | NOT_PROVEN |

**Schema conflict (validation JSON):**
- Canonical writer field: `rank_correlation_spearman` — `src/validation/market_result_validator.py`
- On-disk historical file: `spearman_correlation` + `hit_rate` — `state/market_validations/market_validation_2026-06-12.json`
- Shim documents both: `src/ranking/market_result_validator.py`
- Dashboard/API handles both in places (`scripts/system3_model_to_trade_gap_proof.py`)

**Cost/slippage in labels:** **MISSING** for ML labels  
**Class balance treatment:** SMOTE helpers exist (`core/engine/ai_model/smote_balancer.py`) — usage in live retrain path **NOT_PROVEN**

**Verdict Q6:** **PARTIAL** (definitions exist; production target clarity + leakage protection **NOT_PROVEN**)

---

## Q7 — MODEL INVENTORY

**Do not call heuristics “AI/ML”.**

| Name | Algorithm | Code | Artifact(s) | Active? | Metrics on disk? | Leakage / honesty | Gap |
|------|-----------|------|-------------|---------|------------------|-------------------|-----|
| GainRank multi-factor | **Rules / weighted score** (not ML) | `src/ranking/gain_rank_engine.py` | `state/gain_rank_history.json` | Intended production ranker | Via validator ρ/hit | Neutral defaults (50) dilute signal | PARTIAL |
| ML confidence bridge | Aggregation of probs | `src/ranking/ml_signal_aggregator.py` | expects `dhan_index_ai_signals.csv` | Inactive (schema) | No | Stale PAPER CSV | NOT_PROVEN |
| Dhan baseline `*_model.pkl` | **GradientBoostingClassifier** | `core/engine/train_dhan_models.py` | `core/models/dhan/{NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY,SENSEX}_model.pkl` | Candidate / legacy | meta `test_accuracy` often 1.0 | Perfect accuracy + small n | NOT_PROVEN |
| Dhan RF `*_rf.pkl` | **RandomForest** | offline / ultra paths | `core/models/dhan/*_rf.pkl` | Candidate | `train_accuracy` 1.0 | Same | NOT_PROVEN |
| Dhan LSTM | **LSTM** (PyTorch `.pth`) | (paired meta) | `core/models/dhan/*_lstm_model.pth` | Unknown / unused in GainRank | meta only | Unclear wiring | NOT_PROVEN |
| Ultra models | **RandomForest** (`ultra_v3`) | `ultra_train_models.py` | `core/models/dhan_ultra/*_ultra_model.pkl` | Ensemble candidate | accuracy ~0.99 | Features include rolling win rate — leakage risk | NOT_PROVEN |
| Blended v3 | Classifier (via train pipeline) | `dhan_blended_model_trainer_v2.py` | `core/models/dhan_real_blended/*_blended_v3.pkl` | Candidate | accuracy 1.0; `num_real_rows: 0` in meta | Synthetic/empty provenance | NOT_PROVEN |
| XGBoost v1 | **XGBClassifier** | `system3_phase391_xgboost_training.py`, `ai_model/xgboost_trainer.py` | `models/xgboost_v1/*_xgb_model.pkl` + root `models/xgboost_model.pkl` | Ensemble candidate | accuracy/F1 = 1.0 | Perfect CM → not credible OOS | NOT_PROVEN |
| Ensemble (core) | Weighted Ultra/XGB/LGBM/Cat/RF/NN/Delta | `core/engine/ensemble_predictor.py` | loads above dirs | PARTIAL (LGBM/Cat/NN dirs **MISSING**) | dynamic tracker in-memory | Falls back to **heuristics** | PARTIAL |
| Ensemble (src/ml) | Similar + baseline heuristics | `src/ml/ensemble_predictor.py` | same | Dual path risk | logs `MODEL_FALLBACK_USED` | Heuristic fallback ≠ AI | PARTIAL |
| Phase 392 integration | Ultra 0.55 / XGB 0.40 / Delta 0.05 | `system3_phase392_ensemble_integration.py` | `models/xgboost_v1` | Candidate | phase metrics if run | Delta = heuristic | PARTIAL |
| Heuristic consensus | Rules | `system3_phase78_geni_consensus.py` | N/A | Optional | N/A | **Not AI** | WORKING as rules |
| Logistic regression | — | — | — | — | — | **No `LogisticRegression` in repo** | **MISSING** |
| LightGBM / CatBoost / NN dirs | Referenced | ensemble loaders | `core/models/lightgbm|catboost|neural_net` | No | — | Paths missing | **MISSING** |

**Cloud honesty probe:** `reports/latest/ml_model_truth_honesty/summary.json` → `model_proof_ready: false`, blocker `NO_PREDICTION_SOURCE_FOUND`.

---

## Q8 — MODEL TRAINING

| Step | Path / script | Status |
|------|---------------|--------|
| Historical data | `storage/training/dhan_index_options_training.csv`, blended preview CSV | **MISSING** on disk now |
| Feature gen | train_dhan / ultra_feature_engineering / ai_model | PARTIAL |
| Label gen | `dhan_multi_resolution_labels.generate_labels` | PARTIAL (forward shift OK for y only) |
| Split | `train_test_split(..., test_size=0.2, random_state=42, stratify=y)` | **NOT_PROVEN** for time-series (random split) |
| Walk-forward / purged / embargo | Not in `train_dhan_models.py` | **MISSING** |
| Fit | GB / RF / XGB / Ultra | Artifacts exist; retraining blocked without CSV |
| Auto retrain | `scripts/auto_retrain.py` → `train_blended_models()` | PARTIAL code; needs `storage/training/dhan_blended_training_preview.csv` ≥500 rows — **MISSING** → SKIP |
| Retrain trigger | `state/retrain_signal.json` from ρ&lt;0.40 × 3 days | Signal file **MISSING**; only 1 validation day |
| Calibration / registry / promotion | Informal meta JSON next to pkl | **MISSING** formal registry |
| Cost/slippage in train | — | **MISSING** |

**Verdict Q8:** **NOT_PROVEN** (pipeline scripts exist; current data prerequisites fail)

---

## Q9 — MODEL PERFORMANCE

### Institutional scoreboard (GainRank)

| Metric | Target | Observed evidence | Status |
|--------|--------|-------------------|--------|
| Spearman ρ | ≥0.70 (5+ days) | **1 day:** ρ=**0.20** (`state/market_validations/market_validation_2026-06-12.json`); API trend avg_rho=0.2 | **NOT_PROVEN** |
| Top-N hit rate | ≥70% | hit_rate **0.6667** (top-3) same day | PARTIAL / below target |
| Net P&amp;L | positive after costs | ANALYZER / paper | **NOT_PROVEN** |

**Files:**
- `C:\System3\Genesis_System3\state\market_validations\market_validation_2026-06-12.json`
- Live API snapshot: `reports/latest/quant_lifecycle_Q_20260816\live_api\accuracy_trend.json`
- Gap proof: `reports/latest/model_to_trade_gap/summary.md` (hit_rate 0.6667; trade expectancy not proven)

### Classifier metas (do **not** trust alone)

| Model family | Reported metric | Red flag |
|--------------|-----------------|----------|
| `*_model.pkl` | test_accuracy 1.0 | Overfit / leakage / toy |
| Ultra | accuracy ~0.99 | Same |
| XGB v1 | accuracy & macro_f1 1.0 | Same |
| Blended | accuracy 1.0, real_rows 0 | Invalid provenance |

ROC-AUC, PR-AUC, Brier, Sharpe, drawdown: **not** established for GainRank production path.

**Verdict Q9:** **NOT_PROVEN** (accuracy alone invalid; ρ sample size = 1)

---

## Q10 — MULTI-MODEL / TOURNAMENT

| Requirement | Status |
|-------------|--------|
| Same dataset / timestamps / costs / universe for A vs B vs C | **MISSING** |
| Fair tournament harness | No production tournament; phase366 evaluator is heuristic |
| Production vs baseline comparison | Cloud `compare_best_model` null / blocked (`ml_model_truth_honesty`) |
| Ensemble as “multi-model” | Code exists; many members missing; heuristic delta fallback |
| Dual ensemble implementations | `core/engine/ensemble_predictor.py` **and** `src/ml/ensemble_predictor.py` — risk of divergent behavior |

**Verdict Q10:** **MISSING** / **NOT_PROVEN**

---

## Cross-cutting gaps (priority)

1. **Validation sample:** only 1 day Spearman — floor claims (0.80 in `SYSTEM_STATE.md`) conflict with sole artifact ρ=0.20 → treat SYSTEM_STATE claim as **NOT_PROVEN** without new days.  
2. **Signal CSV schema drift** breaks ML factor.  
3. **Training CSV missing** → auto_retrain cannot run.  
4. **Random split + perfect accuracy** → treat all pkl families as **candidate / obsolete until OOS walk-forward**.  
5. **Heuristics** in ensemble fallback / GainRank / phase78 — label as **rules**, not AI.  
6. **No LogisticRegression** in codebase.  
7. **Validator field names** dual (`spearman_correlation` vs `rank_correlation_spearman`) — shim exists; historical JSON still old schema.

---

## Gap classification summary

| Area | Classification |
|------|----------------|
| Q4 Feature inventory (GainRank 7 factors) | **PARTIAL** |
| Q4 ML / model feature stores | **PARTIAL** |
| Q5 Feature validation | **NOT_PROVEN** |
| Q6 Labels | **PARTIAL** |
| Q7 Model inventory (artifacts on disk) | **PARTIAL** (files exist) / **NOT_PROVEN** (active proven) |
| Q7 Logistic | **MISSING** |
| Q7 LightGBM/CatBoost/NN artifacts | **MISSING** |
| Q8 Training loop | **NOT_PROVEN** |
| Q9 Spearman / hit rate | **NOT_PROVEN** (n=1 day) |
| Q10 Tournament | **MISSING** |

---

## Key absolute paths (quick index)

```
C:\System3\Genesis_System3\src\ranking\gain_rank_engine.py
C:\System3\Genesis_System3\src\ranking\ml_signal_aggregator.py
C:\System3\Genesis_System3\src\validation\market_result_validator.py
C:\System3\Genesis_System3\src\ranking\market_result_validator.py
C:\System3\Genesis_System3\scripts\daily_gain_rank_and_validate.py
C:\System3\Genesis_System3\scripts\auto_retrain.py
C:\System3\Genesis_System3\scripts\calibrate_factor_weights.py
C:\System3\Genesis_System3\core\engine\train_dhan_models.py
C:\System3\Genesis_System3\core\engine\dhan_blended_model_trainer_v2.py
C:\System3\Genesis_System3\core\engine\dhan_multi_resolution_labels.py
C:\System3\Genesis_System3\core\engine\ensemble_predictor.py
C:\System3\Genesis_System3\src\ml\ensemble_predictor.py
C:\System3\Genesis_System3\core\engine\system3_signal_engine.py
C:\System3\Genesis_System3\core\models\dhan\
C:\System3\Genesis_System3\core\models\dhan_ultra\
C:\System3\Genesis_System3\core\models\dhan_real_blended\
C:\System3\Genesis_System3\models\xgboost_v1\
C:\System3\Genesis_System3\state\market_validations\market_validation_2026-06-12.json
C:\System3\Genesis_System3\storage\live\dhan_index_ai_signals.csv
C:\System3\Genesis_System3\reports\latest\ml_model_truth_honesty\summary.json
```

No secrets included.