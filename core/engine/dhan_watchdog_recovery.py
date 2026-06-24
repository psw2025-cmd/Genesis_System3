"""
Dhan Index Options - Watchdog & Recovery Process

Monitors system health and recovers from failures:
- Checks if live signals loop is running
- Validates data pipeline integrity
- Recovers from common errors
- Sends alerts for critical issues
"""

import os
import time
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
SIGNALS_CSV = LIVE_DIR / "dhan_index_ai_signals.csv"
LOG_DIR = PROJECT_ROOT / "logs"


class SystemWatchdog:
    """Monitors and recovers system health."""

    def __init__(self):
        self.signals_csv = SIGNALS_CSV
        self.last_check = None

    def check_signals_pipeline(self) -> dict:
        """Check if signals pipeline is active."""
        result = {
            "status": "UNKNOWN",
            "last_signal_ts": None,
            "age_seconds": None,
            "is_stale": False,
        }

        if not self.signals_csv.exists():
            result["status"] = "NO_DATA"
            return result

        try:
            import pandas as pd

            df = pd.read_csv(self.signals_csv)
            if df.empty:
                result["status"] = "EMPTY"
                return result

            if "ts" in df.columns:
                df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
                last_ts = df["ts"].max()
                result["last_signal_ts"] = last_ts.isoformat() if pd.notna(last_ts) else None

                if pd.notna(last_ts):
                    age = (datetime.utcnow() - last_ts).total_seconds()
                    result["age_seconds"] = age
                    result["is_stale"] = age > 300  # 5 minutes
                    result["status"] = "STALE" if result["is_stale"] else "ACTIVE"
                else:
                    result["status"] = "INVALID_TIMESTAMPS"
            else:
                result["status"] = "NO_TIMESTAMP_COLUMN"
        except Exception as e:
            result["status"] = f"ERROR: {e}"

        return result

    def check_disk_space(self) -> dict:
        """Check available disk space."""
        try:
            import shutil

            total, used, free = shutil.disk_usage(PROJECT_ROOT)
            free_gb = free / (1024**3)
            total_gb = total / (1024**3)
            percent_free = (free / total) * 100 if total > 0 else 0

            return {
                "status": "OK" if percent_free > 10 else "LOW",
                "free_gb": free_gb,
                "total_gb": total_gb,
                "percent_free": percent_free,
            }
        except Exception:
            return {"status": "UNKNOWN"}

    def check_log_files(self) -> dict:
        """Check log file sizes."""
        result = {"status": "OK", "large_files": []}

        if not LOG_DIR.exists():
            return result

        try:
            for log_file in LOG_DIR.glob("*.log"):
                size_mb = log_file.stat().st_size / (1024**2)
                if size_mb > 100:  # > 100 MB
                    result["large_files"].append(
                        {
                            "file": str(log_file.name),
                            "size_mb": size_mb,
                        }
                    )
                    result["status"] = "WARNING"
        except Exception:
            pass

        return result

    def recover_stale_pipeline(self) -> bool:
        """Attempt to recover from stale pipeline."""
        # For now, just log the issue
        # In production, could restart processes, send alerts, etc.
        print("[WATCHDOG] Pipeline appears stale. Manual intervention may be required.")
        return False

    def run_health_check(self) -> dict:
        """Run complete health check."""
        health = {
            "timestamp": datetime.utcnow().isoformat(),
            "signals_pipeline": self.check_signals_pipeline(),
            "disk_space": self.check_disk_space(),
            "log_files": self.check_log_files(),
            "overall_status": "OK",
        }

        # Determine overall status
        if health["signals_pipeline"]["status"] in ["STALE", "NO_DATA", "ERROR"]:
            health["overall_status"] = "WARNING"
        if health["disk_space"]["status"] == "LOW":
            health["overall_status"] = "CRITICAL"

        return health

    def print_health_report(self) -> None:
        """Print health check report."""
        health = self.run_health_check()
        print("=== SYSTEM HEALTH CHECK ===")
        print(f"Timestamp: {health['timestamp']}")
        print(f"\nOverall Status: {health['overall_status']}")
        print(f"\nSignals Pipeline: {health['signals_pipeline']['status']}")
        if health["signals_pipeline"].get("last_signal_ts"):
            print(f"  Last signal: {health['signals_pipeline']['last_signal_ts']}")
            print(f"  Age: {health['signals_pipeline'].get('age_seconds', 0):.0f} seconds")
        print(f"\nDisk Space: {health['disk_space']['status']}")
        if "percent_free" in health["disk_space"]:
            print(f"  Free: {health['disk_space']['percent_free']:.1f}%")
        print(f"\nLog Files: {health['log_files']['status']}")
        if health["log_files"].get("large_files"):
            print("  Large files:")
            for f in health["log_files"]["large_files"]:
                print(f"    {f['file']}: {f['size_mb']:.1f} MB")


def main() -> None:
    """Main entry point for watchdog."""
    watchdog = SystemWatchdog()
    watchdog.print_health_report()


if __name__ == "__main__":
    main()
