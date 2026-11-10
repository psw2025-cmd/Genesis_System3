# Genesis System3 — World-Class Prediction Implementation Backlog

This backlog implements `PREDICTION_WORLD_CLASS_BENCHMARK_POLICY.md` and complements Issues #25, #26 and #188. It does not authorize LIVE trading.

## Priority order

### P0-A — Market-data authority and historical lake
- Finish Issue #188 semantic market-data acceptance before relying on live prediction features.
- Durable point-in-time NSE/BSE cash, indices, futures and options intraday history.
- Full option contract history with expiry/strike/CE/PE/lot/instrument lineage.
- Dhan live market WebSocket and supported multi-level market-depth capture.
- Source/freshness/exchange-time/receive-time/schema lineage on every stored record.
- Explicit rate-limit, Retry-After, exponential backoff/jitter and circuit-breaker behavior.
- Zero synthetic/demo fallback in production labels/features.

**Exit:** reproducible time-range query + point-in-time replay can rebuild a feature row without future data.

### P0-B — Feature store and leakage authority
- Versioned multi-horizon feature store.
- Price/return/volatility, volume/liquidity, microstructure, options surface/OI/Greeks, cross-sectional, regime and event feature groups.
- Feature availability timestamps, freshness and missingness.
- Point-in-time replay, timezone, survivorship and label-leakage tests.
- Drift and feature-ablation evidence.

**Exit:** every champion feature is lineage-complete, leakage-tested and proves incremental OOS value.

### P0-C — Label authority
- Explicit horizon-specific targets.
- Cost-aware direction labels and forward-return/ranking/volatility/options/regime targets.
- Expiry-aware labels for derivatives.
- No future-chain or end-of-day knowledge in intraday labels.

**Exit:** every model declares target, horizon and label version/hash.

### P1-A — Champion/challenger tournament
- Baselines: random walk/persistence, linear/logistic, GainRank heuristic.
- Strong tabular: XGBoost/LightGBM/CatBoost where approved.
- Temporal challengers: N-BEATS/N-HiTS, PatchTST/iTransformer.
- Foundation challengers: current approved TimesFM/Chronos/Moirai class models where usable.
- Microstructure: simple MLP/LSTM plus TLOB/LOB-transformer-style challengers when genuine depth history exists.
- Same dataset/window/horizon/cost assumptions for all candidates.

**Exit:** reproducible tournament identifies champion by multi-gate OOS evidence, not architecture reputation.

### P1-B — Evaluation integrity and economic truth
- Rolling-origin/walk-forward plus purging/embargo.
- CPCV/CSCV or comparable overfitting diagnostics when applicable.
- PBO/deflated performance diagnostics where appropriate.
- Predictive: IC/rho, top-K, MAE/RMSE/quantile, precision/recall/F1, Brier/log-loss/calibration.
- Economic: costed P&L, Sharpe/Sortino, max drawdown, profit factor, expectancy, turnover/capacity.
- Confidence intervals, regime/symbol/expiry stability and optimism-gap reporting.

**Exit:** no promotion from one metric or one test window.

### P1-C — Calibration, uncertainty, OOD and abstention
- Probability calibration tournament.
- Quantile/prediction intervals.
- Adaptive/time-series conformal challengers.
- OOD/regime-shift detection.
- Fail-closed abstain/no-trade state for high uncertainty or poor data quality.

**Exit:** confidence score has empirical reliability and coverage proof.

### P1-D — Immutable prediction ledger
Every paper/production prediction records prediction ID, as-of, horizon, instrument context, data/feature/model/strategy versions and hashes, prediction/confidence/interval, decision/abstain, cost assumptions and realized result.

**Exit:** every aggregate accuracy metric reconciles to row-level immutable predictions.

### P1-E — Continuous paper lifecycle
- Prediction → candidate → paper decision → simulated fill → exit → costed result.
- Daily/weekly/monthly champion monitoring.
- DATA/FEATURE/MODEL/REGIME/CALIBRATION/COST/INFRA error taxonomy.
- Automatic rollback recommendation and challenger re-evaluation when degradation gates fail.

**Exit:** continuous market-day proof demonstrates stability before any separate LIVE discussion.

### P2-A — Reproducible cloud MLOps
- Durable dataset/model registry.
- Champion/challenger/rollback metadata.
- Immutable hashes, training image/environment, seed and config.
- Experiment matrix and point-in-time dataset versions.
- Compact retention-aware evidence; no mystery pickle authority.

### P2-B — Alternative data challengers
Only after P0 market-data/feature integrity is strong: point-in-time licensed news, macro, fundamentals, corporate events, sentiment/LLM-derived and graph features. Each requires ablation and OOS proof.

## Permanent metric principle

The target is not “maximum raw prediction accuracy.” The target is **repeatable, calibrated, statistically credible and economically positive OOS performance after realistic costs**, with an abstain state when evidence is weak.

## Dependencies
- #188 — market-data/broker/UI semantic authority.
- #25 — master paper/analyzer readiness roadmap.
- #26 — daily prediction-vs-actual benchmark; must be expanded beyond rho/hit-rate into the evaluation contract above.

## Safety
ANALYZE/PAPER only. No LIVE/order enablement is part of this backlog.
