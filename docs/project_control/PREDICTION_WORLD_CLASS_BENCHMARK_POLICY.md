# Genesis System3 — World-Class Prediction Benchmark & Accuracy Policy

**Authority:** Permanent prediction/data/feature/model engineering contract for Genesis System3.

## Objective

System3 must optimize for **repeatable out-of-sample economic value with calibrated uncertainty**, not headline classification accuracy. No model, feature, data source, strategy, or AI technique is promoted because it is new, complex, or described as state of the art.

Every material prediction change must be compared on the same point-in-time dataset against simple baselines, the current champion, and relevant contemporary challengers. A challenger wins only if measured improvement survives leakage controls, realistic costs, regime splits, uncertainty calibration, and reproducibility checks.

## Permanent world-best comparison rule

Before a material data/feature/model/prediction promotion, agents must:

1. Fresh-review current primary research and official provider/model documentation relevant to the change.
2. Update a challenger matrix covering simple statistical/tabular baselines and relevant current time-series/microstructure models.
3. Never claim a model is “world best” from reputation, paper headline, architecture size, or one benchmark.
4. Require the same-window, same-data, same-cost, same-horizon tournament before champion selection.
5. Record comparison date, source/version/model and reproducible configuration.
6. Treat external model improvements as research candidates until System3’s own point-in-time out-of-sample evidence proves value.

## P0 — Data truth and historical lake

Prediction promotion is blocked when data is incomplete, stale, synthetic, mislabeled, or not reproducible.

Required coverage:
- timestamped instrument-master snapshots with exchange, segment, lot/tick size, expiry and corporate-action lineage;
- NSE/BSE cash equities, indices, futures and broker-supported option underlyings;
- full option chains by expiry/strike/CE/PE with LTP, volume, OI/change OI, bid/ask, IV and Greeks where genuinely supplied;
- broker WebSocket market feed and, where licensed/supported, multi-level order-book depth;
- durable intraday OHLCV/tick/order-book history rather than transient runtime cache only;
- survivorship-safe, point-in-time universe snapshots;
- source, exchange timestamp, receive timestamp, freshness, quality state and schema version;
- no production target/feature silently filled by synthetic/demo/fabricated values;
- rate-limit aware ingestion with Retry-After/backoff/jitter/circuit breaking and replay-safe collectors.

## P0 — Versioned point-in-time feature store

Every production feature requires version, as-of timestamp, source lineage, availability timestamp, missingness rule, leakage test and freshness rule.

Feature families to benchmark, not blindly enable:

### Price / return / volatility
- multi-horizon returns, momentum and residual momentum;
- realized volatility, range, gaps, ATR and volatility-of-volatility;
- trend strength and mean-reversion state.

### Volume / liquidity / microstructure
- volume, relative volume and VWAP distance;
- spread, microprice, queue/depth imbalance;
- order-flow imbalance, depth slope/convexity and queue pressure when depth exists;
- trade/quote intensity and short-horizon liquidity stress.

### Derivatives / options
- OI and change-OI distributions;
- PCR by strike/expiry and normalized OI concentration;
- futures basis/carry where applicable;
- ATM IV, IV rank/percentile, skew, smile and term structure;
- risk-reversal/butterfly-style surface summaries where mathematically valid;
- aggregate delta/gamma/theta/vega exposure features from genuine chain data;
- expiry/time-to-expiry, moneyness and strike-distance;
- option-surface latent factors only after arbitrage/quality checks.

### Cross-sectional / cross-asset
- breadth, sector relative strength, beta/correlation;
- index/sector/VIX relationships;
- relative ranking and residual-return features;
- related-series context only when it improves OOS results without leakage.

### Regime / event / time
- volatility, trend, liquidity and correlation regimes;
- time-of-day, day-of-week and expiry-day state;
- scheduled macro/corporate events only from point-in-time-safe sources;
- market-open/close/auction state.

### Data-quality guards
- feature age, missingness, stale-source indicators and data confidence;
- out-of-distribution distance and regime confidence.

## P0 — Feature integrity gates

Mandatory before promotion:
- no future information/look-ahead;
- training-only fitting of scalers/encoders/normalizers;
- point-in-time replay test;
- timestamp/timezone consistency;
- no universe survivorship leakage;
- no label-derived feature leakage;
- feature drift monitoring for distribution and missingness;
- permutation/SHAP or equivalent stability analysis where appropriate;
- redundancy/correlation review;
- feature ablation proving incremental OOS contribution.

## P1 — Explicit labels and horizons

Every model must declare explicit targets and prediction horizons. Research target classes may include:
- forward return/regression;
- direction only when move exceeds realistic spread/fees/slippage threshold;
- top-K/cross-sectional ranking;
- realized volatility/risk;
- option premium or IV movement;
- regime classification;
- meta-label trade/no-trade or abstention.

