"""
System3 Phase 92 - Session Replay Player

Reconstruct a day's events as a chronological replay log.
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
SESSION_REPLAY_DIR = STORAGE_ULTRA / "session_replay"

# Input files
SIGNALS_CSV = STORAGE_LIVE / "dhan_index_ai_signals.csv"
TRADES_PLAN_CSV = STORAGE_LIVE / "dhan_index_ai_trades_plan.csv"
PNL_LOG_CSV = STORAGE_LIVE / "dhan_index_ai_pnl_log.csv"

SESSION_REPLAY_DIR.mkdir(parents=True, exist_ok=True)


def load_data_for_date(date_str: str) -> List[Dict[str, Any]]:
    """Load all data for a specific date."""
    events = []

    # Load signals
    if SIGNALS_CSV.exists():
        try:
            df = pd.read_csv(SIGNALS_CSV)
            if "ts" in df.columns:
                date_df = df[df["ts"].str.contains(date_str, na=False)]
                for _, row in date_df.iterrows():
                    events.append(
                        {
                            "timestamp": row.get("ts", ""),
                            "type": "SIGNAL",
                            "underlying": row.get("underlying", ""),
                            "strike": row.get("strike", 0),
                            "side": row.get("side", ""),
                            "pred_label": row.get("pred_label", "HOLD"),
                            "pred_confidence": row.get("pred_confidence", 0.0),
                        }
                    )
        except Exception:
            pass

    # Load trade plans
    if TRADES_PLAN_CSV.exists():
        try:
            df = pd.read_csv(TRADES_PLAN_CSV)
            if "ts" in df.columns:
                date_df = df[df["ts"].str.contains(date_str, na=False)]
                for _, row in date_df.iterrows():
                    events.append(
                        {
                            "timestamp": row.get("ts", ""),
                            "type": "TRADE_PLAN",
                            "underlying": row.get("underlying", ""),
                            "strike": row.get("strike", 0),
                            "side": row.get("side", ""),
                            "entry_price": row.get("entry_price", 0.0),
                            "target_price": row.get("target_price", 0.0),
                            "sl_price": row.get("sl_price", 0.0),
                        }
                    )
        except Exception:
            pass

    # Load PnL
    if PNL_LOG_CSV.exists():
        try:
            df = pd.read_csv(PNL_LOG_CSV)
            if "ts" in df.columns:
                date_df = df[df["ts"].str.contains(date_str, na=False)]
                for _, row in date_df.iterrows():
                    events.append(
                        {
                            "timestamp": row.get("ts", ""),
                            "type": "PNL",
                            "underlying": row.get("underlying", ""),
                            "strike": row.get("strike", 0),
                            "side": row.get("side", ""),
                            "pnl_pct": row.get("pnl_pct", 0.0),
                            "result": row.get("result", "NO_DATA"),
                        }
                    )
        except Exception:
            pass

    return events


def generate_replay(date_str: str) -> None:
    """Generate session replay for a date."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 92 - SESSION REPLAY PLAYER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load events
    events = load_data_for_date(date_str)

    if not events:
        print(f"[PH92] No events found for date {date_str}")
        return

    # Sort by timestamp
    events.sort(key=lambda x: x.get("timestamp", ""))

    # Generate output filename
    date_formatted = date_str.replace("-", "")
    output_file = SESSION_REPLAY_DIR / f"phase92_replay_log_{date_formatted}.md"

    # Write replay log
    with output_file.open("w", encoding="utf-8") as f:
        f.write(f"# System3 Session Replay - {date_str}\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for event in events:
            timestamp = event.get("timestamp", "")
            event_type = event.get("type", "UNKNOWN")

            f.write(f"[{timestamp}] TYPE={event_type}")

            if event_type == "SIGNAL":
                f.write(
                    f" underlying={event.get('underlying')} strike={event.get('strike')} "
                    f"side={event.get('side')} label={event.get('pred_label')} "
                    f"conf={event.get('pred_confidence', 0.0):.2f}"
                )
            elif event_type == "TRADE_PLAN":
                f.write(
                    f" underlying={event.get('underlying')} strike={event.get('strike')} "
                    f"side={event.get('side')} entry={event.get('entry_price', 0.0):.2f}"
                )
            elif event_type == "PNL":
                f.write(
                    f" underlying={event.get('underlying')} strike={event.get('strike')} "
                    f"side={event.get('side')} pnl={event.get('pnl_pct', 0.0):.2f}% "
                    f"result={event.get('result', 'NO_DATA')}"
                )

            f.write("\n")

    print(f"[PH92] Reconstructed session for date={date_str}")
    print(f"[PH92] Replay log written to {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System3 Phase 92 - Session Replay Player")
    parser.add_argument(
        "--date", type=str, default=datetime.now().strftime("%Y-%m-%d"), help="Date to replay (YYYY-MM-DD)"
    )

    args = parser.parse_args()

    try:
        generate_replay(args.date)
        print("\n[PH92] Session replay generation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH92] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
