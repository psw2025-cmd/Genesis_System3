"""Compute fail-closed, lane-specific research gaps against project targets.

The report accepts only forward-issued, immutable observations from an untouched
chronological test. Retrospective replays and fixture arithmetic remain visible
as NOT_PROVEN and cannot be promoted.
"""
from __future__ import annotations

from math import isfinite
from typing import Any


SUPPORTED_LANES = {"equity_weekly", "cepe_next_open"}
_MINIMUM_GATES = {
    "oos_directional_accuracy_pct": "min_oos_directional_accuracy_pct",
    "top_decile_precision_pct": "min_top_decile_precision_pct",
    "oos_trades": "min_oos_trades",
    "oos_days": "min_oos_days",
    "sharpe": "min_sharpe",
    "deflated_sharpe_probability": "min_deflated_sharpe_probability",
}
_MAXIMUM_GATES = {
    "max_drawdown_pct": "max_drawdown_pct",
}
_REQUIRED_REPORT_FIELDS = {
    "positive_forecasts",
    "negative_forecasts",
    "return_distribution",
    "calibration_error",
    "uncertainty",
}
_LANE_FIELDS = {
    "equity_weekly": {"benchmark_excess_return_pct"},
    "cepe_next_open": {
        "full_uncapped_multiple_distribution",
        "benchmark_excess_precision_pct_points",
    },
}


class ResearchGateError(ValueError):
    """Raised for a malformed target configuration or contradictory metrics."""


def _number(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ResearchGateError(f"{name}_INVALID")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ResearchGateError(f"{name}_INVALID") from exc
    if not isfinite(result):
        raise ResearchGateError(f"{name}_INVALID")
    return result


def _target_map(config: dict[str, Any]) -> dict[str, float]:
    raw = config.get("targets")
    if not isinstance(raw, dict):
        raise ResearchGateError("TARGETS_REQUIRED")
    needed = set(_MINIMUM_GATES.values()) | set(_MAXIMUM_GATES.values())
    missing = sorted(needed - raw.keys())
    if missing:
        raise ResearchGateError("TARGETS_MISSING:" + ",".join(missing))
    return {key: _number(raw[key], key) for key in needed}


def evaluate_lane(
    lane: str,
    observation: dict[str, Any],
    project_config: dict[str, Any],
) -> dict[str, Any]:
    """Return current values and signed shortfalls without relaxing any gate."""
    if lane not in SUPPORTED_LANES:
        raise ResearchGateError("LANE_UNSUPPORTED")
    targets = _target_map(project_config)
    governance = project_config.get("governance", {})
    if (
        governance.get("targets_are_goals_not_current_claims") is not True
        or governance.get("frozen_holdout_tuning_forbidden") is not True
        or governance.get("automatic_model_promotion") is not False
        or governance.get("live_trading_enabled") is not False
    ):
        raise ResearchGateError("PROJECT_GOVERNANCE_UNSAFE")

    proof_requirements = {
        "forward_issued": True,
        "immutable_record": True,
        "chronological_untouched_test": True,
        "source_qualified": True,
        "costs_applied": True,
        "survivorship_guard_applied": True,
        "corporate_action_guard_applied": True,
        "multiple_testing_control_applied": True,
    }
    missing_proof = sorted(
        key for key, required in proof_requirements.items()
        if observation.get(key) is not required
    )
    required_metrics = (
        set(_MINIMUM_GATES)
        | set(_MAXIMUM_GATES)
        | _REQUIRED_REPORT_FIELDS
        | _LANE_FIELDS[lane]
    )
    missing_metrics = sorted(
        key for key in required_metrics
        if key not in observation or observation.get(key) is None
    )

    base = {
        "lane": lane,
        "status": "NOT_PROVEN",
        "missing_proof": missing_proof,
        "missing_metrics": missing_metrics,
        "gates": {},
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    if missing_proof or missing_metrics:
        return base

    current = {
        key: _number(observation[key], key)
        for key in set(_MINIMUM_GATES) | set(_MAXIMUM_GATES)
    }
    for name in ("positive_forecasts", "negative_forecasts"):
        current[name] = _number(observation[name], name)
        if current[name] < 0 or not current[name].is_integer():
            raise ResearchGateError(f"{name}_INVALID")
    if current["oos_trades"] < 0 or not current["oos_trades"].is_integer():
        raise ResearchGateError("oos_trades_INVALID")
    if current["oos_days"] < 0 or not current["oos_days"].is_integer():
        raise ResearchGateError("oos_days_INVALID")
    if current["positive_forecasts"] + current["negative_forecasts"] != current["oos_trades"]:
        raise ResearchGateError("FORECAST_COUNTS_DO_NOT_MATCH_OOS_TRADES")
    if not 0 <= current["oos_directional_accuracy_pct"] <= 100:
        raise ResearchGateError("oos_directional_accuracy_pct_INVALID")
    if not 0 <= current["top_decile_precision_pct"] <= 100:
        raise ResearchGateError("top_decile_precision_pct_INVALID")
    if current["max_drawdown_pct"] < 0:
        raise ResearchGateError("max_drawdown_pct_INVALID")
    if not 0 <= current["deflated_sharpe_probability"] <= 1:
        raise ResearchGateError("deflated_sharpe_probability_INVALID")
    if not isinstance(observation["return_distribution"], dict) or not observation["return_distribution"]:
        raise ResearchGateError("return_distribution_INVALID")
    if not isinstance(observation["uncertainty"], dict) or not observation["uncertainty"]:
        raise ResearchGateError("uncertainty_INVALID")
    if lane == "cepe_next_open" and (
        not isinstance(observation["full_uncapped_multiple_distribution"], dict)
        or not observation["full_uncapped_multiple_distribution"]
    ):
        raise ResearchGateError("full_uncapped_multiple_distribution_INVALID")

    gates: dict[str, dict[str, Any]] = {}
    for metric, target_name in _MINIMUM_GATES.items():
        target = targets[target_name]
        value = current[metric]
        shortfall = max(0.0, target - value)
        gates[metric] = {
            "current": value,
            "target": target,
            "gap": round(shortfall, 10),
            "passed": shortfall == 0,
            "direction": "minimum",
        }
    for metric, target_name in _MAXIMUM_GATES.items():
        target = targets[target_name]
        value = current[metric]
        excess = max(0.0, value - target)
        gates[metric] = {
            "current": value,
            "target": target,
            "gap": round(excess, 10),
            "passed": excess == 0,
            "direction": "maximum",
        }

    passed = all(item["passed"] for item in gates.values())
    base.update(
        status="ALL_PROJECT_GATES_PASSED" if passed else "GATE_MISSED",
        gates=gates,
        positive_forecasts=int(current["positive_forecasts"]),
        negative_forecasts=int(current["negative_forecasts"]),
        valid_oos_trades=int(current["oos_trades"]),
        valid_oos_days=int(current["oos_days"]),
        calibration_error=_number(
            observation["calibration_error"], "calibration_error"
        ),
        return_distribution=observation["return_distribution"],
        uncertainty=observation["uncertainty"],
        automatic_promotion_allowed=False,
    )
    if lane == "equity_weekly":
        base["benchmark_excess_return_pct"] = _number(
            observation["benchmark_excess_return_pct"],
            "benchmark_excess_return_pct",
        )
    else:
        base["benchmark_excess_precision_pct_points"] = _number(
            observation["benchmark_excess_precision_pct_points"],
            "benchmark_excess_precision_pct_points",
        )
        base["full_uncapped_multiple_distribution"] = observation[
            "full_uncapped_multiple_distribution"
        ]
        base["opening_fill_proven"] = False
    return base
