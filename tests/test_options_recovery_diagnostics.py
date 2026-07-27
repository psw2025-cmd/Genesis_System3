from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.options_research.recovery_diagnostics import (
    AVAILABLE,
    BLOCKED_EXTERNAL,
    BLOCKED_IV,
    BLOCKED_QUOTES,
    DERIVABLE,
    REJECTED_PROXY,
    attachment_crosscheck,
    execution_fraction_report,
    feature_feasibility_summary,
    load_model_artifact_root,
    simulate_cost_stress,
)


def sample_trades() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"trade_date": "2026-01-01", "gross_return": 0.10, "target_fillable": 1},
            {"trade_date": "2026-01-01", "gross_return": -0.20, "target_fillable": 1},
            {"trade_date": "2026-01-02", "gross_return": 0.00, "target_fillable": 0},
            {"trade_date": "2026-01-03", "gross_return": -0.10, "target_fillable": 1},
        ]
    )


def sample_proof() -> dict:
    return {
        "status": "EXECUTED",
        "execution_assumptions": {"stop_loss_pct": 0.30, "take_profit_pct": 0.60},
    }


def test_decimal_execution_semantics_are_not_basis_points():
    result = execution_fraction_report(0.30, 0.60)
    assert result["stop_loss_percent"] == pytest.approx(30.0)
    assert result["take_profit_percent"] == pytest.approx(60.0)


def test_feature_feasibility_is_exhaustive_and_closed():
    result = feature_feasibility_summary()
    assert result["requested_features"] == 20
    assert result["allowed_for_eod_implementation"] == 9
    assert result["blocked_or_rejected"] == 11
    assert sum(result["status_counts"].values()) == 20
    assert set(result["status_counts"]) == {
        AVAILABLE,
        DERIVABLE,
        BLOCKED_QUOTES,
        BLOCKED_IV,
        BLOCKED_EXTERNAL,
        REJECTED_PROXY,
    }


def test_cost_stress_preserves_no_fill_and_monotonic_cost_damage():
    rows = simulate_cost_stress(sample_trades(), [0.0, 80.0])
    assert rows[0].attempted_trades == 4
    assert rows[0].filled_trades == 3
    assert rows[0].rejected_no_fill == 1
    assert rows[1].ending_capital < rows[0].ending_capital
    assert rows[1].profit_factor < rows[0].profit_factor


def test_invalid_cost_and_missing_columns_are_rejected():
    with pytest.raises(ValueError):
        simulate_cost_stress(sample_trades(), [-1.0])
    with pytest.raises(ValueError):
        simulate_cost_stress(pd.DataFrame({"trade_date": ["x"]}), [0.0])


def test_attachment_crosscheck_blocks_promotion():
    result = attachment_crosscheck(sample_proof(), sample_trades())
    assert result["status"] == "PASS_ATTACHMENT_CROSSCHECK"
    assert result["live_trading_enabled"] is False
    assert result["order_placement_allowed"] is False
    assert result["promotion_allowed"] is False
    decisions = {row["claim"]: row["status"] for row in result["claims"]}
    assert decisions["stop_loss_is_0_3_percent"] == "REJECTED"
    assert decisions["take_profit_is_0_6_percent"] == "REJECTED"
    assert decisions["larger_model_search_should_proceed_immediately"] == "BLOCKED_PENDING_SIGNAL_DIAGNOSTICS"


def test_load_model_artifact_requires_exactly_one_pair(tmp_path: Path):
    model = tmp_path / "model"
    model.mkdir()
    (model / "advanced_model_backtest_proof.json").write_text(
        json.dumps(sample_proof()), encoding="utf-8"
    )
    sample_trades().to_csv(model / "frozen_selected_trades.csv", index=False)
    proof, trades = load_model_artifact_root(tmp_path)
    assert proof["status"] == "EXECUTED"
    assert len(trades) == 4
