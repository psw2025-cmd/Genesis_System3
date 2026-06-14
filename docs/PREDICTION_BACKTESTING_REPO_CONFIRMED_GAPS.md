# Prediction and Backtesting Repo-Confirmed Gaps

**Purpose:** Record only gaps confirmed from current repo inspection. No broad market assumptions are marked confirmed here unless backed by repo code/report evidence.

**Baseline inspected:** `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01`

**Safety rule:** Analyzer/Paper only. This file does not authorize real order placement.

---

# Inspected repo files

- `src/validation/market_result_validator.py`
- `scripts/daily_gain_rank_and_validate.py`
- `src/ranking/daily_gain_scanner.py`
- `src/ranking/gain_rank_engine.py`
- `scripts/calibrate_factor_weights.py`

---

# Confirmed findings

## PRED-RC1 — Validation currently measures rank alignment, not trade outcome

**Evidence path:** `src/validation/market_result_validator.py`

The validator compares predicted top-gain symbols vs actual NSE top movers and computes Spearman rank correlation. It also stores top-3/top-5 overlap.

**Confirmed gap:** This does not prove option trade profitability, entry/exit correctness, net P&L, stop/target behavior, paper-trade lifecycle outcome, or contract-level option replay.

**Status:** `CONFIRMED_GAP`.

**Required next proof:**

```text
reports/latest/prediction_validation/trade_outcome_validation.json
reports/latest/prediction_validation/options_backtest_contract_replay.json
```

---

## PRED-RC2 — Actual-results validation is limited to tracked index underlyings

**Evidence path:** `src/validation/market_result_validator.py`

`TRACKED_UNDERLYINGS` is limited to NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, and SENSEX. Actual NSE most-active options are normalized only if they match tracked underlyings.

**Confirmed gap:** Equity stock options are not proven in this validation path. Cash-equity vs F&O-stock-option eligibility is not validated here.

**Status:** `CONFIRMED_GAP`.

**Required next proof:**

```text
reports/latest/prediction_validation/equity_option_validation_coverage.json
reports/latest/options_dashboard_contract_visibility/fno_eligibility_classification.json
```

---

## PRED-RC3 — Synthetic fallback exists in ranking runner

**Evidence path:** `scripts/daily_gain_rank_and_validate.py`

The ranking runner loads option-chain data in this order: NSE public API, local CSV, then synthetic fallback. Synthetic fallback creates strike, option_type, OI, volume, LTP, and IV values.

**Confirmed gap:** Any prediction/ranking output must prove whether it used live/NSE, CSV, or synthetic fallback. Synthetic/fallback data must not be counted as production proof.

**Status:** `CONFIRMED_GAP`.

**Required next proof:**

```text
reports/latest/prediction_validation/prediction_data_source_map.json
reports/latest/prediction_validation/fallback_synthetic_rejection.json
```

---

## PRED-RC4 — Option-chain frame used for ranking omits executable quote fields

**Evidence path:** `scripts/daily_gain_rank_and_validate.py`

The NSE chain parser stores strike, option_type, OI, volume, LTP, and IV.

**Confirmed gap:** Ranking data does not prove bid, ask, bid quantity, ask quantity, spread, depth, token, lot size, strike validity, expiry validity, or executable mark price.

**Status:** `CONFIRMED_GAP`.

**Required next proof:**

```text
reports/latest/prediction_validation/option_chain_training_data_audit.json
reports/latest/options_dashboard_contract_visibility/option_quote_quality.json
```

---

## PRED-RC5 — Daily scanner prediction uses stored CSV only and four index symbols

**Evidence path:** `src/ranking/daily_gain_scanner.py`

`run_prediction()` loads latest stored option-chain CSVs for NIFTY, BANKNIFTY, FINNIFTY, and MIDCPNIFTY, then saves top predictions and full ranking.

**Confirmed gap:** Current scanner path does not prove live quote freshness, data-source age, real-time option chain, equity option coverage, or token/strike/expiry validity.

**Status:** `CONFIRMED_GAP`.

**Required next proof:**

