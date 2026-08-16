# Genesis System3 — Q11–Q20 Strategy / Backtest / Paper / Promotion Audit

**Trees audited:** `C:\System3\Genesis_System3` (primary), `C:\System3\Genesis_System3_broker_permfix` (exists; mirrors same strategy/paper/backtest filenames).  
**Mode:** READ-ONLY code + on-disk proof. No secrets. No LIVE enablement advice beyond documenting gates.

**Top-line verdict:** Runtime path is **analyzer + paper**. Primary “strategy” is **GainRank heuristics + PCR/OI `StrategyEngine`** (`BUY_CE` / `BUY_PE` / `IRON_CONDOR`). Institutional champion/promotion is **partial / paper-only**. `LIVE_TRADING_ENABLED` / live-exec flags remain **false**. Prediction-vs-actual durable history is **thin** (1 validation day).

---

## Classification legend

| Tag | Meaning |
|-----|---------|
| `ACTIVE_RUNTIME` | Wired into scheduler / live chain / dashboard production path |
| `PAPER_ONLY` | Executes or records paper/sim only |
| `BACKTEST_ONLY` | Offline proof / research; not order path |
| `DEAD_CODE` | Present; no durable wiring / no result artifacts found |
| `UNKNOWN` | Exists; callers unclear or dual-use |

---

## Q11 — STRATEGY INVENTORY

