"""Evidence-only Phase-1 diagnostics for the corrected recovery framework.

This module never places orders, never promotes models, and never changes the
frozen holdout. It cross-checks the existing full-archive model artifact and
separates:
1. repository facts,
2. post-hoc frozen diagnostics,
3. pre-frozen validation gates,
4. unsupported recommendations.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .eod_features import STOP_LOSS_PCT, TAKE_PROFIT_PCT


@dataclass(frozen=True)
class ValidationGate:
    positive_mean_daily_return: bool
    profit_factor_above_one: bool
    sharpe_above_zero: bool
    max_drawdown_below_25pct: bool
    positive_rank_correlation: bool

    @property
    def passed(self) -> bool:
        return all(asdict(self).values())


def _find_one(root: Path, name: str) -> Path:
    matches = sorted(root.rglob(name))
    if len(matches) != 1:
        raise FileNotFoundError(f"expected exactly one {name}, found {len(matches)}")
    return matches[0]


def _metric(values: np.ndarray, allocation: float = 0.05) -> dict:
    values = np.asarray(values, dtype=float)
    positive = values[values > 0]
    negative = values[values <= 0]
    daily = values * float(allocation)
    bounded = np.clip(daily, -0.99, 1.0)
    equity = np.cumprod(1.0 + bounded) if len(bounded) else np.asarray([], dtype=float)
    peak = np.maximum.accumulate(equity) if len(equity) else np.asarray([], dtype=float)
    drawdown = (
        float(np.max((peak - equity) / np.maximum(peak, 1e-12)))
        if len(equity)
        else 0.0
    )
    mean_daily = float(daily.mean()) if len(daily) else 0.0
    std_daily = float(daily.std(ddof=1)) if len(daily) > 1 else 0.0
    sharpe = mean_daily / std_daily * math.sqrt(252) if std_daily > 0 else None
    avg_win = float(positive.mean()) if len(positive) else 0.0
    avg_loss = float(abs(negative.mean())) if len(negative) else 0.0
    empirical_break_even = (
        avg_loss / (avg_win + avg_loss)
        if avg_win > 0 and avg_loss > 0
        else None
    )
    return {
        "trades": int(len(values)),
        "winners": int((values > 0).sum()),
        "losers": int((values <= 0).sum()),
        "win_rate": float((values > 0).mean()) if len(values) else 0.0,
        "mean_trade_return": float(values.mean()) if len(values) else 0.0,
        "average_win": avg_win,
        "average_loss_abs": avg_loss,
        "empirical_break_even_win_rate": empirical_break_even,
        "profit_factor": (
            float(positive.sum() / abs(negative.sum()))
            if len(negative) and negative.sum() < 0
            else None
        ),
        "annualized_sharpe": sharpe,
        "maximum_drawdown": drawdown,
        "compounded_total_return": float(equity[-1] - 1.0) if len(equity) else 0.0,
        "ending_capital_from_100000": (
            float(100_000.0 * equity[-1]) if len(equity) else 100_000.0
        ),
        "per_trade_allocation": float(allocation),
    }


def validation_gate(row: dict, cost_key: str = "80.0") -> ValidationGate:
    metrics = row["metrics"]
    cost = metrics["cost_stress"][cost_key]
    return ValidationGate(
        positive_mean_daily_return=float(cost["mean_daily_return"]) > 0.0,
        profit_factor_above_one=float(cost.get("profit_factor") or 0.0) > 1.0,
        sharpe_above_zero=float(cost.get("annualized_sharpe") or 0.0) > 0.0,
        max_drawdown_below_25pct=float(cost["max_drawdown"]) < 0.25,
        positive_rank_correlation=float(metrics.get("median_daily_spearman") or 0.0) > 0.0,
    )


def validation_gate_report(rows: list[dict], cost_key: str = "80.0") -> dict:
    evaluated = []
    for rank, row in enumerate(rows, start=1):
        gate = validation_gate(row, cost_key)
        cost = row["metrics"]["cost_stress"][cost_key]
        evaluated.append({
            "validation_rank": rank,
            "lightgbm_weight": float(row["lightgbm_weight"]),
            "top_k": int(row["top_k"]),
            "min_probability": float(row["min_probability"]),
            "composite": float(row["composite"]),
            "mean_daily_return": float(cost["mean_daily_return"]),
            "profit_factor": float(cost.get("profit_factor") or 0.0),
            "annualized_sharpe": float(cost.get("annualized_sharpe") or 0.0),
            "maximum_drawdown": float(cost["max_drawdown"]),
            "median_daily_spearman": float(
                row["metrics"].get("median_daily_spearman") or 0.0
            ),
            "gates": asdict(gate),
            "passed": gate.passed,
        })
    return {
        "cost_bps": float(cost_key),
        "candidates_evaluated": len(evaluated),
        "candidates_passing": sum(row["passed"] for row in evaluated),
        "all_candidates_failed": bool(evaluated) and not any(
            row["passed"] for row in evaluated
        ),
        "best_candidate": evaluated[0] if evaluated else None,
        "rows": evaluated,
    }


def filter_scenarios(trades: pd.DataFrame) -> dict[str, pd.Series]:
    frame = trades.copy()
    if "dte" not in frame:
        frame["dte"] = (
            pd.to_datetime(frame["expiry"]) - pd.to_datetime(frame["trade_date"])
        ).dt.days
    return {
        "base": pd.Series(True, index=frame.index),
        "dte_5_30": frame["dte"].between(5, 30),
        "oi_ge_2000": frame["oi"].ge(2_000),
        "volume_ge_500": frame["volume"].ge(500),
        "combined_dte_5_30_oi_2000_volume_500": (
            frame["dte"].between(5, 30)
            & frame["oi"].ge(2_000)
            & frame["volume"].ge(500)
        ),
    }


def frozen_filter_report(
    trades: pd.DataFrame,
    costs_bps: Iterable[float] = (0.0, 80.0),
) -> dict:
    frame = trades.copy()
    frame["trade_date"] = pd.to_datetime(frame["trade_date"])
    frame["expiry"] = pd.to_datetime(frame["expiry"])
    frame["dte"] = (frame["expiry"] - frame["trade_date"]).dt.days
    filled = frame[frame["target_fillable"].astype(int).eq(1)].copy()
    scenarios = filter_scenarios(filled)
    rows = []
    for name, mask in scenarios.items():
        subset = filled.loc[mask].sort_values("trade_date")
        result = {
            "scenario": name,
            "trades": int(len(subset)),
            "retained_fraction": float(len(subset) / len(filled)) if len(filled) else 0.0,
            "costs": {},
        }
        for cost in costs_bps:
            values = subset["gross_return"].astype(float).to_numpy() - float(cost) / 10_000.0
            result["costs"][str(float(cost))] = _metric(values)
        rows.append(result)
    return {
        "status": "POST_HOC_FROZEN_DIAGNOSTIC_ONLY",
        "selection_or_tuning_allowed": False,
        "reason": (
            "These filters were inspected after the frozen holdout was opened. "
            "They may generate hypotheses, but cannot select production settings."
        ),
        "attempted_trades": int(len(frame)),
        "filled_trades": int(len(filled)),
        "rejected_no_fill": int(len(frame) - len(filled)),
        "rows": rows,
    }


def analyse_artifact(artifact_root: Path) -> dict:
    proof_path = _find_one(artifact_root, "advanced_model_backtest_proof.json")
    validation_path = _find_one(artifact_root, "validation_search.json")
    trades_path = _find_one(artifact_root, "frozen_selected_trades.csv")

    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    validation_rows = json.loads(validation_path.read_text(encoding="utf-8"))
    trades = pd.read_csv(trades_path)

    validation = validation_gate_report(validation_rows)
    filters = frozen_filter_report(trades)
    frozen = proof["frozen_test"]

    scenario_map = {row["scenario"]: row for row in filters["rows"]}
    zero = scenario_map["base"]["costs"]["0.0"]
    base = scenario_map["base"]["costs"]["80.0"]
    volume_500 = scenario_map["volume_ge_500"]["costs"]["80.0"]
    combined = scenario_map[
        "combined_dte_5_30_oi_2000_volume_500"
    ]["costs"]["80.0"]

    result = {
        "status": "PHASE1_DIAGNOSTIC_EXECUTED",
        "source_paths": {
            "proof": str(proof_path),
            "validation": str(validation_path),
            "trades": str(trades_path),
        },
        "repository_semantics": {
            "current_regression_target": "target_net_return",
            "current_binary_target": "target_positive",
            "entry": "NEXT_SESSION_OPEN",
            "exit": "STOP_FIRST_ELSE_TARGET_ELSE_NEXT_CLOSE",
            "stop_loss_fraction": float(STOP_LOSS_PCT),
            "stop_loss_percent": float(STOP_LOSS_PCT * 100.0),
            "take_profit_fraction": float(TAKE_PROFIT_PCT),
            "take_profit_percent": float(TAKE_PROFIT_PCT * 100.0),
            "fixed_2_to_1_breakeven_formula_fully_applicable": False,
            "reason": (
                "Many trades exit at next-session close rather than exactly at "
                "the stop or target, so empirical average win/loss controls break-even."
            ),
        },
        "framework_claims": [
            {
                "claim": "current_target_is_simple_next_premium_difference",
                "status": "REJECTED_BY_REPOSITORY_CODE",
            },
            {
                "claim": "binary_profitability_target_is_new",
                "status": "REJECTED_ALREADY_IMPLEMENTED",
            },
            {
                "claim": "rank_quintile_target_is_new",
                "status": "SUPPORTED_FOR_PRE_FROZEN_RESEARCH_ONLY",
            },
            {
                "claim": "smote_should_be_used",
                "status": "REJECTED_UNNECESSARY_AND_HIGH_LEAKAGE_RISK",
            },
            {
                "claim": "fixed_33pct_breakeven_proves_3pct_edge",
                "status": "REJECTED_BY_EMPIRICAL_EXIT_DISTRIBUTION",
            },
            {
                "claim": "regime_diagnosis_can_use_current_model_artifact",
                "status": "BLOCKED_NO_REGIME_SERIES_IN_ARTIFACT",
            },
            {
                "claim": "dynamic_realized_vol_stop_can_be_validated_from_eod_ohlc",
                "status": "BLOCKED_INTRADAY_PATH_AND_REFERENCE_SERIES_REQUIRED",
            },
            {
                "claim": "live_ready_by_week_10_or_sharpe_forecast",
                "status": "REJECTED_UNSUPPORTED_FORWARD_CLAIM",
            },
        ],
        "pre_frozen_validation_gate": validation,
        "frozen_filter_diagnostics": filters,
        "frozen_baseline": {
            "days": int(frozen["days"]),
            "attempted_trades": int(frozen["attempted_trades"]),
            "filled_trades": int(frozen["filled_trades"]),
            "row_roc_auc": float(frozen["row_roc_auc"]),
            "median_daily_spearman": float(frozen["median_daily_spearman"]),
            "mean_top_k_overlap": float(frozen["mean_top_k_overlap"]),
            "zero_cost": zero,
            "base_80bps": base,
        },
        "phase1_answers": {
            "target_bottleneck": {
                "status": "NOT_ISOLATED",
                "proof": (
                    "Regression and binary profitability targets already exist; "
                    "both validation and frozen evidence are weak."
                ),
            },
            "entry_filter_bottleneck": {
                "status": "POST_HOC_HYPOTHESIS_SUPPORTED_NOT_VALIDATED",
                "volume_ge_500_80bps_profit_factor": float(
                    volume_500["profit_factor"] or 0.0
                ),
                "volume_ge_500_80bps_return": float(
                    volume_500["compounded_total_return"]
                ),
                "combined_80bps_profit_factor": float(
                    combined["profit_factor"] or 0.0
                ),
                "combined_80bps_return": float(
                    combined["compounded_total_return"]
                ),
            },
            "regime_bottleneck": {
                "status": "BLOCKED",
                "proof": "No NIFTY/VIX or validated regime label series is stored in the model artifact.",
            },
        },
        "decision": {
            "validation_candidates_passing": int(validation["candidates_passing"]),
            "frozen_should_have_remained_closed_under_new_gate": bool(
                validation["all_candidates_failed"]
            ),
            "current_model_rejected": True,
            "next_valid_experiment": (
                "Nested chronological pre-frozen validation of volume/liquidity "
                "eligibility and rank-target alternatives. Create a new untouched "
                "holdout before any later final test."
            ),
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "promotion_allowed": False,
            "frozen_configuration_tuning_allowed": False,
        },
    }
    return result


def write_reports(report: dict, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "corrected_framework_phase1.json"
    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    validation_rows = report["pre_frozen_validation_gate"]["rows"]
    pd.DataFrame(validation_rows).drop(columns=["gates"], errors="ignore").to_csv(
        output_dir / "validation_gate.csv", index=False
    )
    filter_rows = []
    for scenario in report["frozen_filter_diagnostics"]["rows"]:
        for cost, metrics in scenario["costs"].items():
            filter_rows.append({
                "scenario": scenario["scenario"],
                "cost_bps": float(cost),
                "trades": scenario["trades"],
                "retained_fraction": scenario["retained_fraction"],
                **metrics,
            })
    pd.DataFrame(filter_rows).to_csv(
        output_dir / "frozen_filter_diagnostics.csv", index=False
    )
    pd.DataFrame(report["framework_claims"]).to_csv(
        output_dir / "framework_claims.csv", index=False
    )

    decision = report["decision"]
    lines = [
        "# Genesis_System3 Corrected Framework Phase-1 Diagnostic",
        "",
        f"- Status: **{report['status']}**",
        f"- Validation candidates: **{report['pre_frozen_validation_gate']['candidates_evaluated']}**",
        f"- Validation candidates passing: **{report['pre_frozen_validation_gate']['candidates_passing']}**",
        f"- Frozen should have remained closed: **{str(decision['frozen_should_have_remained_closed_under_new_gate']).lower()}**",
        f"- Stop / target: **{report['repository_semantics']['stop_loss_percent']:.0f}% / {report['repository_semantics']['take_profit_percent']:.0f}%**",
        f"- Live trading enabled: **{str(decision['live_trading_enabled']).lower()}**",
        f"- Promotion allowed: **{str(decision['promotion_allowed']).lower()}**",
        "",
        "## Phase-1 answers",
        "",
    ]
    for name, value in report["phase1_answers"].items():
        lines.append(f"- `{name}`: **{value['status']}**")
    lines += [
        "",
        "## Decision",
        "",
        decision["next_valid_experiment"],
        "",
        "The frozen filter results are post-hoc diagnostics only and cannot be used "
        "to select or promote a strategy.",
    ]
    md_path = output_dir / "corrected_framework_phase1.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    files = [
        json_path,
        output_dir / "validation_gate.csv",
        output_dir / "frozen_filter_diagnostics.csv",
        output_dir / "framework_claims.csv",
        md_path,
    ]
    manifest = {
        "files": [
            {
                "path": path.name,
                "bytes": path.stat().st_size,
            }
            for path in files
        ],
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "promotion_allowed": False,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return files + [manifest_path]
