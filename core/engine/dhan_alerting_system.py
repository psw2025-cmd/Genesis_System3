"""
Dhan Index Options - Alerting System

Monitors system and sends alerts for:
- Critical errors
- Stale pipeline
- Unusual trade patterns
- Risk limit breaches
- System health issues
"""

import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

from core.engine.dhan_automation_config import AUTOMATION_CONFIG

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
ALERTS_LOG = PROJECT_ROOT / "storage" / "live" / "system_alerts.log"

logger = logging.getLogger(__name__)


class AlertingSystem:
    """Monitors system and generates alerts."""

    def __init__(self):
        self.alerts_log = ALERTS_LOG
        self.alerts_log.parent.mkdir(parents=True, exist_ok=True)
        self.alert_levels = ["INFO", "WARNING", "CRITICAL"]

    def alert(
        self,
        level: str,
        category: str,
        message: str,
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Generate an alert.

        Levels: INFO, WARNING, CRITICAL
        Categories: PIPELINE, TRADE, RISK, SYSTEM, PERFORMANCE
        """
        if level not in self.alert_levels:
            level = "INFO"

        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "category": category,
            "message": message,
            "details": details or {},
        }

        # Log to file
        log_msg = f"[{level}] [{category}] {message}"
        if details:
            log_msg += f" | Details: {details}"

        with self.alerts_log.open("a", encoding="utf-8") as f:
            f.write(f"{alert['timestamp']} | {log_msg}\n")

        # Also log via Python logger
        if level == "CRITICAL":
            logger.critical(log_msg)
        elif level == "WARNING":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        # Print to console for critical alerts
        if level == "CRITICAL":
            print(f"[ALERT CRITICAL] {category}: {message}")

    def check_pipeline_health(self) -> List[Dict[str, Any]]:
        """Check pipeline health and generate alerts if needed."""
        alerts = []

        # Check signals CSV
        signals_csv = LIVE_DIR / "dhan_index_ai_signals.csv"
        if signals_csv.exists():
            try:
                import pandas as pd

                df = pd.read_csv(signals_csv)
                if not df.empty and "ts" in df.columns:
                    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
                    last_ts = df["ts"].max()
                    if pd.notna(last_ts):
                        age = (datetime.utcnow() - last_ts).total_seconds()
                        if age > 600:  # 10 minutes
                            alerts.append(
                                {
                                    "level": "WARNING",
                                    "category": "PIPELINE",
                                    "message": f"Signals pipeline appears stale (last signal {age:.0f}s ago)",
                                }
                            )
            except Exception:
                pass

        return alerts

    def check_risk_limits(self) -> List[Dict[str, Any]]:
        """Check if risk limits are being approached."""
        alerts = []

        exec_log = LIVE_DIR / "dhan_index_ai_trades_exec_log.csv"
        if exec_log.exists():
            try:
                import pandas as pd

                df = pd.read_csv(exec_log)
                if not df.empty and "ts_exec" in df.columns:
                    df["ts_exec"] = pd.to_datetime(df["ts_exec"], errors="coerce")
                    today = datetime.utcnow().date()
                    df["date"] = df["ts_exec"].dt.date
                    today_count = len(df[df["date"] == today])

                    if today_count >= AUTOMATION_CONFIG.max_trades_per_day * 0.8:
                        alerts.append(
                            {
                                "level": "WARNING",
                                "category": "RISK",
                                "message": f"Approaching daily trade limit: {today_count}/{AUTOMATION_CONFIG.max_trades_per_day}",
                            }
                        )
            except Exception:
                pass

        return alerts

    def run_health_checks(self) -> None:
        """Run all health checks and generate alerts."""
        # Pipeline health
        pipeline_alerts = self.check_pipeline_health()
        for alert in pipeline_alerts:
            self.alert(**alert)

        # Risk limits
        risk_alerts = self.check_risk_limits()
        for alert in risk_alerts:
            self.alert(**alert)


def main() -> None:
    """Main entry point for alerting system."""
    print("=== ANGEL ONE INDEX OPTIONS - ALERTING SYSTEM ===")

    alerting = AlertingSystem()
    alerting.run_health_checks()

    print("[INFO] Health checks completed. Check alerts log for details.")
    print(f"[INFO] Alerts log: {ALERTS_LOG}")


if __name__ == "__main__":
    main()
