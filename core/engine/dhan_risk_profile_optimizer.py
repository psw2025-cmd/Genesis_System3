"""
Dhan Index Options - Position Sizing & Risk Optimizer

Suggests risk profile based on real PnL distribution.
AUTO-UPDATE: DISABLED - Only suggestions, never auto-applies.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from core.engine.dhan_real_outcome_logger import load_outcomes

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
RISK_PROFILE_JSON = CONFIG_DIR / "risk_profile_suggestions.json"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def optimize_risk_profile() -> Dict[str, Any]:
    """
    Optimize risk profile based on real PnL distribution.

    Returns:
        Dict with risk profile suggestions
    """
    df = load_outcomes()
    if df.empty:
        return {
            "status": "NO_DATA",
            "message": "No outcome data available",
        }

    if "pnl_pct" not in df.columns:
        return {
            "status": "NO_PNL_DATA",
            "message": "PnL data not available",
        }

    # Analyze PnL distribution
    pnl_series = df["pnl_pct"]

    # Suggest per-trade capital %
    # Based on Kelly Criterion approximation
    win_rate = (pnl_series > 0).sum() / len(pnl_series)
    avg_win = pnl_series[pnl_series > 0].mean() if (pnl_series > 0).sum() > 0 else 0.0
    avg_loss = abs(pnl_series[pnl_series < 0].mean()) if (pnl_series < 0).sum() > 0 else 1.0

    if avg_loss > 0:
        kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        kelly_fraction = max(0.0, min(0.25, kelly_fraction))  # Cap at 25%
    else:
        kelly_fraction = 0.05  # Conservative default

    # Suggest max daily loss cap
    daily_pnl = df.groupby(df["timestamp"].str[:10])["pnl_pct"].sum() if "timestamp" in df.columns else pd.Series()
    max_daily_loss = abs(daily_pnl.min()) if len(daily_pnl) > 0 else 10.0
    suggested_daily_loss_cap = max(5.0, min(20.0, max_daily_loss * 1.5))

    # Suggest max open trades
    # Based on trade frequency and win rate
    if "timestamp" in df.columns:
        daily_trade_counts = df.groupby(df["timestamp"].str[:10]).size()
        avg_daily_trades = daily_trade_counts.mean() if len(daily_trade_counts) > 0 else 5.0
    else:
        avg_daily_trades = 5.0

    # Adjust based on win rate
    if win_rate > 0.6:
        suggested_max_trades = int(avg_daily_trades * 1.2)
    elif win_rate < 0.4:
        suggested_max_trades = int(avg_daily_trades * 0.8)
    else:
        suggested_max_trades = int(avg_daily_trades)

    suggested_max_trades = max(3, min(20, suggested_max_trades))

    suggestions = {
        "status": "SUCCESS",
        "per_trade_capital_pct": float(kelly_fraction * 100),
        "max_daily_loss_cap_pct": float(suggested_daily_loss_cap),
        "max_open_trades": int(suggested_max_trades),
        "rationale": {
            "win_rate": float(win_rate * 100),
            "avg_win": float(avg_win),
            "avg_loss": float(avg_loss),
            "kelly_fraction": float(kelly_fraction),
            "analysis_date": datetime.utcnow().isoformat(),
        },
    }

    return suggestions


def save_risk_profile_suggestions(suggestions: Dict[str, Any]) -> Path:
    """
    Save risk profile suggestions to JSON.

    Returns:
        Path to saved JSON
    """
    with RISK_PROFILE_JSON.open("w", encoding="utf-8") as f:
        json.dump(suggestions, f, indent=2)

    return RISK_PROFILE_JSON


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - RISK PROFILE OPTIMIZER ===")
    print("[INFO] AUTO-UPDATE: DISABLED - Suggestions only\n")

    suggestions = optimize_risk_profile()

    if suggestions["status"] == "SUCCESS":
        print("=== RISK PROFILE SUGGESTIONS ===\n")
        print(f"Per-Trade Capital %: {suggestions['per_trade_capital_pct']:.2f}%")
        print(f"Max Daily Loss Cap %: {suggestions['max_daily_loss_cap_pct']:.2f}%")
        print(f"Max Open Trades: {suggestions['max_open_trades']}")

        print("\n=== RATIONALE ===")
        rationale = suggestions["rationale"]
        print(f"Win Rate: {rationale['win_rate']:.1f}%")
        print(f"Avg Win: {rationale['avg_win']:.2f}%")
        print(f"Avg Loss: {rationale['avg_loss']:.2f}%")
        print(f"Kelly Fraction: {rationale['kelly_fraction']:.3f}")

        # Save
        save_path = save_risk_profile_suggestions(suggestions)
        print(f"\n[SAVE] Risk profile suggestions saved to: {save_path}")
        print("\n[NOTE] These are SUGGESTIONS ONLY. Manual review required before applying.")
    else:
        print(f"[INFO] {suggestions.get('message', 'Suggestions not available')}")


if __name__ == "__main__":
    main()