Labels must be horizon-specific, expiry-aware where relevant, cost-aware, reproducible and free of future-chain knowledge.

## P1 — Champion/challenger tournament

Every tournament must include simple baselines and relevant advanced challengers.

Minimum baselines:
- naive/random-walk/persistence;
- linear/logistic models;
- current GainRank heuristic;
- tree/tabular models such as XGBoost/LightGBM/CatBoost when technically/licensing suitable.

Relevant temporal challengers may include:
- N-BEATS/N-HiTS;
- PatchTST/iTransformer;
- current open/approved time-series foundation models such as TimesFM, Chronos or Moirai families where technically and legally usable.

Relevant high-frequency challengers may include:
- simple MLP/LSTM microstructure baselines;
- LOB-transformer/TLOB-style architectures when genuine order-book history exists.

Advanced models are not promoted unless they beat simple baselines and the current champion on System3’s own OOS economic and calibration gates.

## P1 — Evaluation integrity

A single accuracy, hit-rate or Spearman threshold is never sufficient for promotion.

### Predictive metrics
- Spearman/Pearson IC for ranking/continuous targets;
- top-K hit/recall/precision;
- MAE/RMSE or pinball/quantile loss;
- precision/recall/F1 for actionable classes;
- Brier score/log loss and calibration error for probabilities.

### Economic metrics
- P&L after brokerage, exchange fees, taxes/charges, spread, slippage and latency assumptions;
- Sharpe/Sortino, max drawdown, profit factor, expectancy, turnover and capacity/liquidity;
- separate gross and net results.

### Robustness gates
- rolling-origin/walk-forward proof;
- purging and embargo consistent with label horizon;
- CPCV/CSCV or equivalent overfitting diagnostics where suitable;
- probability of backtest overfitting / deflated performance diagnostics where suitable;
- regime-by-regime results;
- bootstrap/confidence intervals and statistical-significance checks;
- stability across symbols, expiries and time periods;
- explicit optimism gap between research and untouched test/live-paper windows.

## P1 — Uncertainty, abstention and OOD

A prediction without calibrated uncertainty is not production-complete.

Require as appropriate:
- probability calibration such as Platt/isotonic/beta-style challengers;
- prediction/quantile intervals;
- adaptive/time-series conformal challenger methods for coverage under drift;
- OOD/regime-shift detector;
- abstain/no-trade when uncertainty, data quality or OOD risk exceeds policy limits.

Confidence must never be a cosmetic score detached from empirical reliability.

## P1 — Immutable prediction ledger

Every evaluated production/paper prediction must carry:
- `prediction_id`;
- event/as-of timestamp and horizon;
- symbol/instrument/expiry/strike context as applicable;
- data snapshot or lineage hash;
- feature-set version/hash;
- model/ensemble version and artifact hash;
- strategy/ranker version;
- raw prediction, calibrated probability/confidence and interval;
- decision/abstain state;
- cost assumptions;
- realized outcome and evaluation timestamp.

No model may be declared better from aggregate dashboard numbers if row-level prediction lineage is absent.

## P1 — Regime-aware monitoring and self-correction

Continuous PAPER/ANALYZE monitoring must classify degradation into DATA, FEATURE, MODEL, REGIME, COST/EXECUTION, CALIBRATION and INFRA categories.

Self-correction means bounded retraining/recalibration/challenger evaluation under governance. It never means uncontrolled code mutation, automatic LIVE enablement, or automatic capital deployment.

Champion rollback must be available when post-promotion paper evidence violates agreed degradation gates.

## P2 — Reproducible MLOps

Required maturity:
- durable cloud-backed dataset/artifact registry;
- model registry with champion/challenger/rollback records;
- immutable artifact hashes;
- reproducible training environment/image and seed/config capture;
- experiment registry and comparison matrix;
- point-in-time dataset versioning;
- compact, storage-retention-aware training/evaluation evidence;
- no unidentified pickle/model file may become production authority.

## P2 — External / alternative data

News, sentiment, macro, fundamentals, corporate events, graph relationships and LLM-derived features are optional challengers, not prerequisites. Add them only when source/licensing is acceptable, timestamps are point-in-time safe, revision semantics are understood, ablation proves incremental OOS value, and they do not distract from P0 market-data/microstructure/data-quality gaps.

## Promotion law

A candidate may progress only when all applicable gates are green:

`DATA -> LINEAGE -> FEATURE -> LEAKAGE -> LABEL -> TOURNAMENT -> OOS -> COST -> CALIBRATION -> ROBUSTNESS -> PAPER -> UI/API TRUTH -> CHAMPION`

Any failed stage returns the candidate to investigation; it is never bypassed by a high headline accuracy number.

## Safety

- ANALYZE/PAPER remains authoritative.
- LIVE and order placement remain disabled unless separately and explicitly approved through existing live-trading governance.
- Prediction research must never weaken broker, risk, IAM, secret or trading safety controls.
