# Prediction, Teacher/Label, Backtesting, and Accuracy Gap Protocol

**Purpose:** Define mandatory proof requirements for System3 prediction data, teacher/label creation, backtesting, walk-forward validation, accuracy metrics, probability calibration, drift monitoring, and dashboard accuracy claims.

**Safety rule:** This protocol is for Analyzer/Paper validation only. It does not authorize real order placement.

---

# Core issue

A model is not proven because it prints a score, shows a green dashboard badge, or has one profitable-looking backtest.

System3 prediction readiness requires proof of:

- data correctness
- teacher/label correctness
- feature timestamp correctness
- no look-ahead leakage
- temporal/walk-forward validation
- realistic options contract replay
- costs, spread, slippage, and no-fill risk
- probability calibration
- rank stability
- regime coverage
- paper-vs-backtest consistency
- model drift monitoring
- promotion governance

---

# Source-based facts that must shape System3

## Fact 1 — Time-series validation must not train on future data

Scikit-learn documents TimeSeriesSplit as a cross-validator for time-ordered data because other cross-validation methods are inappropriate when they would train on future data and evaluate on past data.

System3 rule:

```text
Random split on market time-series = NOT_PROVEN unless explicitly leakage-safe.
```

Required artifact:

```text
reports/latest/prediction_validation/time_series_split_proof.json
```

---

## Fact 2 — Look-ahead bias invalidates backtests

Look-ahead bias means using information that was not available at decision time. Any backtest using unavailable future information must be marked invalid.

Required artifact:

```text
reports/latest/prediction_validation/lookahead_bias_audit.json
```

---

## Fact 3 — Historical data must prove OHLCV and OI where needed

For Dhan-style historical data, OHLCV and derivative OI must be mapped by instrument, segment, security id, and timestamp. Options prediction cannot rely only on underlying candles.

Required artifact:

```text
reports/latest/prediction_validation/historical_data_source_audit.json
```

---

## Fact 4 — Options prediction needs option-chain features

Option-chain data must include strike-wise CE/PE, bid/ask, LTP, OI, volume, IV, and Greeks where available. Any option model using only direction of the underlying is incomplete.

Required artifact:

```text
reports/latest/prediction_validation/option_chain_training_data_audit.json
```

---

## Fact 5 — Accuracy alone is not enough

A single accuracy value cannot prove trade readiness. Classification, probability, ranking, and trading-P&L metrics measure different things.

Required artifact:

```text
reports/latest/prediction_validation/metric_suite_audit.json
```

---

## Fact 6 — Probability/confidence must be calibrated

If a model displays probability/confidence, it must prove calibration. A 0.80 confidence bucket should be checked against actual outcomes over enough out-of-sample cases.

Required artifact:

```text
reports/latest/prediction_validation/probability_calibration_audit.json
```

---

# PRED8 gap matrix

## PRED8-01 — Prediction data source map missing/incomplete

Every prediction input must have source, timestamp, availability time, stale flag, fallback flag, and synthetic flag.

Inputs to map:

- spot/index OHLCV
- equity OHLCV
- option OHLCV
- option-chain snapshot
- bid/ask/depth
- OI/volume/OI change
- IV/Greeks
- VIX/macro/global cues
- broker quote source
- news/event source
- contract master source

Required artifact:

```text
reports/latest/prediction_validation/prediction_data_source_map.json
```

Status: `BLOCKER`.

---

## PRED8-02 — Feature point-in-time audit missing

Every feature must prove it was available before prediction time.

Required fields:

```text
feature_name
feature_value
feature_source
feature_event_time
feature_ingested_time
feature_available_to_model_time
prediction_time
is_point_in_time_safe
```

Reject if:

```text
feature_available_to_model_time > prediction_time
```

Required artifact:

```text
reports/latest/prediction_validation/feature_point_in_time_audit.json
```

Status: `HARD_BLOCKER`.

---

## PRED8-03 — Teacher/label definition missing

The model must prove what it is trained to predict.

Possible labels:

- next_1m_direction
- next_5m_direction
- next_15m_direction
- next_day_direction
- max_favorable_excursion
- max_adverse_excursion
- option_premium_return
- underlying_return
- risk_adjusted_return
- hit_target_before_stop
- net_pnl_positive_after_costs

Each label must define horizon, entry assumption, exit assumption, stop/target, costs, slippage, spread, and whether it uses underlying, option premium, or net P&L.

Required artifact:

```text
reports/latest/prediction_validation/teacher_label_definition.json
```

Status: `BLOCKER`.

---

## PRED8-04 — Label leakage audit missing

Future high/low/close may be used only to create labels, never as features. Rolling features must be shifted safely.

Required artifact:

```text
reports/latest/prediction_validation/label_leakage_audit.json
```

Status: `HARD_BLOCKER`.

---

## PRED8-05 — Temporal validation scheme required

Allowed validation modes:

- walk_forward_split
- rolling_window_split
- expanding_window_split
- purged_embargo_split where label overlap exists
- market_regime_out_of_sample_split

Required artifact:

```text
reports/latest/prediction_validation/temporal_validation_scheme.json
```

Status: `BLOCKER`.

---

## PRED8-06 — Walk-forward validation must cover regimes

Required regime coverage:

- trending market
- range market
- high VIX
- low VIX
- expiry week
- non-expiry week
- news/event day
- gap-open day
- high volume day
- low liquidity day

Required artifact:

```text
reports/latest/prediction_validation/walk_forward_regime_coverage.json
```

