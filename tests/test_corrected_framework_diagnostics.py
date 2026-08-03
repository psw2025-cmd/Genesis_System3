from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.options_research.corrected_framework_diagnostics import (
    _metric,
    analyse_artifact,
    filter_scenarios,
    validation_gate_report,
    write_reports,
)


def _validation_row(passing: bool) -> dict:
    value = 0.01 if passing else -0.01
    return {
        "lightgbm_weight": 1.0,
        "top_k": 1,
        "min_probability": 0.6,
        "composite": value,
        "metrics": {
            "median_daily_spearman": 0.1 if passing else 0.0,
            "cost_stress": {
                "80.0": {
                    "mean_daily_return": value,
                    "profit_factor": 1.2 if passing else 0.8,
                    "annualized_sharpe": 0.5 if passing else -0.5,
                    "max_drawdown": 0.1 if passing else 0.4,
                }
            },
        },
    }


def test_validation_gate_rejects_all_negative_candidates():
    report = validation_gate_report([_validation_row(False), _validation_row(False)])
    assert report["candidates_evaluated"] == 2
    assert report["candidates_passing"] == 0
    assert report["all_candidates_failed"] is True


def test_validation_gate_accepts_only_complete_pass():
    report = validation_gate_report([_validation_row(False), _validation_row(True)])
    assert report["candidates_passing"] == 1
    assert report["all_candidates_failed"] is False


def test_empirical_break_even_uses_real_average_win_and_loss():
    result = _metric(pd.Series([0.60, -0.30, -0.10]).to_numpy())
    expected = 0.20 / (0.60 + 0.20)
    assert abs(result["empirical_break_even_win_rate"] - expected) < 1e-12
    assert result["empirical_break_even_win_rate"] != 1 / 3


def test_filter_scenarios_are_deterministic():
    frame = pd.DataFrame({
        "trade_date": ["2026-01-01", "2026-01-01"],
        "expiry": ["2026-01-11", "2026-02-20"],
        "oi": [3000, 1000],
        "volume": [700, 200],
    })
    masks = filter_scenarios(frame)
    assert int(masks["base"].sum()) == 2
    assert int(masks["dte_5_30"].sum()) == 1
    assert int(masks["oi_ge_2000"].sum()) == 1
    assert int(masks["volume_ge_500"].sum()) == 1
    assert int(masks["combined_dte_5_30_oi_2000_volume_500"].sum()) == 1


def test_full_artifact_analysis_rejects_unsupported_framework_claims(tmp_path: Path):
    proof = {
        "frozen_test": {
            "days": 2,
            "attempted_trades": 2,
            "filled_trades": 2,
            "row_roc_auc": 0.468,
            "median_daily_spearman": 0.05,
            "mean_top_k_overlap": 0.004,
            "cost_stress": {
                "0.0": {"compounded_total_return": -0.1, "profit_factor": 0.8},
                "80.0": {"compounded_total_return": -0.2, "profit_factor": 0.7},
            },
        }
    }
    (tmp_path / "advanced_model_backtest_proof.json").write_text(json.dumps(proof))
    (tmp_path / "validation_search.json").write_text(
        json.dumps([_validation_row(False)])
    )
    pd.DataFrame({
        "trade_date": ["2026-01-01", "2026-01-02"],
        "symbol": ["A", "B"],
        "expiry": ["2026-01-10", "2026-01-20"],
        "strike": [100, 200],
        "option_type": ["CE", "PE"],
        "close": [20, 30],
        "volume": [600, 100],
        "oi": [3000, 1000],
        "target_fillable": [1, 1],
        "gross_return": [0.1, -0.1],
        "probability": [0.7, 0.8],
        "ensemble_score": [0.9, 0.8],
    }).to_csv(tmp_path / "frozen_selected_trades.csv", index=False)

    report = analyse_artifact(tmp_path)
    claims = {row["claim"]: row["status"] for row in report["framework_claims"]}
    assert claims["current_target_is_simple_next_premium_difference"] == "REJECTED_BY_REPOSITORY_CODE"
    assert claims["binary_profitability_target_is_new"] == "REJECTED_ALREADY_IMPLEMENTED"
    assert report["repository_semantics"]["stop_loss_percent"] == 30.0
    assert report["repository_semantics"]["take_profit_percent"] == 60.0
    assert report["decision"]["promotion_allowed"] is False
    assert report["decision"]["frozen_configuration_tuning_allowed"] is False


def test_report_writer_preserves_safety_and_six_files(tmp_path: Path):
    report = {
        "status": "PHASE1_DIAGNOSTIC_EXECUTED",
        "repository_semantics": {
            "stop_loss_percent": 30.0,
            "take_profit_percent": 60.0,
        },
        "framework_claims": [],
        "pre_frozen_validation_gate": {
            "candidates_evaluated": 0,
            "candidates_passing": 0,
            "rows": [],
        },
        "frozen_filter_diagnostics": {"rows": []},
        "phase1_answers": {
            "target_bottleneck": {"status": "NOT_ISOLATED"},
            "entry_filter_bottleneck": {"status": "BLOCKED"},
            "regime_bottleneck": {"status": "BLOCKED"},
        },
        "decision": {
            "frozen_should_have_remained_closed_under_new_gate": True,
            "next_valid_experiment": "nested validation",
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "promotion_allowed": False,
        },
    }
    files = write_reports(report, tmp_path)
    assert len(files) == 6
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["live_trading_enabled"] is False
    assert manifest["order_placement_allowed"] is False
    assert manifest["promotion_allowed"] is False
