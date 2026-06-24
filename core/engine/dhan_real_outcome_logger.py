"""
Dhan Index Options - Real Outcome Logger

Logs every trade (even DRY RUN) into persistent learning table.
AUTO-UPDATE: DISABLED - Only logs, never modifies configs.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
OUTCOMES_CSV = LEARNING_DIR / "dhan_real_outcomes.csv"

# Ensure directory exists
LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def log_trade_outcome(
    underlying: str,
    strike: float,
    side: str,
    entry_price: float,
    exit_price: float,
    pnl_pct: float,
    holding_time: float,
    reason_exit: str,
    signal_confidence: float,
    score: float,
    thresholds_used: Dict[str, float],
    regime: str,
    model_version: str,
    snapshot_index: int,
) -> bool:
    """
    Log a trade outcome to learning table.

    Args:
        underlying: Underlying name (NIFTY, BANKNIFTY, etc.)
        strike: Strike price
        side: Option side (CE/PE)
        entry_price: Entry price
        exit_price: Exit price
        pnl_pct: PnL percentage
        holding_time: Holding time in minutes
        reason_exit: Exit reason (TP/SL/TIMEOUT)
        signal_confidence: Signal confidence at entry
        score: Expected move score at entry
        thresholds_used: Dict with thresholds used
        regime: Market regime at entry
        model_version: Model version used
        snapshot_index: Snapshot index from signals CSV

    Returns:
        True if logged successfully
    """
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "underlying": underlying,
        "strike": strike,
        "side": side,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "pnl_pct": pnl_pct,
        "holding_time": holding_time,
        "reason_exit": reason_exit,
        "signal_confidence": signal_confidence,
        "score": score,
        "thresholds_confidence": thresholds_used.get("min_confidence", 0.0),
        "thresholds_score": thresholds_used.get("min_abs_score", 0.0),
        "regime": regime,
        "model_version": model_version,
        "snapshot_index": snapshot_index,
    }

    # Append to CSV (idempotent)
    try:
        if OUTCOMES_CSV.exists():
            df = pd.read_csv(OUTCOMES_CSV)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            df = pd.DataFrame([row])

        df.to_csv(OUTCOMES_CSV, index=False)
        return True
    except Exception as e:
        print(f"[OUTCOME LOGGER] Failed to log outcome: {e}")
        return False


def load_outcomes() -> pd.DataFrame:
    """
    Load all outcomes from learning table.

    Returns:
        DataFrame with all outcomes
    """
    if not OUTCOMES_CSV.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(OUTCOMES_CSV)
        return df
    except Exception as e:
        print(f"[OUTCOME LOGGER] Failed to load outcomes: {e}")
        return pd.DataFrame()


def get_outcome_summary() -> Dict[str, Any]:
    """
    Get summary statistics from outcomes.

    Returns:
        Dict with summary stats
    """
    df = load_outcomes()
    if df.empty:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "avg_pnl": 0.0,
            "total_pnl": 0.0,
        }

    if "pnl_pct" not in df.columns:
        return {
            "total_trades": len(df),
            "win_rate": 0.0,
            "avg_pnl": 0.0,
            "total_pnl": 0.0,
        }

    total_trades = len(df)
    win_rate = (df["pnl_pct"] > 0).sum() / total_trades * 100.0 if total_trades > 0 else 0.0
    avg_pnl = df["pnl_pct"].mean()
    total_pnl = df["pnl_pct"].sum()

    return {
        "total_trades": total_trades,
        "win_rate": float(win_rate),
        "avg_pnl": float(avg_pnl),
        "total_pnl": float(total_pnl),
    }


def main() -> None:
    """Test outcome logger."""
    print("=== ANGEL ONE INDEX OPTIONS - REAL OUTCOME LOGGER ===")
    print(f"[INFO] Outcomes CSV: {OUTCOMES_CSV}")

    # Test log
    result = log_trade_outcome(
        underlying="NIFTY",
        strike=22000.0,
        side="CE",
        entry_price=100.0,
        exit_price=110.0,
        pnl_pct=10.0,
        holding_time=30.0,
        reason_exit="TP",
        signal_confidence=0.85,
        score=0.35,
        thresholds_used={"min_confidence": 0.80, "min_abs_score": 0.30},
        regime="NORMAL",
        model_version="v1.0",
        snapshot_index=1,
    )

    if result:
        print("[SUCCESS] Test outcome logged")
    else:
        print("[ERROR] Failed to log test outcome")

    # Show summary
    summary = get_outcome_summary()
    print(f"\n[SUMMARY] Total trades: {summary['total_trades']}")
    print(f"[SUMMARY] Win rate: {summary['win_rate']:.1f}%")
    print(f"[SUMMARY] Avg PnL: {summary['avg_pnl']:.2f}%")


if __name__ == "__main__":
    main()