Status: `NOT_PROVEN`.

---

## PRED8-07 — Costed backtest required

Backtest must include brokerage, STT, exchange charges, GST, stamp duty, slippage, bid/ask spread, partial-fill/no-fill risk, and exit liquidity.

Required artifact:

```text
reports/latest/prediction_validation/costed_backtest_audit.json
```

Status: `BLOCKER`.

---

## PRED8-08 — Options backtesting must replay contracts

Options backtesting must prove selected CE/PE, strike, expiry, token/security id, bid/ask/LTP at entry and exit, IV/Greeks/OI/volume, spread, theta risk, expiry risk, and exit liquidity.

Required artifact:

```text
reports/latest/prediction_validation/options_backtest_contract_replay.json
```

Status: `BLOCKER`.

---

## PRED8-09 — Baseline models required

Compare against:

- no-trade baseline
- buy-and-hold underlying
- ATM option-buy baseline
- random direction baseline
- previous candle momentum baseline
- simple trend baseline
- volatility breakout baseline
- rule-based option-chain baseline

Required artifact:

```text
reports/latest/prediction_validation/baseline_model_comparison.json
```

Status: `NOT_PROVEN`.

---

## PRED8-10 — Accuracy metric suite required

Dashboard must show classification, probability, ranking, and trading metrics.

Required metrics:

- accuracy, balanced accuracy, precision, recall, F1, confusion matrix
- log loss, Brier score, calibration curve
- Spearman rank correlation, top-k hit rate, precision@k, rank stability
- net P&L after costs, expectancy, win rate, profit factor, max drawdown, trade count, slippage impact

Required artifact:

```text
reports/latest/prediction_validation/accuracy_metric_suite.json
```

Status: `BLOCKER`.

---

## PRED8-11 — Probability calibration required

If dashboard shows confidence/probability, it must show calibration bins, predicted probability vs actual frequency, Brier score, log loss, sample size, calibration period, and out-of-sample status.

Required artifact:

```text
reports/latest/prediction_validation/calibration_curve.json
```

Status: `BLOCKER`.

---

## PRED8-12 — Model promotion policy required

Promotion is blocked unless temporal validation, walk-forward, costed backtest, paper consistency, calibration, minimum sample size, drawdown, no-leakage, no-fallback, and rollback conditions are all proven.

Required artifact:

```text
reports/latest/prediction_validation/model_promotion_policy_gate.json
```

Status: `BLOCKER`.

---

## PRED8-13 — Prediction dashboard explainability required

Dashboard must show prediction time, model version, model hash, feature snapshot id, data source status, label type, horizon, predicted class/return, probability/confidence, calibration status, rank score, contract selected, trade/no-trade decision, reasons, and blockers.

Required artifact:

```text
reports/latest/prediction_validation/prediction_dashboard_explainability.json
```

Status: `BLOCKER_FOR_TRUST`.

---

## PRED8-14 — Drift and decay monitoring required

Track rolling accuracy, rolling calibration, rolling P&L, feature drift, prediction distribution drift, signal frequency drift, market regime drift, rank correlation decay, model age, and data-source change.

Required artifact:

```text
reports/latest/prediction_validation/model_drift_monitor.json
```

Status: `NOT_PROVEN`.

---

## PRED8-15 — Post-trade attribution required

Every outcome must explain whether the prediction, option strike, entry, exit, spread, theta, IV, liquidity, or risk rule caused the result.

Required artifact:

```text
reports/latest/prediction_validation/post_trade_attribution.json
```

Status: `NOT_PROVEN`.

---

# Accuracy dashboard rule

Dashboard must never show generic `ML Accuracy: PASS` unless it also shows:

```text
sample size
validation window
validation method
costed net P&L
walk-forward status
calibration status
rank correlation
trade count
drawdown
leakage status
promotion status
```

Allowed states:

```text
MODEL_EXPERIMENTAL
MODEL_OBSERVE_ONLY
MODEL_PAPER_VALIDATED
MODEL_PROMOTION_BLOCKED
MODEL_ANALYZER_VALIDATED_ONLY
```

---

# Required artifacts

```text
reports/latest/online_source_validation/prediction_backtesting_source_map.json
reports/latest/prediction_validation/prediction_data_source_map.json
reports/latest/prediction_validation/teacher_label_definition.json
reports/latest/prediction_validation/lookahead_bias_audit.json
reports/latest/prediction_validation/temporal_validation_scheme.json
reports/latest/prediction_validation/walk_forward_regime_coverage.json
reports/latest/prediction_validation/costed_backtest_audit.json
reports/latest/prediction_validation/options_backtest_contract_replay.json
reports/latest/prediction_validation/accuracy_metric_suite.json
reports/latest/prediction_validation/calibration_curve.json
reports/latest/prediction_validation/model_promotion_policy_gate.json
reports/latest/prediction_validation/model_drift_monitor.json
```

---

# Final rule

Prediction/backtest/accuracy is not proven unless the user can answer:

```text
What data trained this model?
What was the teacher/label?
Was every feature point-in-time safe?
Was validation temporal/walk-forward?
Was option-chain contract replay used?
Were costs, spread, slippage, and no-fill risk included?
Was probability calibrated?
Was performance stable across regimes?
Was paper performance consistent with backtest?
Why is the model promoted or blocked?
```

Until then:

```text
PREDICTION_ACCURACY_TRUST: NOT_PROVEN
MODEL_PROMOTION: BLOCKED
REAL_ORDER_PLACEMENT: DISABLED
```
