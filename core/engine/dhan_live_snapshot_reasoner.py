"""
Dhan Index Options - Live Snapshot Reasoner

Provides reasoning and explanations for live snapshot signals.
SAFE MODE ONLY - Read-only analysis.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
SIGNALS_CSV = LIVE_DIR / "dhan_index_ai_signals.csv"


def reason_about_snapshot(df_signals: pd.DataFrame) -> Dict[str, Any]:
    """
    Provide reasoning about current snapshot signals.

    Args:
        df_signals: DataFrame with current signals

    Returns:
        Dict with reasoning and explanations
    """
    if df_signals.empty:
        return {
            "status": "NO_DATA",
            "message": "No signals to reason about",
        }

    reasoning = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "total_signals": len(df_signals),
        "signal_distribution": {},
        "key_insights": [],
        "recommendations": [],
    }

    # Signal distribution
    if "pred_label" in df_signals.columns:
        label_counts = df_signals["pred_label"].value_counts()
        reasoning["signal_distribution"] = label_counts.to_dict()

        # Insights
        buy_signals = len(df_signals[df_signals["pred_label"].isin(["BUY_CE", "BUY_PE"])])
        if buy_signals > 0:
            reasoning["key_insights"].append(f"Found {buy_signals} BUY signals in snapshot")
        else:
            reasoning["key_insights"].append("No BUY signals in current snapshot")

    # Confidence analysis
    if "pred_confidence" in df_signals.columns:
        avg_conf = df_signals["pred_confidence"].mean()
        reasoning["key_insights"].append(f"Average confidence: {avg_conf:.3f}")

        if avg_conf < 0.7:
            reasoning["recommendations"].append("Low average confidence - consider waiting for stronger signals")
        elif avg_conf > 0.9:
            reasoning["recommendations"].append("High average confidence - signals are strong")

    # Score analysis
    if "expected_move_score" in df_signals.columns:
        avg_score = df_signals["expected_move_score"].abs().mean()
        reasoning["key_insights"].append(f"Average expected move score: {avg_score:.3f}")

    return reasoning


def analyze_latest_snapshot() -> Dict[str, Any]:
    """
    Analyze the latest snapshot from signals CSV.

    Returns:
        Dict with reasoning
    """
    if not SIGNALS_CSV.exists():
        return {
            "status": "NO_FILE",
            "message": "Signals CSV not found",
        }

    try:
        df = pd.read_csv(SIGNALS_CSV)
        if df.empty:
            return {
                "status": "EMPTY",
                "message": "No signals in CSV",
            }

        # Get latest snapshot
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.sort_values("ts")
            latest = df.tail(100)  # Last 100 rows
        else:
            latest = df.tail(100)

        return reason_about_snapshot(latest)

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - LIVE SNAPSHOT REASONER ===")
    print("[INFO] SAFE MODE - Read-only analysis\n")

    reasoning = analyze_latest_snapshot()

    if reasoning["status"] in ["NO_FILE", "EMPTY", "NO_DATA"]:
        print(f"[INFO] {reasoning.get('message', 'No data available')}")
        return

    if reasoning["status"] == "ERROR":
        print(f"[ERROR] {reasoning.get('message', 'Analysis failed')}")
        return

    print("=== SNAPSHOT REASONING ===\n")
    print(f"Total Signals: {reasoning['total_signals']}")

    if reasoning["signal_distribution"]:
        print("\nSignal Distribution:")
        for label, count in reasoning["signal_distribution"].items():
            print(f"  {label}: {count}")

    if reasoning["key_insights"]:
        print("\nKey Insights:")
        for insight in reasoning["key_insights"]:
            print(f"  • {insight}")

    if reasoning["recommendations"]:
        print("\nRecommendations:")
        for rec in reasoning["recommendations"]:
            print(f"  → {rec}")


if __name__ == "__main__":
    main()
