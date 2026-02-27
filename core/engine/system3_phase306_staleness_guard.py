"""
System3 Phase 306 - Real-Time Staleness & Latency Guard

Detects and marks stale or delayed snapshots.
AUTO-HEAL INTEGRATED: Automatically triggers recovery actions.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)

SIGNALS_CSV = STORAGE_LIVE / "angel_index_ai_signals.csv"
STALENESS_CSV = STORAGE_META / "system3_staleness_flags_306.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_staleness_guard_306.md"

STALE_THRESHOLD_SEC = 90  # > 90 seconds = STALE
EXPIRED_THRESHOLD_SEC = 300  # > 5 minutes = EXPIRED
RECENT_SNAPSHOTS = 100  # Last N snapshots to check

# Auto-heal configuration
AUTO_HEAL_ENABLED = True
AUTO_HEAL_TRIGGER_FILE = STORAGE_META / "system3_heal_trigger.json"


def load_csv_robust(path: Path) -> pd.DataFrame:
    """Load CSV with robust error handling."""
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, engine="python", on_bad_lines="skip")
    except Exception:
        return pd.DataFrame()


def classify_staleness(latency_seconds: float) -> str:
    """Classify staleness state."""
    if latency_seconds > EXPIRED_THRESHOLD_SEC:
        return "EXPIRED"
    elif latency_seconds > STALE_THRESHOLD_SEC:
        return "STALE"
    else:
        return "FRESH"


def trigger_auto_heal(reason: str, severity: str = "MEDIUM") -> None:
    """Trigger auto-heal orchestrator."""
    if not AUTO_HEAL_ENABLED:
        return

    try:
        trigger_data = {
            "timestamp": datetime.now().isoformat(),
            "triggered_by": "phase306_staleness_guard",
            "reason": reason,
            "severity": severity,
        }

        with AUTO_HEAL_TRIGGER_FILE.open("w", encoding="utf-8") as f:
            import json

            json.dump(trigger_data, f, indent=2)

    except Exception:
        pass


def run_phase306(**kwargs) -> Dict[str, Any]:
    """Run Phase 306: Real-Time Staleness & Latency Guard.

    AUTO-HEAL: Triggers healing if EXPIRED data detected.
    """
    errors = []
    auto_heal_triggered = False

    try:
        df = load_csv_robust(SIGNALS_CSV)

        if df.empty:
            return {
                "phase": 306,
                "status": "WARN",
                "details": "Signals CSV not found or empty",
                "outputs": {"report_file": str(REPORT_PATH), "flags_csv": str(STALENESS_CSV)},
                "errors": [],
            }

        # Get recent snapshots
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.dropna(subset=["ts"]).sort_values("ts")
            df_recent = df.tail(RECENT_SNAPSHOTS).copy()
        else:
            df_recent = df.tail(RECENT_SNAPSHOTS).copy()

        if df_recent.empty:
            return {
                "phase": 306,
                "status": "WARN",
                "details": "No recent data to analyze",
                "outputs": {"report_file": str(REPORT_PATH), "flags_csv": str(STALENESS_CSV)},
                "errors": [],
            }

        # Compute latency per underlying
        now = datetime.now()
        staleness_data = []

        if "underlying" in df_recent.columns:
            for underlying in df_recent["underlying"].unique():
                df_u = df_recent[df_recent["underlying"] == underlying]
                if "ts" in df_u.columns:
                    latest_ts = df_u["ts"].max()
                    if pd.notna(latest_ts):
                        latency = (now - latest_ts).total_seconds()
                        state = classify_staleness(latency)
                        staleness_data.append(
                            {
                                "underlying": underlying,
                                "last_ts": latest_ts.isoformat() if hasattr(latest_ts, "isoformat") else str(latest_ts),
                                "latency_seconds": latency,
                                "staleness_state": state,
                            }
                        )
        else:
            # No underlying column - analyze overall
            if "ts" in df_recent.columns:
                latest_ts = df_recent["ts"].max()
                if pd.notna(latest_ts):
                    latency = (now - latest_ts).total_seconds()
                    state = classify_staleness(latency)
                    staleness_data.append(
                        {
                            "underlying": "ALL",
                            "last_ts": latest_ts.isoformat() if hasattr(latest_ts, "isoformat") else str(latest_ts),
                            "latency_seconds": latency,
                            "staleness_state": state,
                        }
                    )

        # Save CSV flags
        if staleness_data:
            df_flags = pd.DataFrame(staleness_data)
            df_flags.to_csv(STALENESS_CSV, index=False)
        else:
            df_flags = pd.DataFrame()

        # Generate report
        report_lines = [
            "# System3 Staleness & Latency Guard Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Current Time**: {now.isoformat()}\n\n",
        ]

        if staleness_data:
            report_lines.append("## Staleness Status by Underlying\n\n")
            report_lines.append("| Underlying | Last Timestamp | Latency (seconds) | State |\n")
            report_lines.append("|------------|----------------|-------------------|-------|\n")

            for item in staleness_data:
                report_lines.append(
                    f"| {item['underlying']} | {item['last_ts']} | {item['latency_seconds']:.1f} | {item['staleness_state']} |\n"
                )

            # Summary
            fresh_count = sum(1 for item in staleness_data if item["staleness_state"] == "FRESH")
            stale_count = sum(1 for item in staleness_data if item["staleness_state"] == "STALE")
            expired_count = sum(1 for item in staleness_data if item["staleness_state"] == "EXPIRED")

            report_lines.append("\n## Summary\n\n")
            report_lines.append(f"- **FRESH**: {fresh_count}\n")
            report_lines.append(f"- **STALE**: {stale_count}\n")
            report_lines.append(f"- **EXPIRED**: {expired_count}\n")

            if expired_count > 0:
                report_lines.append("\n⚠️ **WARNING**: Some underlyings have EXPIRED data!\n")
        else:
            report_lines.append("No staleness data available.\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        if staleness_data:
            expired_count = sum(1 for item in staleness_data if item["staleness_state"] == "EXPIRED")
            if expired_count > 0:
                status = "WARN"

                # Auto-heal integration: Trigger healing for expired data
                trigger_auto_heal(reason=f"{expired_count} underlyings have EXPIRED data", severity="HIGH")
                auto_heal_triggered = True

        return {
            "phase": 306,
            "status": status,
            "details": f"Analyzed {len(staleness_data)} underlyings",
            "outputs": {
                "underlyings_checked": len(staleness_data),
                "fresh_count": sum(1 for item in staleness_data if item["staleness_state"] == "FRESH"),
                "stale_count": sum(1 for item in staleness_data if item["staleness_state"] == "STALE"),
                "expired_count": sum(1 for item in staleness_data if item["staleness_state"] == "EXPIRED"),
                "report_file": str(REPORT_PATH),
                "flags_csv": str(STALENESS_CSV),
                "auto_heal_triggered": auto_heal_triggered,
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(str(e))
        return {
            "phase": 306,
            "status": "ERROR",
            "details": f"Exception: {e}",
            "outputs": {"report_file": str(REPORT_PATH), "flags_csv": str(STALENESS_CSV)},
            "errors": errors,
        }
