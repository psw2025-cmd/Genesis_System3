# Q2–Q10 — Quality, History, Features, Labels, Models

## Q2 Data quality — **PARTIAL**
Implemented guards (examples): same-day OI cache skip, 3-day staleness, Thursday expiry guard (`nse_provider` / oi cache tests), UDiFF IDO filter fixes, paced OC.
Remaining risks: fallback falsely labelled Dhan; synthetic leakage; CE/PE asymmetry not continuously proven on full universe; timezone IST vs UTC labeling in stores.

## Q3 Historical data — **PARTIAL / INSUFFICIENT for institutional WF**
| Asset class | Reality |
|-------------|---------|
| Index options EOD | Bhavcopy days in `storage/bhavcopy/` |
| Equities multi-year tick | **MISSING** as production lake |
| Options contract-level intraday | **MISSING** |
| Supports training? | **PARTIAL** (blended CSV + bhavcopy signals) |
| Supports walk-forward options BT? | **NOT_PROVEN / NO** at institutional bar |

## Q4 Features — **PARTIAL**
Primary production ranker: `src/ranking/gain_rank_engine.py` factors (OI, IV proxy, volume, PCR, premium, momentum, **ml_confidence**).
Bridge: `src/ranking/ml_signal_aggregator.py` from `dhan_index_ai_signals.csv`.
Multi-timeframe feature store (1m…daily versioned): **MISSING**.
High-value missing (do not invent blindly): calibrated IV smile, depth, stable regime features with leakage tests.

## Q5 Feature validation — **PARTIAL / NOT_PROVEN**
Unit tests cover bhavcopy/OI/datasource fallback. Systematic leakage/lookahead/feature-drift suite for all features: **NOT_PROVEN**.

## Q6 Labels — **PARTIAL**
Primary label/eval: Spearman ρ vs actual top movers + top-N hit rate (`market_result_validator`).
Many Q6 example labels (N-minute return, CE/PE direction, etc.): **NOT_PROVEN** as production targets.
If target unclear → model result **NOT_PROVEN** (applies to several experimental paths).

## Q7 Model inventory
| Name | Type | File / artifact | Active in prod rank? | Class |
|------|------|-----------------|----------------------|-------|
| GainRankEngine | Heuristic | `gain_rank_engine.py` | **YES** | WORKING (heuristic ≠ AI) |
| ml_signal_aggregator | Bridge | `ml_signal_aggregator.py` | optional factor | PARTIAL |
| EnsemblePredictor | ML ensemble | `src/ml/ensemble_predictor.py` + pickles | not sole SSOT | PARTIAL |
| Blended trainers | ML train | `core/engine/dhan_blended_model_trainer_v2.py` → `core/models/dhan/*.pkl` | host-dependent | PARTIAL |
| Phase XGB etc. | Experimental | `storage/models/…` | not daily SSOT | PARTIAL / DEAD_RUNTIME |

## Q8 Training — **PARTIAL**
Path: history CSV → train → pickles → optional auto_retrain at 16:00 IST if `state/retrain_signal.json`.
Gaps: purged/embargo splits **NOT_PROVEN**; MLflow registry **MISSING**; Cloud durable artifact store **MISSING**.

## Q9 Performance — **PARTIAL**
Live `/api/accuracy_trend`: avg_rho, trend, retrain_needed, days_available.
Dashboard Accuracy/Performance tabs consume ρ / hit rate.
Full suite (Sharpe, Sortino, costed PF, calibration curves) as promotion metrics: **NOT_PROVEN**.

## Q10 Multi-model tournament — **MISSING / NOT_PROVEN**
No fair same-window tournament harness proven as gate for champion selection.

## Live snapshot fields (this session)
See `supporting/accuracy_trend.json`, `supporting/gain_rank.json`, `supporting/system_health.json`.
