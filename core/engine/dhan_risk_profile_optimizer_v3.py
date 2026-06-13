"""
Dhan Index Options - Risk Profile Optimizer V3

Suggests ideal risk ranges based on real outcomes.
Reports only - no position-size changes.
SAFE MODE ONLY - Read-only suggestions.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

from core.engine.dhan_unified_outcome_logger_v3 import get_outcome_stats

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
REAL_OUTCOMES_CSV = LEARNING_DIR / "real_outcomes.csv"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def optimize_risk_profile_v3() -> Dict[str, Any]:
    """
    Optimize risk profile based on real outcomes (SUGGESTIONS ONLY).

    Suggests ideal risk ranges.
    Reports only - no position-size changes.

    Returns:
        Dict with risk profile suggestions
    """
    print("=== ANGEL ONE INDEX OPTIONS - RISK PROFILE OPTIMIZER V3 ===")
    print("[INFO] SAFE MODE - Suggestions only, NO position-size changes\n")

    if not REAL_OUTCOMES_CSV.exists():
        return {
            "status": "NO_DATA",
            "message": "No outcome data available",
        }

    try:
        df = pd.read_csv(REAL_OUTCOMES_CSV)
        if df.empty:
            return {
                "status": "EMPTY",
                "message": "Outcomes CSV is empty",
            }

        if "pnl_pct" not in df.columns:
            return {
                "status": "NO_PNL_DATA",
                "message": "PnL data not available",
            }

        # Analyze PnL distribution
        pnl_series = df["pnl_pct"]

        # Suggest per-trade capital % (Kelly Criterion approximation)
        win_rate = (pnl_series > 0).sum() / len(pnl_series)
        avg_win = pnl_series[pnl_series > 0].mean() if (pnl_series > 0).sum() > 0 else 0.0
        avg_loss = abs(pnl_series[pnl_series < 0].mean()) if (pnl_series < 0).sum() > 0 else 1.0

        if avg_loss > 0 and avg_win > 0:
            kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly_fraction = max(0.0, min(0.25, kelly_fraction))  # Cap at 25%
        else:
            kelly_fraction = 0.05  # Conservative default

        # Suggest max daily loss cap
        if "exit_timestamp" in df.columns:
            df["date"] = pd.to_datetime(df["exit_timestamp"], errors="coerce").dt.date
            daily_pnl = df.groupby("date")["pnl_pct"].sum()
            max_daily_loss = abs(daily_pnl.min()) if len(daily_pnl) > 0 else 10.0
        else:
            max_daily_loss = 10.0

        suggested_daily_loss_cap = max(5.0, min(20.0, max_daily_loss * 1.5))

        # Suggest max open trades
        if "exit_timestamp" in df.columns:
            daily_trade_counts = df.groupby("date").size()
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
            "applied": False,  # Explicitly marked as not applied
            "note": "SUGGESTIONS ONLY - NOT APPLIED",
        }

        return suggestions

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def save_risk_profile_suggestions(suggestions: Dict[str, Any]) -> Path:
    """
    Save risk profile suggestions to JSON.

    Returns:
        Path to saved JSON
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    json_path = REPORTS_DIR / f"risk_profile_suggestions_{today}.json"

    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "applied": False,  # Explicitly marked as not applied
        "note": "These are SUGGESTIONS ONLY. Manual review required before applying.",
        "suggestions": suggestions,
    }

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    return json_path


def main() -> None:
    """Main entry point."""
    suggestions = optimize_risk_profile_v3()

    if suggestions["status"] == "SUCCESS":
        print("=== RISK PROFILE SUGGESTIONS (NOT APPLIED) ===\n")
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
        print(f"\n⚠️  {suggestions['note']}")
        print("⚠️  IMPORTANT: These are SUGGESTIONS ONLY. They have NOT been applied.")
    else:
        print(f"[INFO] {suggestions.get('message', 'Suggestions not available')}")


if __name__ == "__main__":
    main()