| Strategy / logic | Key files | Market / instruments | Entry / exit / risk (as coded) | Class |
|------------------|-----------|----------------------|--------------------------------|-------|
| **GainRank multi-factor ranker** | `C:\System3\Genesis_System3\src\ranking\gain_rank_engine.py`; `scripts\daily_gain_rank_and_validate.py`; scheduler job | Index options underlyings NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY | Weighted OI/IV/volume/PCR/premium/momentum/`ml_confidence`; ranks symbols (not option legs) | `ACTIVE_RUNTIME` |
| **StrategyEngine PCR/OI sentiment** | `C:\System3\Genesis_System3\src\selector\strategy_engine.py`; used by `scripts\run_live_chain.py` | Index option chain DF | Entry: bullish→`BUY_CE`, bearish→`BUY_PE`, neutral+liq→`IRON_CONDOR`; SL=70% of mid, target=150% mid; filters on confidence/liquidity | `ACTIVE_RUNTIME` + `PAPER_ONLY` (via PaperExecutor) |
| **ML confidence bridge** | `src\ranking\ml_signal_aggregator.py` → GainRank | Same | Reads `dhan_index_ai_signals.csv` probs → 0–100 factor | `ACTIVE_RUNTIME` (optional factor) |
| **EnsemblePredictor** | `src\ml\ensemble_predictor.py` | Models under `core\models\dhan\` | Classifiers if pickles present; not sole GainRank SSOT | `UNKNOWN` / partial runtime |
| **10k StrategyOptimizer grid** | `scripts\optimize_10k_strategies.py`, `scripts\final_best_strategy_selector.py`, `scripts\world_class_optimizer.py` | Param grid (Kelly/ATR/IV/ML confidence…) | Offline tournament; `outputs\strategy_optimization_results.json` **MISSING** | `DEAD_CODE` / experimental offline |
| **dhan_strategy_optimizer** | `core\engine\dhan_strategy_optimizer.py` | Ultra/menu path | Separate StrategyOptimizer class | `UNKNOWN` |
| **Lifetime research champion** | `dashboard\backend\lifetime_research_engine.py`; `scripts\system3_lifetime_research_runner.py`; policy `config\lifetime_research_policy.json` | Historical outcome rows | Walk-forward gates → **paper champion only** | `BACKTEST_ONLY` / paper promotion |
| **Phase strategy ensemble** | `core\engine\system3_phase366_strategy_ensemble_evaluator.py` | Phase runner | Research phase | `BACKTEST_ONLY` |
| **Duplicates** | Same BUY_CE/PE/IC names appear in StrategyEngine + optimizer entry labels + docs; GainRank vs Ensemble are **parallel**, not one stack | — | — | Note |

**UI visibility:** Paper / Backtest React tabs — `dashboard\frontend\src\components\PaperTrading.tsx`, `Backtest.tsx`. Gain rank / accuracy APIs in `dashboard\backend\app.py` (`/api/gain_rank`, `/api/accuracy_trend`).

---

## Q12 — STRATEGY DISCOVERY / BEST-STRATEGY SEARCH

| Mechanism | Path | Evidence status | Class |
|-----------|------|-----------------|-------|
| 10k combinatorial optimizer | `scripts\optimize_10k_strategies.py` | No `outputs\strategy_optimization_results.json` | `DEAD_CODE` |
| Final best selector | `scripts\final_best_strategy_selector.py` → `outputs\final_best_strategy.json` | Depends on missing 10k outputs | `DEAD_CODE` |
| Lifetime research tournament | `lifetime_research_engine.select_champion` | Policy thresholds exist; paper-only; blocks if LIVE env unsafe | `BACKTEST_ONLY` (implemented) |
| GainRank daily rank | `daily_gain_rank_and_validate.py` | Production analyzer ranking — **not** a strategy tournament | `ACTIVE_RUNTIME` |

**Finding:** No proven multi-family OOS tournament (trend/mean-rev/IV/skew/etc.) with cost-sensitive robustness. Do not treat “best strategy” scripts as runtime authority.

---

## Q13 — BACKTEST (engines + costs + lookahead)

### Engines

| Engine | Path | Costs in code? | Lookahead / realism | Class |
|--------|------|----------------|---------------------|-------|
| **Costed walk-forward proof** | `scripts\costed_walkforward_proof.py` → `reports\latest\recent_backtest_walkforward_proof\costed_walkforward_proof.json` | **Yes:** ₹20/side brokerage, STT 0.0625% sell, exch txn, 18% GST on brokerage+exc, SEBI, 0.1% slippage both sides | Day N **close** entry + day N+1 close exit; signal = max `oi_chg` CE on day N (EOD); **no stamp duty**; **no bid/ask**; label says “ATM” but code is OI-chg rank | `BACKTEST_ONLY` |
| **PF-gated backtest** | `scripts\pf_gated_backtest.py` (PF≥1.20, phantom premium guard, ATM band) | Same cost model + honesty gate | Same EOD close-to-close pattern; `pf_gated_backtest.json` **MISSING** on disk | `BACKTEST_ONLY` (code present, proof not present) |
| **Phase 280** | `core\engine\system3_phase280_strategy_backtester.py` | **No** | Sums `forward_return_1` on `pred_label` rows — leakage risk if labels not purged | `BACKTEST_ONLY` |
| **Dashboard BacktestingEngine** | `dashboard\backend\backtesting.py` | **No** (no STT/brokerage/slippage) | Same-bar entry at row price | `BACKTEST_ONLY` / UI |
| **Synthetic Dhan backtester** | `core\engine\dhan_synthetic_backtester.py` | **No** cost grep hits | **Fabricated** random-walk spots/options | `BACKTEST_ONLY` / synthetic |
| **Ultra sampler** | `core\engine\system3_phase383_ultra_backtest_sampler.py` | Phase research | — | `BACKTEST_ONLY` |

### Cost claims vs code (costed walk-forward)

| Checklist item | Present in `costed_walkforward_proof.py`? |
|----------------|-------------------------------------------|
| Brokerage | Yes (flat ₹20/side) |
| STT | Yes (sell-side) |
| Exchange + GST + SEBI | Yes |
| Slippage | Yes (0.1% value) |
| Stamp duty | **No** |
| Bid/ask / spread | **No** (uses close) |
| Liquidity / OI / volume filters | Partial (CE close>10; OI_chg sort only) |
| Lot size | Yes (hardcoded map) |
| Historical contract match | Yes (strike+expiry on next day) |
| “No future data” | **Partial:** exit uses next day only; **entry at same-day close after EOD signal = same-bar/EOD bias** |
| Intrabar / stop ordering / gaps | **Not modeled** |

**Proof artifact:** `C:\System3\Genesis_System3\reports\latest\recent_backtest_walkforward_proof\costed_walkforward_proof.json` — `pass: true`, `costs_slippage_included_proven: true`, but note field says *“Not a performance claim”*; net PnL strongly negative on 5 bhavcopy days.  
**Master orchestrator** treats this as gate evidence: `scripts\system3_master_proof_orchestrator.py` → `gate_backtest_walkforward`.

**Contrast:** `tools\model_benchmark_leaderboard.py` still hard-codes reasons: *“walk-forward benchmark not yet implemented”*, *“cost/slippage P&L benchmark not yet implemented”*, *“promotion gate not yet implemented”* — meaning **ML leaderboard path ≠ costed bhavcopy proof path**.

---

## Q14 — WALK-FORWARD / ROBUSTNESS

| Item | Status |
|------|--------|
| Day N → N+1 roll on bhavcopy | Implemented in `costed_walkforward_proof.py` (5 days → 8 trades) |
| TRAIN→VALIDATE→TEST→ROLL formal splits | **Not** in costed proof; **partial** in `lifetime_research_engine` (`min_walk_forward_windows: 3` in policy) |
| Regime labels (bull/bear/vol/expiry week) | **Missing** as enforced gates |
| PF honesty gate | Code in `pf_gated_backtest.py`; proof file **missing** |
| Sample size | Tiny (5 EOD days) — insufficient for robustness claims |

---

## Q15 — PREDICTION VS ACTUAL

| Store | Path | On-disk evidence | Schema vs Q15 ideal |
|-------|------|------------------|---------------------|
| Predictions / ranks | `C:\System3\Genesis_System3\state\gain_rank_history.json` | **EXISTS** (~9KB, 12 dated snapshots; sample from 2026-06-12) | Rank + gain_score + recommendation — **no** `prediction_id` / model_version / horizon / probability per trade |
| Actual outcomes | `C:\System3\Genesis_System3\state\market_validations\` | **1 file:** `market_validation_2026-06-12.json` | `spearman_correlation: 0.2`, `hit_rate: 0.6667`, `status: RETRAIN_NEEDED` |
| Writers | `src\validation\market_result_validator.py`; `src\ranking\gain_rank_engine.py`; `scripts\daily_gain_rank_and_validate.py` | — | Retrain if ρ&lt;0.40 for 3 days → `state\retrain_signal.json` |
| Consumers | `dashboard\backend\app.py` `/api/accuracy_trend`, `/api/gain_rank`; `scripts\daily_prediction_benchmark.py`; `scripts\system3_gate_evaluator.py` | — | Dual keys `spearman_correlation` \| `rank_correlation_spearman` |
| Per-prediction error ledger | Q15 full fields | **MISSING** | No durable prediction_id→actual return store |

---

## Q16 — SELF-LEARNING (safe definition)

| Component | Path | Behavior vs safe loop | Class |
|-----------|------|----------------------|-------|
| Validation → retrain signal | `market_result_validator` → `state\retrain_signal.json` | Evidence-gated signal | `ACTIVE_RUNTIME` (when job runs) |
| Auto retrain | `scripts\auto_retrain.py` (scheduler 16:00) | Train only if signal + ≥500 blended CSV rows; clears signal | `ACTIVE_RUNTIME` / controlled |
| ContinuousLearningSystem | `continuous_learning_system.py` | Doc claims auto model update from paper trades; invoked from `dashboard\backend\app.py` / `runner.py` | `UNKNOWN` / riskier path — **not** full champion gate |
| Ultra safety | `core\engine\ultra_safety.py` defaults | `AUTO_RETRAIN_MODELS: False`, `AUTO_PROMOTE_MODELS: False` | Safe defaults |
| Immutable history append → challenger → promote | Blueprint | **PARTIAL** at best; no MLflow registry | — |

---

## Q17 — CHAMPION / CHALLENGER

| Piece | Path | Status |
|-------|------|--------|
| Paper champion selector | `dashboard\backend\lifetime_research_engine.py` `select_champion` | Implemented; `paper_only: true`; refuses unsafe LIVE env |
| Policy | `config\lifetime_research_policy.json` | min hit_rate 0.55, PF 1.15, WF windows 3; *live blocked until separate human approval* |
| Ultra Baseline vs Ultra promote | `core\engine\ultra_promotion_manager.py` | Manual keyword; `AUTO_PROMOTE_MODELS` false by default |
| Model registry / hash rollback | — | **MISSING** institutional registry |
| “NO MODEL READY” | lifetime research `BLOCKED` status | Supported in runner |

---

## Q18 — SELF-CORRECTION

| Expected (error taxonomy → regression) | Found |
|----------------------------------------|-------|
| DATA/FEATURE/MODEL/REGIME… classifiers | **Not** implemented as a structured correction engine |
| Retrain on low ρ | Yes (`RETRAIN_NEEDED` / `auto_retrain.py`) |
| Feature/label fix workflow with mandatory regression | **MISSING** as codified Q18 loop |

Closest related: drift analyzers under `core\engine\` (phase335, etc.) — research phases, not production correction SOP.

---

## Q19 — PAPER / SIMULATION

| Stage | Path | Notes | Class |
|-------|------|-------|-------|
| Signal → paper fill | `scripts\run_live_chain.py` + `src\trading\paper_executor.py` | Slippage only (0.1%); **no STT/brokerage/GST** in PaperExecutor | `PAPER_ONLY` |
| Dashboard paper ledger | `dashboard\backend\paper_pipeline_v8.py`, `cloud_paper_engine.py` | Explicitly no broker place/modify/cancel; needs live option quote | `PAPER_ONLY` / `ACTIVE_RUNTIME` (API) |
| Lifecycle proof | `scripts\paper_lifecycle_proof.py`; `reports\latest\analyzer_paper_lifecycle_proof\` | `full_lifecycle_proven: false`; warnings include full signal→exit PnL not proven | `PAPER_ONLY` — **not fully proven** |
| Fixtures / tests | `tests\test_paper_pipeline_v8_dhan_only.py`, fixtures | Unit/contract | — |
| Config | `config\live_trade_config.py` | Documents paper mode; live flags false | — |

**Reconciliation:** Production readiness still lists `REAL_PAPER_LIFECYCLE_NOT_PROVEN` in places; human gate still requires `REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF`.

---

## Q20 — PROMOTION GATE + LIVE FLAGS

### LIVE flags (still false — documented only)

| Flag / artifact | Value |
|-----------------|-------|
| `config\live_trade_config.py` `LIVE_TRADING_ENABLED` | `False` |
| `USE_LIVE_EXECUTION_ENGINE` | `False` |
| `config\live_trade_config.json` `LIVE_TRADING_ENABLED` | `false` |
| Ultra defaults `AUTO_EXECUTE_TRADES` / `AUTO_PROMOTE_MODELS` | `False` |
| `reports\latest\production_grade_readiness\summary.json` | `live_trading_enabled: false`, `production_ready_for_real_money: false`, mode `ANALYZER_PAPER_ONLY` |
| `reports\latest\human_approval_gate\summary.json` | Human approval true **but** `live_trading_env_flip_authorized: false`, `production_ready_for_real_money: false` |
| `dashboard\backend\routers\ml.py` | `ready_for_live: False` always in response construction |

### Technical gates still required (from human_approval proof)

- `REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF`
- `ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS` (only **1** validation day on disk; ρ=0.20)
- `POSITIVE_NET_EXPECTANCY_AFTER_ALL_COSTS`
- `WEBSOCKET_TICK_HEALTH_PROVEN`

### Gate evaluators (code)

- `scripts\system3_gate_evaluator.py` — Spearman ≥0.70 over 5 days, paper lifecycle, expectancy, etc.
- `scripts\system3_master_proof_orchestrator.py` — includes costed walk-forward gate
- `tools\model_benchmark_leaderboard.py` — explicitly: **promotion gate not yet implemented**
- Lifetime policy: paper champion ≠ live promotion

**Q20 checklist (DATA/FEATURE/LEAKAGE/…/MULTI-AGENT):** **Not** implemented as a single enforced promotion FSM. Scattered proofs + human gate + false LIVE flags.

---

## Cross-tree note (`Genesis_System3_broker_permfix`)

Parallel copies observed for: `scripts\costed_walkforward_proof.py`, `pf_gated_backtest.py`, `optimize_10k_strategies.py`, `src\selector\strategy_engine.py`, `src\trading\paper_executor.py`, `dashboard\backend\paper_pipeline_v8.py` / `backtesting.py`, promotion phase modules. Treat **main tree** as SSOT unless a specific permfix delta is proven by hash/diff.

---

## Evidence snapshot (non-secret)

| Artifact | Result |
|----------|--------|
| `state\gain_rank_history.json` | Present (12 entries) |
| `state\market_validations\*.json` | 1 day (2026-06-12), ρ=0.20 |
| `costed_walkforward_proof.json` | PASS (pipeline/cost mechanics), not performance |
| `pf_gated_backtest.json` | Missing |
| `outputs\strategy_optimization_results.json` | Missing |
| Live / production_ready flags | All false |

---

## Concise matrix: Q11–Q20 readiness

| Q | Topic | Verdict |
|---|-------|---------|
| Q11 | Strategy inventory | GainRank + StrategyEngine active; many optimizers dead/unknown |
| Q12 | Discovery tournament | Not proven as runtime; lifetime research paper-only |
| Q13 | Backtest costs | Costed WF: partial realistic costs; other engines: no costs / synthetic |
| Q14 | Walk-forward | Thin EOD proof; no regime robustness |
| Q15 | Pred vs actual | Stores exist; history too thin; schema incomplete vs checklist |
| Q16 | Self-learning | Controlled retrain signal path yes; uncontrolled continuous learner present |
| Q17 | Champion/challenger | Paper champion engine yes; full registry/promote no |
| Q18 | Self-correction | Taxonomy loop missing |
| Q19 | Paper | Code paths exist; full market-day lifecycle **not** fully proven |
| Q20 | Promotion / LIVE | Gates documented; LIVE remains false; no single institutional promote FSM |