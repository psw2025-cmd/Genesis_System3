"""
System3 Phase 76 - GENI Self-Critique Engine

GENI reviews past signals vs outcomes and creates a self-critique report:
where it was right, wrong, late, or too conservative.
"""

import sys
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"

# Input files
SIGNALS_CSV = STORAGE_LIVE / "angel_index_ai_signals.csv"
TRADES_PLAN_CSV = STORAGE_LIVE / "angel_index_ai_trades_plan.csv"
PNL_LOG_CSV = STORAGE_LIVE / "angel_index_ai_pnl_log.csv"

# Output files
OUTPUT_JSON = STORAGE_ULTRA / "phase76_geni_self_review.json"
OUTPUT_MD = STORAGE_ULTRA / "phase76_geni_self_review.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)


def load_data() -> Dict[str, pd.DataFrame]:
    """Load signals, trades, and PnL data."""
    data = {}

    if SIGNALS_CSV.exists():
        try:
            data["signals"] = pd.read_csv(SIGNALS_CSV)
            print(f"[PH76] Loaded {len(data['signals'])} signals")
        except Exception as e:
            print(f"[PH76] Error loading signals: {e}")
            data["signals"] = pd.DataFrame()
    else:
        data["signals"] = pd.DataFrame()

    if TRADES_PLAN_CSV.exists():
        try:
            data["trades"] = pd.read_csv(TRADES_PLAN_CSV)
            print(f"[PH76] Loaded {len(data['trades'])} trades")
        except Exception as e:
            print(f"[PH76] Error loading trades: {e}")
            data["trades"] = pd.DataFrame()
    else:
        data["trades"] = pd.DataFrame()

    if PNL_LOG_CSV.exists():
        try:
            data["pnl"] = pd.read_csv(PNL_LOG_CSV)
            print(f"[PH76] Loaded {len(data['pnl'])} PnL rows")
        except Exception as e:
            print(f"[PH76] Error loading PnL: {e}")
            data["pnl"] = pd.DataFrame()
    else:
        data["pnl"] = pd.DataFrame()

    return data


