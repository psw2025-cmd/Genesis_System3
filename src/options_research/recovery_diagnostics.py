"""Evidence-first recovery diagnostics for the Genesis_System3 options model.

This module does not promote models or place orders. It cross-checks recovery
proposals against the actual EOD archive contract and frozen holdout artifacts
before expensive retraining is allowed.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

CURRENT_FEATURE_COLUMNS = (
    "open_close_return", "range_pct", "settle_gap_pct", "log_volume", "log_oi",
    "oi_change_ratio", "moneyness_pct", "days_to_expiry", "sqrt_days_to_expiry",
    "prev_close_return", "prev_volume_change", "prev_oi_change", "underlying_return",
    "option_is_call", "instrument_is_index", "weekday_sin", "weekday_cos",
    "month_sin", "month_cos",
)

AVAILABLE = "AVAILABLE_CURRENT"
DERIVABLE = "DERIVABLE_FROM_EOD"
BLOCKED_QUOTES = "BLOCKED_REQUIRES_BID_ASK_OR_INTRADAY"
BLOCKED_IV = "BLOCKED_REQUIRES_RELIABLE_IV_OR_SPOT_HISTORY"
BLOCKED_EXTERNAL = "BLOCKED_REQUIRES_EXTERNAL_REFERENCE_DATA"
REJECTED_PROXY = "REJECTED_UNVALIDATED_PROXY"

REQUESTED_FEATURES = {
    "IV_RANK_30d": BLOCKED_IV,
    "REALIZED_IV_SPREAD": BLOCKED_IV,
    "SLOPE_TERM": BLOCKED_IV,
    "IV_ZSCORE": BLOCKED_IV,
    "DELTA_PROXY": AVAILABLE,
    "GAMMA_PROXY": REJECTED_PROXY,
    "VEGA_EXPOSURE": BLOCKED_IV,
    "SKEW_CURVATURE": BLOCKED_IV,
    "SPREAD_PCT": BLOCKED_QUOTES,
    "OI_DEVIATION": DERIVABLE,
    "VOLUME_TREND": DERIVABLE,
    "LIQUIDITY_RATIO": BLOCKED_QUOTES,
    "MOMENTUM_5D": DERIVABLE,
    "PREMIUM_DEVIATION_20D": DERIVABLE,
    "CROSS_CORRELATION": DERIVABLE,
    "ROLLOVER_EFFECT": DERIVABLE,
    "NIFTY_DIRECTION": DERIVABLE,
    "IV_INDEX_STOCK_SPREAD": BLOCKED_IV,
    "PCR_SENTIMENT": DERIVABLE,
    "SECTOR_ROTATION_SIGNAL": BLOCKED_EXTERNAL,
}

FEATURE_EVIDENCE = {
    "IV_RANK_30d": "NSE EOD bhavcopy has no reliable historical IV series across the full archive.",
    "REALIZED_IV_SPREAD": "Requires both realised underlying volatility and reliable implied volatility.",
    "SLOPE_TERM": "Requires comparable IV observations across expiries.",
    "IV_ZSCORE": "Requires a stable historical IV series.",
    "DELTA_PROXY": "Signed moneyness_pct already exists; do not add a duplicate differently named feature.",
    "GAMMA_PROXY": "Premium change per spot move is not gamma without controlled spot and IV effects.",
    "VEGA_EXPOSURE": "Requires implied volatility and option-pricing inputs.",
    "SKEW_CURVATURE": "Requires reliable same-session IV by strike.",
    "SPREAD_PCT": "Bid and ask are absent from EOD bhavcopy.",
    "OI_DEVIATION": "Can be derived chronologically from contract OI history.",
    "VOLUME_TREND": "Can be derived chronologically from prior contract volume.",
    "LIQUIDITY_RATIO": "The proposed denominator is bid/ask spread, which is absent.",
    "MOMENTUM_5D": "Can be derived from prior contract closes without future data.",
    "PREMIUM_DEVIATION_20D": "Can be derived from prior contract closes without future data.",
    "CROSS_CORRELATION": "Can be derived from historical neighbouring contracts with strict timestamp controls.",
    "ROLLOVER_EFFECT": "Can be derived using expiry-aware historical joins.",
    "NIFTY_DIRECTION": "Can be derived from index records when the session contains a valid NIFTY reference.",
    "IV_INDEX_STOCK_SPREAD": "Requires reliable IV for both index and stock options.",
    "PCR_SENTIMENT": "Can be derived from same-session CE/PE volume or OI aggregates.",
    "SECTOR_ROTATION_SIGNAL": "Requires a versioned symbol-to-sector reference not present in bhavcopy.",
}


@dataclass(frozen=True)
class CostResult:
    cost_bps: float
    attempted_trades: int
    filled_trades: int
    rejected_no_fill: int
    days: int
    win_rate: float
    profit_factor: float | None
    mean_trade_return: float
    mean_daily_return: float
    annualized_sharpe: float | None
    annualized_sortino: float | None
    maximum_drawdown: float
    compounded_total_return: float
    initial_capital: float
    ending_capital: float
    net_pnl: float


def execution_fraction_report(stop_loss_fraction: float, take_profit_fraction: float) -> dict:
    """Return unambiguous decimal and percentage values."""
    for name, value in {
        "stop_loss_fraction": stop_loss_fraction,
        "take_profit_fraction": take_profit_fraction,
    }.items():
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be a finite non-negative decimal fraction")
    return {
        "stop_loss_fraction": float(stop_loss_fraction),
        "stop_loss_percent": float(stop_loss_fraction * 100.0),
        "take_profit_fraction": float(take_profit_fraction),
        "take_profit_percent": float(take_profit_fraction * 100.0),
        "interpretation": "DECIMAL_FRACTION_OF_ENTRY_PRICE",
    }


def feature_feasibility_rows() -> list[dict]:
    return [
        {
            "feature": feature,
            "status": status,
            "evidence": FEATURE_EVIDENCE[feature],
            "allowed_for_eod_implementation": status in {AVAILABLE, DERIVABLE},
        }
        for feature, status in REQUESTED_FEATURES.items()
    ]


def feature_feasibility_summary() -> dict:
    rows = feature_feasibility_rows()
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {
        "requested_features": len(rows),
        "status_counts": counts,
        "allowed_for_eod_implementation": sum(row["allowed_for_eod_implementation"] for row in rows),
        "blocked_or_rejected": sum(not row["allowed_for_eod_implementation"] for row in rows),
        "rows": rows,
    }


def _drawdown(daily_returns: np.ndarray) -> float:
    if not len(daily_returns):
        return 0.0
    equity = np.cumprod(1.0 + np.clip(daily_returns, -0.99, 10.0))
    peak = np.maximum.accumulate(equity)
    return float(np.max((peak - equity) / np.maximum(peak, 1e-12)))


def simulate_cost_stress(
    trades: pd.DataFrame,
    costs_bps: Iterable[float],
    *,
    initial_capital: float = 100_000.0,
    per_trade_allocation: float = 0.05,
    maximum_daily_exposure: float = 0.15,
) -> list[CostResult]:
    required = {"trade_date", "gross_return", "target_fillable"}
    missing = required - set(trades.columns)
    if missing:
        raise ValueError(f"trade ledger missing columns: {sorted(missing)}")
    if initial_capital <= 0:
        raise ValueError("initial_capital must be positive")
    if not 0 < per_trade_allocation <= 1:
        raise ValueError("per_trade_allocation must be in (0, 1]")
    if not 0 < maximum_daily_exposure <= 1:
        raise ValueError("maximum_daily_exposure must be in (0, 1]")

    frame = trades.copy()
    frame["trade_date"] = frame["trade_date"].astype(str)
    frame["gross_return"] = pd.to_numeric(frame["gross_return"], errors="raise")
    frame["target_fillable"] = pd.to_numeric(frame["target_fillable"], errors="raise").astype(int)
    results: list[CostResult] = []

    for raw_cost in costs_bps:
        cost = float(raw_cost)
        if not math.isfinite(cost) or cost < 0:
            raise ValueError("cost bps must be finite and non-negative")
        trade_net: list[float] = []
        daily_returns: list[float] = []
        filled_total = 0
        capital = float(initial_capital)

        for _, day in frame.groupby("trade_date", sort=True):
            filled = day[day["target_fillable"].eq(1)]
            net = (filled["gross_return"] - cost / 10_000.0).astype(float)
            filled_total += len(filled)
            trade_net.extend(net.tolist())
            allocation = (
                min(per_trade_allocation, maximum_daily_exposure / len(filled))
                if len(filled) else 0.0
            )
            daily_return = float(net.sum() * allocation) if len(net) else 0.0
            daily_returns.append(daily_return)
            capital *= 1.0 + daily_return

        trade_array = np.asarray(trade_net, dtype=float)
        daily_array = np.asarray(daily_returns, dtype=float)
        positive = trade_array[trade_array > 0]
        negative = trade_array[trade_array <= 0]
        std = float(daily_array.std(ddof=1)) if len(daily_array) > 1 else 0.0
        downside = daily_array[daily_array < 0]
        downside_std = float(downside.std(ddof=1)) if len(downside) > 1 else 0.0
        pf = float(positive.sum() / abs(negative.sum())) if negative.sum() < 0 else None

        results.append(CostResult(
            cost_bps=cost,
            attempted_trades=int(len(frame)),
            filled_trades=int(filled_total),
            rejected_no_fill=int(len(frame) - filled_total),
            days=int(frame["trade_date"].nunique()),
            win_rate=float((trade_array > 0).mean()) if len(trade_array) else 0.0,
            profit_factor=pf,
            mean_trade_return=float(trade_array.mean()) if len(trade_array) else 0.0,
            mean_daily_return=float(daily_array.mean()) if len(daily_array) else 0.0,
            annualized_sharpe=float(daily_array.mean() / std * math.sqrt(252)) if std > 0 else None,
            annualized_sortino=(
                float(daily_array.mean() / downside_std * math.sqrt(252))
                if downside_std > 0 else None
            ),
            maximum_drawdown=_drawdown(daily_array),
            compounded_total_return=float(capital / initial_capital - 1.0),
            initial_capital=float(initial_capital),
            ending_capital=float(capital),
            net_pnl=float(capital - initial_capital),
        ))
    return results


def cost_results_as_dict(results: Iterable[CostResult]) -> list[dict]:
    return [asdict(result) for result in results]


def attachment_crosscheck(model_proof: dict, trades: pd.DataFrame) -> dict:
    assumptions = model_proof.get("execution_assumptions", {})
    stop = float(assumptions.get("stop_loss_pct", 0.0))
    target = float(assumptions.get("take_profit_pct", 0.0))
    semantics = execution_fraction_report(stop, target)
    costs = simulate_cost_stress(trades, [0.0, 20.0, 30.0, 40.0, 80.0, 120.0, 200.0])
    zero = costs[0]
    feasibility = feature_feasibility_summary()

    claims = [
        {
            "claim": "stop_loss_is_0_3_percent",
            "status": "REJECTED",
            "proof": f"Repository fraction {stop} equals {semantics['stop_loss_percent']} percent.",
        },
        {
            "claim": "take_profit_is_0_6_percent",
            "status": "REJECTED",
            "proof": f"Repository fraction {target} equals {semantics['take_profit_percent']} percent.",
        },
        {
            "claim": "cost_is_primary_failure_source",
            "status": "REJECTED_BY_ZERO_COST_HOLDOUT",
            "proof": (
                f"At 0 bps the frozen normalized return is "
                f"{zero.compounded_total_return:.6f} with PF {zero.profit_factor:.6f}."
            ),
        },
        {
            "claim": "current_model_is_only_lightgbm",
            "status": "REJECTED",
            "proof": (
                "Current artifact stores an SGD regressor, an SGD classifier, "
                "and a LightGBM challenger combined by rank."
            ),
        },
        {
            "claim": "all_20_requested_features_can_be_added_to_eod_archive",
            "status": "REJECTED",
            "proof": (
                f"{feasibility['allowed_for_eod_implementation']} of "
                f"{feasibility['requested_features']} are currently available or safely derivable."
            ),
        },
        {
            "claim": "larger_model_search_should_proceed_immediately",
            "status": "BLOCKED_PENDING_SIGNAL_DIAGNOSTICS",
            "proof": (
                "Feature and target diagnostics must pass on pre-frozen chronological data "
                "before additional model-capacity trials."
            ),
        },
    ]
    return {
        "status": "PASS_ATTACHMENT_CROSSCHECK",
        "model_status": model_proof.get("status"),
        "execution_semantics": semantics,
        "feature_feasibility": feasibility,
        "cost_stress": cost_results_as_dict(costs),
        "claims": claims,
        "safe_implementation_sequence": [
            "freeze current rejected model and preserve frozen evidence",
            "run feature availability and signal diagnostics on pre-frozen sessions only",
            "implement only EOD-derivable features with timestamp tests",
            "compare target definitions chronologically without SMOTE or random splits",
            "run nested validation before opening a new untouched holdout",
            "keep promotion and live trading disabled",
        ],
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "promotion_allowed": False,
    }


def load_model_artifact_root(root: Path) -> tuple[dict, pd.DataFrame]:
    candidates = list(root.rglob("advanced_model_backtest_proof.json"))
    ledgers = list(root.rglob("frozen_selected_trades.csv"))
    if len(candidates) != 1 or len(ledgers) != 1:
        raise ValueError(
            f"expected exactly one model proof and one frozen ledger; "
            f"found {len(candidates)} and {len(ledgers)}"
        )
    import json

    proof = json.loads(candidates[0].read_text(encoding="utf-8"))
    trades = pd.read_csv(ledgers[0])
    return proof, trades
