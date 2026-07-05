"""
Dhan Index Options - Unified Outcome Logger V3

Logs real outcomes after market close.
Output: learning/real_outcomes.csv
SAFE MODE ONLY - Read-only logging, no threshold changes, no config changes.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
REAL_OUTCOMES_CSV = LEARNING_DIR / "real_outcomes.csv"
OUTCOME_PLACEHOLDERS_CSV = LEARNING_DIR / "outcome_placeholders.csv"

LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def log_real_outcome(
    signal_timestamp: str,
    underlying: str,
    strike: float,
    side: str,
    entry_price: float,
    exit_price: float,
    exit_timestamp: str,
    pnl_pct: float,
    exit_reason: str,
    entry_confidence: float,
    entry_score: float,
) -> bool:
    """
    Log a real outcome after market close.

    Args:
        signal_timestamp: Original signal timestamp
        underlying: Underlying name
        strike: Strike price
        side: Option side (CE/PE)
        entry_price: Entry price
        exit_price: Exit price
        exit_timestamp: Exit timestamp
        pnl_pct: PnL percentage
        exit_reason: Exit reason (TP/SL/TIMEOUT)
        entry_confidence: Confidence at entry
        entry_score: Score at entry

    Returns:
        True if logged successfully
    """
    row = {
        "signal_timestamp": signal_timestamp,
        "underlying": underlying,
        "strike": strike,
        "side": side,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "exit_timestamp": exit_timestamp,
        "pnl_pct": pnl_pct,
        "exit_reason": exit_reason,
        "entry_confidence": entry_confidence,
        "entry_score": entry_score,
        "logged_at": datetime.utcnow().isoformat(),
    }

    try:
        if REAL_OUTCOMES_CSV.exists():
            df = pd.read_csv(REAL_OUTCOMES_CSV)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            df = pd.DataFrame([row])

        df.to_csv(REAL_OUTCOMES_CSV, index=False)
        return True
    except Exception as e:
        print(f"[OUTCOME LOGGER] Failed to log outcome: {e}")
        return False


def update_placeholders_from_outcomes() -> Dict[str, Any]:
    """
    Update placeholders with actual outcomes.

    Reads from outcome_placeholders.csv and updates with real outcomes.
    Does NOT modify thresholds or configs.

    Returns:
        Dict with update results
    """
    if not OUTCOME_PLACEHOLDERS_CSV.exists():
        return {
            "status": "NO_PLACEHOLDERS",
            "message": "No placeholders found",
        }

    if not REAL_OUTCOMES_CSV.exists():
        return {
            "status": "NO_OUTCOMES",
            "message": "No outcomes logged yet",
        }

    try:
        df_placeholders = pd.read_csv(OUTCOME_PLACEHOLDERS_CSV)
        df_outcomes = pd.read_csv(REAL_OUTCOMES_CSV)

        # Match placeholders with outcomes by signal_timestamp + underlying + strike + side
        updated = 0
        for idx, placeholder in df_placeholders.iterrows():
            if placeholder.get("status") != "PENDING":
                continue

            # Find matching outcome
            match = df_outcomes[
                (df_outcomes["signal_timestamp"] == placeholder.get("signal_timestamp", ""))
                & (df_outcomes["underlying"] == placeholder.get("underlying", ""))
                & (df_outcomes["strike"] == placeholder.get("strike", 0.0))
                & (df_outcomes["side"] == placeholder.get("side", ""))
            ]

            if not match.empty:
                outcome = match.iloc[0]
                df_placeholders.at[idx, "exit_price"] = outcome.get("exit_price")
                df_placeholders.at[idx, "exit_timestamp"] = outcome.get("exit_timestamp")
                df_placeholders.at[idx, "pnl_pct"] = outcome.get("pnl_pct")
                df_placeholders.at[idx, "exit_reason"] = outcome.get("exit_reason")
                df_placeholders.at[idx, "status"] = "COMPLETED"
                updated += 1

        # Save updated placeholders
        df_placeholders.to_csv(OUTCOME_PLACEHOLDERS_CSV, index=False)

        return {
            "status": "SUCCESS",
            "updated": updated,
            "total_placeholders": len(df_placeholders),
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def get_outcome_stats() -> Dict[str, Any]:
    """
    Get outcome statistics (read-only).

    Returns:
        Dict with outcome stats
    """
    if not REAL_OUTCOMES_CSV.exists():
        return {
            "status": "EMPTY",
            "count": 0,
            "message": "No outcomes logged yet",
        }

    try:
        df = pd.read_csv(REAL_OUTCOMES_CSV)
        if df.empty:
            return {
                "status": "EMPTY",
                "count": 0,
            }

        stats = {
            "status": "SUCCESS",
            "total_outcomes": len(df),
        }

        if "pnl_pct" in df.columns:
            stats["win_rate"] = float((df["pnl_pct"] > 0).sum() / len(df) * 100) if len(df) > 0 else 0.0
            stats["avg_pnl"] = float(df["pnl_pct"].mean())
            stats["total_pnl"] = float(df["pnl_pct"].sum())

        if "exit_reason" in df.columns:
            stats["exit_reason_distribution"] = df["exit_reason"].value_counts().to_dict()

        if "underlying" in df.columns:
            stats["by_underlying"] = {}
            for u in df["underlying"].unique():
                df_u = df[df["underlying"] == u]
                stats["by_underlying"][u] = {
                    "count": len(df_u),
                    "win_rate": float((df_u["pnl_pct"] > 0).sum() / len(df_u) * 100) if len(df_u) > 0 else 0.0,
                    "avg_pnl": float(df_u["pnl_pct"].mean()) if "pnl_pct" in df_u.columns else 0.0,
                }

        return stats

    except Exception as e:
        return {
            "status": "ERROR",
            "count": 0,
            "error": str(e),
        }


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - UNIFIED OUTCOME LOGGER V3 ===")
    print("[INFO] SAFE MODE - Read-only logging, no threshold changes\n")

    # Update placeholders
    update_result = update_placeholders_from_outcomes()
    if update_result["status"] == "SUCCESS":
        print(f"[UPDATE] Updated {update_result['updated']} placeholders with outcomes")

    # Show stats
    stats = get_outcome_stats()
    if stats["status"] == "SUCCESS":
        print(f"\n=== OUTCOME STATISTICS ===")
        print(f"Total Outcomes: {stats['total_outcomes']}")
        if "win_rate" in stats:
            print(f"Win Rate: {stats['win_rate']:.1f}%")
            print(f"Average PnL: {stats['avg_pnl']:.2f}%")
            print(f"Total PnL: {stats['total_pnl']:.2f}%")

        if "exit_reason_distribution" in stats:
            print("\nExit Reason Distribution:")
            for reason, count in stats["exit_reason_distribution"].items():
                print(f"  {reason}: {count}")

        if "by_underlying" in stats:
            print("\nBy Underlying:")
            for u, data in stats["by_underlying"].items():
                print(
                    f"  {u}: {data['count']} trades, win_rate={data['win_rate']:.1f}%, avg_pnl={data['avg_pnl']:.2f}%"
                )
    else:
        print(f"[INFO] {stats.get('message', 'No outcome statistics available')}")


if __name__ == "__main__":
    main()
