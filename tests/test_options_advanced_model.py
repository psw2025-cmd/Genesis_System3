from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.options_research.advanced_model import (
    MAX_DAILY_EXPOSURE,
    PER_TRADE_ALLOCATION,
    SelectionConfig,
    deterministic_sample,
    evaluate_files,
    metric_summary,
    normalized_paper_ledger,
    selected_rows,
)
from src.options_research.eod_features import FEATURE_COLUMNS


def feature_frame(day: str, rows: int = 20) -> pd.DataFrame:
    values = {
        "symbol": [f"SYM{i % 5}" for i in range(rows)],
        "expiry": pd.to_datetime(["2026-08-27"] * rows),
        "strike": [100.0 + i for i in range(rows)],
        "option_type": ["CE" if i % 2 == 0 else "PE" for i in range(rows)],
        "instrument": ["OPTSTK"] * rows,
        "trade_date": pd.to_datetime([day] * rows),
        "gross_return": np.linspace(-0.10, 0.20, rows),
        "target_net_return": np.linspace(-0.108, 0.192, rows),
        "target_positive": (np.linspace(-0.108, 0.192, rows) > 0).astype(int),
        "target_fillable": np.ones(rows, dtype=int),
        "close": np.linspace(10, 30, rows),
        "volume": np.arange(1, rows + 1) * 100,
        "oi": np.arange(1, rows + 1) * 1000,
    }
    for index, column in enumerate(FEATURE_COLUMNS):
        values[column] = np.linspace(-1, 1, rows) + index * 0.001
    return pd.DataFrame(values)


def test_deterministic_sample_spans_all_sessions(tmp_path: Path):
    files = []
    for index, day in enumerate(("2026-01-02", "2026-01-05", "2026-01-06")):
        path = tmp_path / f"2026010{index + 2}_features.parquet"
        feature_frame(day).to_parquet(path, index=False)
        files.append(path)
    sample = deterministic_sample(files, max_rows=60, seed=7)
    assert len(sample) == 60
    assert sample["trade_date"].nunique() == 3
    assert set(FEATURE_COLUMNS).issubset(sample.columns)
    assert "target_fillable" in sample.columns


def test_selected_rows_is_distinct_underlying_and_thresholded():
    frame = feature_frame("2026-01-02", rows=20)
    frame["baseline_rank"] = np.linspace(0.01, 1.0, len(frame))
    frame["challenger_rank"] = np.linspace(1.0, 0.01, len(frame))
    frame["probability"] = 0.70
    selected, predicted, actual = selected_rows(
        frame, SelectionConfig(lightgbm_weight=0.5, top_k=3, min_probability=0.60)
    )
    assert len(selected) == 3
    assert selected["symbol"].nunique() == 3
    assert predicted["symbol"].nunique() == 5
    assert actual["symbol"].nunique() == 5


def test_metric_summary_reports_costed_risk_statistics():
    metrics = metric_summary(
        trades=[0.10, -0.05, 0.03, -0.02, 0.06],
        daily=[0.005, -0.0025, 0.0015],
    )
    assert metrics["trades"] == 5
    assert metrics["winners"] == 3
    assert metrics["losers"] == 2
    assert metrics["profit_factor"] is not None
    assert 0 <= metrics["max_drawdown"] < 0.01
    assert metrics["max_consecutive_losing_trades"] == 1
    assert metrics["per_trade_allocation"] == PER_TRADE_ALLOCATION
    assert metrics["maximum_daily_exposure"] == MAX_DAILY_EXPOSURE


class IdentityScaler:
    def transform(self, values):
        return values


class FirstFeatureRegressor:
    def predict(self, values):
        return values[:, 0]


class FixedClassifier:
    def predict_proba(self, values):
        probability = np.full(len(values), 0.75)
        return np.column_stack([1 - probability, probability])


def test_evaluate_counts_no_fill_and_caps_portfolio_return(tmp_path: Path):
    frame = feature_frame("2026-01-02", rows=5)
    frame["symbol"] = ["A", "B", "C", "D", "E"]
    frame["gross_return"] = [0.10, 0.20, -0.30, 0.60, 0.40]
    frame["target_fillable"] = [1, 0, 1, 1, 1]
    frame[FEATURE_COLUMNS[0]] = [0.9, 0.8, 0.7, 0.6, 0.5]
    path = tmp_path / "20260102_features.parquet"
    frame.to_parquet(path, index=False)
    metrics, trades = evaluate_files(
        [path], IdentityScaler(), FirstFeatureRegressor(), FixedClassifier(), None,
        SelectionConfig(lightgbm_weight=0.0, top_k=3, min_probability=0.0),
        [0.0],
    )
    assert metrics["attempted_trades"] == 3
    assert metrics["filled_trades"] == 2
    assert metrics["rejected_no_fill"] == 1
    assert metrics["fill_rate"] == 2 / 3
    # A +10% and C -30%, each at 5% capital => -1.0% portfolio return.
    assert abs(metrics["cost_stress"]["0.0"]["mean_daily_return"] - (-0.01)) < 1e-12
    assert len(trades) == 3


def test_normalized_paper_ledger_is_capped_and_not_broker_pnl():
    trades = pd.DataFrame({
        "trade_date": ["2026-01-02", "2026-01-02", "2026-01-02", "2026-01-05"],
        "gross_return": [0.60, 0.60, 0.60, -0.30],
        "target_fillable": [1, 1, 1, 0],
    })
    ledger, proof = normalized_paper_ledger(trades, cost_bps=0, initial_capital_inr=100_000)
    assert len(ledger) == 2
    assert proof["attempted_trades"] == 4
    assert proof["filled_trades"] == 3
    assert proof["rejected_no_fill"] == 1
    assert proof["initial_capital_inr"] == 100_000
    assert proof["maximum_daily_exposure"] == 0.15
    assert proof["per_trade_allocation"] == 0.05
    assert ledger["daily_gross_exposure"].max() <= 0.15 + 1e-12
    assert abs(ledger.iloc[0]["portfolio_net_return"] - 0.09) < 1e-12
    assert proof["historical_lot_sizes_used"] is False
    assert proof["broker_fills_used"] is False
    assert proof["live_trading_enabled"] is False
