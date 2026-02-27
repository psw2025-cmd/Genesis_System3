"""
System3 Phase 93 - Operator Override Engine

Allow operator to define override rules and log what they would block.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
CONFIG_DIR = PROJECT_ROOT / "config"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"

# Config file
CONFIG_JSON = CONFIG_DIR / "system3_operator_override.json"

# Input files
SIGNALS_CSV = STORAGE_LIVE / "angel_index_ai_signals.csv"
TRADES_PLAN_CSV = STORAGE_LIVE / "angel_index_ai_trades_plan.csv"

# Output files
STATE_JSON = STORAGE_ULTRA / "phase93_override_state.json"
LOG_MD = STORAGE_ULTRA / "phase93_override_log.md"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load operator override config."""
    if not CONFIG_JSON.exists():
        # Create default
        default_config = {
            "blocked_underlyings": [],
            "force_hold_all": False,
            "max_trades_per_day": 10,
        }
        with CONFIG_JSON.open("w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    try:
        with CONFIG_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[PH93] Error loading config: {e}")
        return {
            "blocked_underlyings": [],
            "force_hold_all": False,
            "max_trades_per_day": 10,
        }


def evaluate_overrides() -> Dict[str, Any]:
    """Evaluate operator overrides on today's signals/trades."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 93 - OPERATOR OVERRIDE ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load config
    config = load_config()

    # Load today's data
    today = datetime.now().strftime("%Y-%m-%d")
    blocked_signals = []
    blocked_trades = []

    # Check signals
    if SIGNALS_CSV.exists():
        try:
            df = pd.read_csv(SIGNALS_CSV)
            if "ts" in df.columns:
                today_signals = df[df["ts"].str.contains(today, na=False)]

                for _, row in today_signals.iterrows():
                    underlying = row.get("underlying", "")
                    blocked = False
                    reason = ""

                    if config.get("force_hold_all", False):
                        blocked = True
                        reason = "force_hold_all enabled"
                    elif underlying in config.get("blocked_underlyings", []):
                        blocked = True
                        reason = f"underlying {underlying} is blocked"

                    if blocked:
                        blocked_signals.append(
                            {
                                "ts": row.get("ts", ""),
                                "underlying": underlying,
                                "strike": row.get("strike", 0),
                                "side": row.get("side", ""),
                                "reason": reason,
                            }
                        )
        except Exception:
            pass

    # Check trades
    if TRADES_PLAN_CSV.exists():
        try:
            df = pd.read_csv(TRADES_PLAN_CSV)
            if "ts" in df.columns:
                today_trades = df[df["ts"].str.contains(today, na=False)]

                # Check max trades per day
                max_trades = config.get("max_trades_per_day", 10)
                if len(today_trades) > max_trades:
                    excess = today_trades.iloc[max_trades:]
                    for _, row in excess.iterrows():
                        blocked_trades.append(
                            {
                                "ts": row.get("ts", ""),
                                "underlying": row.get("underlying", ""),
                                "strike": row.get("strike", 0),
                                "side": row.get("side", ""),
                                "reason": f"exceeds max_trades_per_day ({max_trades})",
                            }
                        )

                # Check blocked underlyings
                for _, row in today_trades.iterrows():
                    underlying = row.get("underlying", "")
                    if underlying in config.get("blocked_underlyings", []):
                        blocked_trades.append(
                            {
                                "ts": row.get("ts", ""),
                                "underlying": underlying,
                                "strike": row.get("strike", 0),
                                "side": row.get("side", ""),
                                "reason": f"underlying {underlying} is blocked",
                            }
                        )
        except Exception:
            pass

    state = {
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "blocked_signals": blocked_signals,
        "blocked_trades": blocked_trades,
        "total_blocked": len(blocked_signals) + len(blocked_trades),
    }

    # Save state
    with STATE_JSON.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    # Generate MD
    generate_log_md(state)

    print(f"[PH93] Evaluated operator overrides on {len(blocked_signals) + len(blocked_trades)} candidates")

    return state


def generate_log_md(state: Dict[str, Any]) -> None:
    """Generate markdown log."""
    with LOG_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 93 - Operator Override Log\n\n")
        f.write(f"**Date**: {state['timestamp']}\n\n")

        f.write(f"**Total Blocked**: {state['total_blocked']}\n")
        f.write(f"- Blocked Signals: {len(state['blocked_signals'])}\n")
        f.write(f"- Blocked Trades: {len(state['blocked_trades'])}\n\n")

        if state["blocked_signals"]:
            f.write("## Blocked Signals\n\n")
            for sig in state["blocked_signals"]:
                f.write(f"- {sig['ts']} | {sig['underlying']} | {sig['strike']} | {sig['side']} | {sig['reason']}\n")
            f.write("\n")

        if state["blocked_trades"]:
            f.write("## Blocked Trades\n\n")
            for trade in state["blocked_trades"]:
                f.write(
                    f"- {trade['ts']} | {trade['underlying']} | {trade['strike']} | {trade['side']} | {trade['reason']}\n"
                )


def main():
    """Main entry point."""
    try:
        state = evaluate_overrides()
        print("\n[PH93] Operator override evaluation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH93] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
