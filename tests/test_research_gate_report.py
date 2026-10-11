"""Tests for numerical research-gate reporting; no market-skill claims."""
import pytest

from scripts.research_gate_report import ResearchGateError, evaluate_lane


CONFIG = {
    "targets": {
        "min_oos_directional_accuracy_pct": 65.0,
        "min_top_decile_precision_pct": 70.0,
        "min_sharpe": 2.5,
        "max_drawdown_pct": 10.0,
        "min_oos_trades": 100,
        "min_oos_days": 60,
        "min_deflated_sharpe_probability": 0.95,
    },
    "governance": {
        "targets_are_goals_not_current_claims": True,
        "frozen_holdout_tuning_forbidden": True,
        "automatic_model_promotion": False,
        "live_trading_enabled": False,
    },
}
PROOF = {
    "forward_issued": True,
    "immutable_record": True,
    "chronological_untouched_test": True,
    "source_qualified": True,
    "costs_applied": True,
    "survivorship_guard_applied": True,
    "corporate_action_guard_applied": True,
    "multiple_testing_control_applied": True,
}
COMMON = {
    **PROOF,
    "oos_directional_accuracy_pct": 60.0,
    "top_decile_precision_pct": 72.0,
    "oos_trades": 120,
    "oos_days": 61,
    "sharpe": 2.0,
    "max_drawdown_pct": 12.0,
    "deflated_sharpe_probability": 0.90,
    "positive_forecasts": 70,
    "negative_forecasts": 50,
    "return_distribution": {"p05": -4.0, "median": 0.5, "p95": 8.0},
    "calibration_error": 0.08,
    "uncertainty": {"method": "block-bootstrap", "confidence": 0.95},
}


def test_empty_forward_sample_is_not_proven_and_has_no_fake_numeric_gap():
    result = evaluate_lane(
        "equity_weekly",
        {
            "forward_issued": False,
            "immutable_record": True,
            "chronological_untouched_test": False,
        },
        CONFIG,
    )

    assert result["status"] == "NOT_PROVEN"
    assert "forward_issued" in result["missing_proof"]
    assert result["gates"] == {}
    assert result["order_placement_allowed"] is False


def test_equity_report_records_signed_shortfalls_and_passes_individual_gate():
    result = evaluate_lane(
        "equity_weekly",
        {**COMMON, "benchmark_excess_return_pct": -1.2},
        CONFIG,
    )

    assert result["status"] == "GATE_MISSED"
    assert result["gates"]["oos_directional_accuracy_pct"]["gap"] == 5.0
    assert result["gates"]["top_decile_precision_pct"]["passed"] is True
    assert result["gates"]["sharpe"]["gap"] == 0.5
    assert result["gates"]["max_drawdown_pct"]["gap"] == 2.0
    assert result["gates"]["deflated_sharpe_probability"]["gap"] == 0.05
    assert result["benchmark_excess_return_pct"] == -1.2
    assert result["automatic_promotion_allowed"] is False


def test_cepe_report_keeps_full_distribution_and_never_claims_opening_fill():
    result = evaluate_lane(
        "cepe_next_open",
        {
            **COMMON,
            "benchmark_excess_precision_pct_points": 4.0,
            "full_uncapped_multiple_distribution": {
                "count": 120,
                "p50": 0.8,
                "p95": 1.7,
                "gte_3x": 2,
                "gte_10x": 0,
                "gte_20x": 0,
                "gte_30x": 0,
            },
        },
        CONFIG,
    )

    assert result["valid_oos_trades"] == 120
    assert result["full_uncapped_multiple_distribution"]["gte_3x"] == 2
    assert result["opening_fill_proven"] is False
    assert result["live_trading_enabled"] is False


def test_all_gates_can_pass_but_never_auto_promote_or_place_orders():
    observation = {
        **COMMON,
        "oos_directional_accuracy_pct": 65,
        "top_decile_precision_pct": 70,
        "sharpe": 2.5,
        "max_drawdown_pct": 10,
        "deflated_sharpe_probability": 0.95,
        "benchmark_excess_return_pct": 1.0,
    }
    result = evaluate_lane("equity_weekly", observation, CONFIG)

    assert result["status"] == "ALL_PROJECT_GATES_PASSED"
    assert all(gate["gap"] == 0 for gate in result["gates"].values())
    assert result["automatic_promotion_allowed"] is False
    assert result["order_placement_allowed"] is False


def test_contradictory_forecast_counts_fail_closed():
    with pytest.raises(
        ResearchGateError,
        match="FORECAST_COUNTS_DO_NOT_MATCH_OOS_TRADES",
    ):
        evaluate_lane(
            "equity_weekly",
            {
                **COMMON,
                "positive_forecasts": 71,
                "benchmark_excess_return_pct": 1.0,
            },
            CONFIG,
        )
