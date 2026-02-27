"""
System3 Phase 91 - Live Control Dashboard (MD)

Provide a text/MD live dashboard snapshot of System3.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"

# Input files (for today's stats)
SIGNALS_CSV = STORAGE_LIVE / "angel_index_ai_signals.csv"
TRADES_PLAN_CSV = STORAGE_LIVE / "angel_index_ai_trades_plan.csv"
PNL_LOG_CSV = STORAGE_LIVE / "angel_index_ai_pnl_log.csv"

# Phase outputs
PHASE80_JSON = STORAGE_ULTRA / "phase80_geni_evolution_status.json"
PHASE88_JSON = STORAGE_ULTRA / "phase88_portfolio_risk.json"

# Output file
OUTPUT_MD = STORAGE_ULTRA / "phase91_live_dashboard.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)


def get_system_status() -> Dict[str, Any]:
    """Get current system status."""
    try:
        from core.engine.ultra_safety import load_ultra_safety
        from core.engine.angel_automation_config import AUTOMATION_CONFIG

        safety = load_ultra_safety()
        auto_exec = safety.get("AUTO_EXECUTE_TRADES", False) or AUTOMATION_CONFIG.auto_execute_trades

        return {
            "mode": "ULTRA",
            "profile": "BASELINE",  # Would normally detect
            "auto_exec": "ON" if auto_exec else "OFF",
            "safety_status": "LOCKDOWN" if auto_exec else "SAFE",
        }
    except Exception:
        return {
            "mode": "BASELINE",
            "profile": "BASELINE",
            "auto_exec": "OFF",
            "safety_status": "SAFE",
        }


def get_today_stats() -> Dict[str, int]:
    """Get today's statistics."""
    today = datetime.now().strftime("%Y-%m-%d")

    signals_count = 0
    trades_count = 0
    realized_pnl = 0.0

    # Count signals
    if SIGNALS_CSV.exists():
        try:
            import pandas as pd

            df = pd.read_csv(SIGNALS_CSV)
            if "ts" in df.columns:
                today_signals = df[df["ts"].str.contains(today, na=False)]
                signals_count = len(today_signals)
        except Exception:
            pass

    # Count trades
    if TRADES_PLAN_CSV.exists():
        try:
            import pandas as pd

            df = pd.read_csv(TRADES_PLAN_CSV)
            if "ts" in df.columns:
                today_trades = df[df["ts"].str.contains(today, na=False)]
                trades_count = len(today_trades)
        except Exception:
            pass

    # Calculate realized PnL
    if PNL_LOG_CSV.exists():
        try:
            import pandas as pd

            df = pd.read_csv(PNL_LOG_CSV)
            if "ts" in df.columns and "pnl_pct" in df.columns:
                today_pnl = df[df["ts"].str.contains(today, na=False)]
                if "pnl_pct" in today_pnl.columns:
                    realized_pnl = float(today_pnl["pnl_pct"].sum())
        except Exception:
            pass

    return {
        "signals_count": signals_count,
        "trades_count": trades_count,
        "realized_pnl": realized_pnl,
    }


def get_geni_recommendations() -> List[str]:
    """Get top 3 GENI recommendations from Phase 80."""
    if not PHASE80_JSON.exists():
        return []

    try:
        import json

        with PHASE80_JSON.open("r", encoding="utf-8") as f:
            phase80_data = json.load(f)
        actions = phase80_data.get("next_step_actions", [])
        return actions[:3]
    except Exception:
        return []


def get_risk_flags() -> List[str]:
    """Get HIGH risk flags from Phase 88."""
    if not PHASE88_JSON.exists():
        return []

    try:
        import json

        with PHASE88_JSON.open("r", encoding="utf-8") as f:
            phase88_data = json.load(f)
        flags = phase88_data.get("risk_flags", [])
        high_flags = [f["message"] for f in flags if f.get("level") == "HIGH"]
        return high_flags
    except Exception:
        return []


def generate_dashboard() -> None:
    """Generate live dashboard."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 91 - LIVE CONTROL DASHBOARD")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Gather data
    system_status = get_system_status()
    today_stats = get_today_stats()
    geni_recommendations = get_geni_recommendations()
    risk_flags = get_risk_flags()

    # Find largest underlying exposure
    largest_exposure = "N/A"
    if PHASE88_JSON.exists():
        try:
            import json

            with PHASE88_JSON.open("r", encoding="utf-8") as f:
                phase88_data = json.load(f)
            exposures = phase88_data.get("per_underlying_exposure", {})
            if exposures:
                largest_exposure = max(exposures.items(), key=lambda x: x[1])[0]
        except Exception:
            pass

    # Generate MD
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Live Control Dashboard\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # System Status
        f.write("## 1. System Status\n\n")
        f.write(f"- **Mode**: {system_status['mode']}\n")
        f.write(f"- **Profile**: {system_status['profile']}\n")
        f.write(f"- **Auto-execute**: {system_status['auto_exec']}\n")
        f.write(f"- **Safety Status**: {system_status['safety_status']}\n\n")

        # Today Stats
        f.write("## 2. Today Stats\n\n")
        f.write(f"- **Signals Count**: {today_stats['signals_count']}\n")
        f.write(f"- **Trades Count**: {today_stats['trades_count']}\n")
        f.write(f"- **Realized PnL**: {today_stats['realized_pnl']:.2f}%\n\n")

        # Risk
        f.write("## 3. Risk\n\n")
        f.write(f"- **Largest Underlying Exposure**: {largest_exposure}\n")
        if risk_flags:
            f.write("- **HIGH Risk Flags**:\n")
            for flag in risk_flags:
                f.write(f"  - ⚠️ {flag}\n")
        else:
            f.write("- **HIGH Risk Flags**: None\n")
        f.write("\n")

        # GENI Recommendations
        f.write("## 4. GENI Recommendations\n\n")
        if geni_recommendations:
            for i, rec in enumerate(geni_recommendations, 1):
                f.write(f"{i}. {rec}\n")
        else:
            f.write("No recommendations available. Run Phase 80 to generate recommendations.\n")
        f.write("\n")

    print(f"[PH91] Live dashboard snapshot written to {OUTPUT_MD}")


def main():
    """Main entry point."""
    try:
        generate_dashboard()
        print("\n[PH91] Dashboard generation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH91] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