def analyze_signal(signal_row: pd.Series, trades_df: pd.DataFrame, pnl_df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze a single signal against trades and outcomes."""
    # Create unique key for matching
    signal_ts = signal_row.get("ts", "")
    underlying = signal_row.get("underlying", "")
    strike = signal_row.get("strike", 0)
    side = signal_row.get("side", "")
    pred_label = signal_row.get("pred_label", "HOLD")
    pred_confidence = signal_row.get("pred_confidence", 0.0)
    expected_move_score = signal_row.get("expected_move_score", 0.0)

    result = {
        "was_trade_taken": False,
        "direction_correct": None,
        "missed_profit_opportunity": False,
        "too_conservative": False,
        "too_aggressive": False,
    }

    # Check if trade was taken
    if not trades_df.empty:
        trade_match = trades_df[
            (trades_df["underlying"] == underlying)
            & (trades_df["strike"] == strike)
            & (trades_df["side"] == side)
            & (trades_df["ts"] == signal_ts)
        ]
        if not trade_match.empty:
            result["was_trade_taken"] = True

    # Check PnL outcome
    if not pnl_df.empty:
        pnl_match = pnl_df[
            (pnl_df["underlying"] == underlying)
            & (pnl_df["strike"] == strike)
            & (pnl_df["side"] == side)
            & (pnl_df["ts"] == signal_ts)
        ]
        if not pnl_match.empty:
            pnl_row = pnl_match.iloc[0]
            pnl_pct = pnl_row.get("pnl_pct", 0.0)
            result_pnl = pnl_row.get("result", "NO_DATA")

            # Determine direction correctness
            if result_pnl != "NO_DATA" and pnl_pct != 0:
                if pred_label == "BUY_CE" and pnl_pct > 0:
                    result["direction_correct"] = True
                elif pred_label == "BUY_PE" and pnl_pct > 0:
                    result["direction_correct"] = True
                elif pred_label in ["BUY_CE", "BUY_PE"] and pnl_pct < 0:
                    result["direction_correct"] = False

                # Check if too aggressive (loss > threshold, e.g., -5%)
                if pnl_pct < -5.0:
                    result["too_aggressive"] = True

                # Check missed opportunity
                max_fav_pct = pnl_row.get("max_fav_pct", 0.0)
                if max_fav_pct > 10.0 and not result["was_trade_taken"]:
                    result["missed_profit_opportunity"] = True

    # Check if too conservative (strong signal but no trade)
    if pred_label in ["BUY_CE", "BUY_PE"] and pred_confidence > 0.8 and expected_move_score > 0.3:
        if not result["was_trade_taken"]:
            result["too_conservative"] = True

    return result


def compute_aggregate_metrics(signals_df: pd.DataFrame, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregate metrics overall and per underlying."""
    overall = {
        "total_signals": len(signals_df),
        "total_trades": sum(1 for r in analysis_results if r["was_trade_taken"]),
        "correct_direction_count": sum(1 for r in analysis_results if r["direction_correct"] is True),
        "incorrect_direction_count": sum(1 for r in analysis_results if r["direction_correct"] is False),
        "missed_opportunities": sum(1 for r in analysis_results if r["missed_profit_opportunity"]),
        "too_conservative_count": sum(1 for r in analysis_results if r["too_conservative"]),
        "too_aggressive_count": sum(1 for r in analysis_results if r["too_aggressive"]),
    }

    # Per underlying
    per_underlying = defaultdict(
        lambda: {
            "total_signals": 0,
            "total_trades": 0,
            "correct_direction_count": 0,
            "incorrect_direction_count": 0,
            "missed_opportunities": 0,
            "too_conservative_count": 0,
            "too_aggressive_count": 0,
        }
    )

    for idx, signal_row in signals_df.iterrows():
        underlying = signal_row.get("underlying", "UNKNOWN")
        result = analysis_results[idx]

        per_underlying[underlying]["total_signals"] += 1
        if result["was_trade_taken"]:
            per_underlying[underlying]["total_trades"] += 1
        if result["direction_correct"] is True:
            per_underlying[underlying]["correct_direction_count"] += 1
        if result["direction_correct"] is False:
            per_underlying[underlying]["incorrect_direction_count"] += 1
        if result["missed_profit_opportunity"]:
            per_underlying[underlying]["missed_opportunities"] += 1
        if result["too_conservative"]:
            per_underlying[underlying]["too_conservative_count"] += 1
        if result["too_aggressive"]:
            per_underlying[underlying]["too_aggressive_count"] += 1

    return {
        "overall": overall,
        "per_underlying": dict(per_underlying),
    }


def generate_self_critique() -> Dict[str, Any]:
    """Generate self-critique report."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 76 - GENI SELF-CRITIQUE ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load data
    data = load_data()
    signals_df = data["signals"]
    trades_df = data["trades"]
    pnl_df = data["pnl"]

    if signals_df.empty:
        print("[PH76] No signals found. Creating empty report.")
        return {
            "timestamp": datetime.now().isoformat(),
            "overall": {
                "total_signals": 0,
                "total_trades": 0,
                "correct_direction_count": 0,
                "incorrect_direction_count": 0,
                "missed_opportunities": 0,
                "too_conservative_count": 0,
                "too_aggressive_count": 0,
            },
            "per_underlying": {},
        }

    # Analyze each signal
    print(f"[PH76] Analyzing {len(signals_df)} signals...")
    analysis_results = []
    for idx, signal_row in signals_df.iterrows():
        result = analyze_signal(signal_row, trades_df, pnl_df)
        analysis_results.append(result)

    # Compute metrics
    metrics = compute_aggregate_metrics(signals_df, analysis_results)

    # Create report
    report = {
        "timestamp": datetime.now().isoformat(),
        **metrics,
    }

    # Save JSON
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[PH76] Self-critique summary written to {OUTPUT_JSON}")

    # Generate MD
    generate_markdown(report)
    print(f"[PH76] Markdown report written to {OUTPUT_MD}")

    return report


def generate_markdown(report: Dict[str, Any]) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 76 - GENI Self-Critique Report\n\n")
        f.write(f"**Date**: {report['timestamp']}\n\n")

        # Overall summary
        overall = report["overall"]
        f.write("## Overall Summary\n\n")
        f.write(f"- **Total Signals**: {overall['total_signals']}\n")
        f.write(f"- **Total Trades**: {overall['total_trades']}\n")
        f.write(f"- **Correct Direction**: {overall['correct_direction_count']}\n")
        f.write(f"- **Incorrect Direction**: {overall['incorrect_direction_count']}\n")
        f.write(f"- **Missed Opportunities**: {overall['missed_opportunities']}\n")
        f.write(f"- **Too Conservative**: {overall['too_conservative_count']}\n")
        f.write(f"- **Too Aggressive**: {overall['too_aggressive_count']}\n\n")

        # Per underlying table
        if report["per_underlying"]:
            f.write("## Per Underlying Analysis\n\n")
            f.write(
                "| Underlying | Signals | Trades | Correct | Incorrect | Missed | Too Conservative | Too Aggressive |\n"
            )
            f.write(
                "|------------|---------|--------|---------|-----------|--------|-------------------|----------------|\n"
            )

            for underlying, stats in sorted(report["per_underlying"].items()):
                f.write(
                    f"| {underlying} | {stats['total_signals']} | {stats['total_trades']} | "
                    f"{stats['correct_direction_count']} | {stats['incorrect_direction_count']} | "
                    f"{stats['missed_opportunities']} | {stats['too_conservative_count']} | "
                    f"{stats['too_aggressive_count']} |\n"
                )
            f.write("\n")

        # Too Conservative section
        total_too_conservative = overall["too_conservative_count"]
        if total_too_conservative > 0:
            f.write("## Too Conservative\n\n")
            f.write(f"**Count**: {total_too_conservative}\n\n")
            f.write("GENI identified strong signals (high confidence, high expected move) but trades were not taken. ")
            f.write("This suggests thresholds may be too strict or risk management is overly cautious.\n\n")

        # Too Aggressive section
        total_too_aggressive = overall["too_aggressive_count"]
        if total_too_aggressive > 0:
            f.write("## Too Aggressive\n\n")
            f.write(f"**Count**: {total_too_aggressive}\n\n")
            f.write("GENI identified trades that resulted in significant losses (>5%). ")
            f.write("This suggests risk thresholds may need to be tightened or entry criteria refined.\n\n")


def main():
    """Main entry point."""
    try:
        report = generate_self_critique()
        print("\n[PH76] Self-critique generation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH76] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