```text
reports/latest/prediction_validation/live_prediction_source_freshness.json
reports/latest/prediction_validation/equity_option_universe_coverage.json
```

---

## PRED-RC6 — Saved prediction snapshot is too thin for forensic replay

**Evidence path:** `src/ranking/gain_rank_engine.py`

Rank history saves only rank, underlying, gain_score, expected_move_pct, and recommendation.

**Confirmed gap:** Saved prediction history does not include feature values, feature timestamps, source provenance, model/version/hash, CE/PE, selected strike, expiry, token, bid/ask/LTP, or rejection reasons. This prevents forensic replay.

**Status:** `CONFIRMED_GAP`.

**Required next proof:**

```text
reports/latest/prediction_validation/feature_snapshot_replay_schema.json
reports/latest/prediction_validation/prediction_replay_artifact.json
```

---

## PRED-RC7 — Gain score uses factor formula but no contract-level trade validation

**Evidence path:** `src/ranking/gain_rank_engine.py`

GainRankEngine scores OI change, IV percentile/proxy, volume surge, PCR divergence, ATM premium ratio, momentum, and ML confidence. It returns `TRADE` when score >= threshold.

**Confirmed gap:** A `TRADE` recommendation from gain score does not prove that a specific option contract is valid, liquid, executable, risk-approved, or profitable after costs.

**Status:** `CONFIRMED_GAP`.

**Required next proof:**

```text
reports/latest/prediction_validation/contract_level_trade_gate.json
reports/latest/prediction_validation/costed_option_trade_replay.json
```

---

## PRED-RC8 — Current factor weights mention 1-day grid-search influence

**Evidence path:** `src/ranking/gain_rank_engine.py`

Code comments state the grid search was optimal on 1 day and applied conservatively, with auto-update expected after 5+ validation days.

**Confirmed gap:** Current weights cannot be treated as high-confidence model promotion proof without enough validation days and documented out-of-sample performance.

**Status:** `CONFIRMED_GAP`.

**Required next proof:**

```text
reports/latest/prediction_validation/factor_weight_confidence.json
reports/latest/prediction_validation/out_of_sample_weight_validation.json
```

---

## PRED-RC9 — Calibration guardrails exist, but scope is narrow

**Evidence path:** `scripts/calibrate_factor_weights.py`

Calibration script has a confidence threshold: less than 5 validation days is report-only; 5+ can auto-update; 14+ is high confidence. It builds IV history using prior files only, which is a good anti-lookahead step.

**Confirmed gap:** Calibration still optimizes factor weights on rank correlation for limited symbols and does not prove option entry/exit, paper-trade P&L, probability calibration, trade expectancy, or contract replay.

**Status:** `CONFIRMED_GAP_WITH_GOOD_GUARDRAIL`.

**Required next proof:**

```text
reports/latest/prediction_validation/calibration_scope_limitations.json
reports/latest/prediction_validation/paper_vs_backtest_consistency.json
```

---

## PRED-RC10 — Accuracy dashboard must not show generic PASS from these metrics alone

**Evidence path:** combined inspection of validator, scanner, gain rank engine, and calibration script.

Current repo validation mainly supports rank correlation/top-k overlap/factor calibration. It does not prove a full options trading model.

**Confirmed gap:** Dashboard must not show `ML Accuracy: PASS` unless it also shows sample size, validation method, validation window, costed P&L, calibration, contract replay, leakage audit, and promotion status.

**Status:** `CONFIRMED_GAP`.

**Required next proof:**

```text
reports/latest/prediction_validation/accuracy_dashboard_truth_matrix.json
```

---

# Required next repo audit batch

Current batch complete. More gaps may exist. Next batch should inspect:

```text
core/data/nse_provider.py
src/ranking/ml_signal_aggregator.py
reports/latest/model_training_load_proof/summary.json
reports/latest/recent_backtest_walkforward_proof/summary.json
reports/latest/proof_status_matrix/proof_status_matrix.json
dashboard/app.js accuracy/proof display
```

No production readiness claim should be made from prediction/accuracy until those are inspected and reconciled.
