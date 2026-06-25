"""
Real-Time Alerts & Notifications System
"""

import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytz

IST = pytz.timezone("Asia/Kolkata")

# Slack delivery, OFF by default - same opt-in pattern as the API-key auth
# and kill switch: set SLACK_WEBHOOK_URL to enable. Without it, alerts
# behave exactly as before (written to alerts.jsonl only, no delivery
# channel) - this was the original gap (alerts had zero delivery channel,
# nothing ever paged a human). Only WARNING+ severity is sent to avoid
# flooding Slack with routine INFO alerts.
_SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
_SLACK_MIN_SEVERITY_RANK = {"info": 0, "warning": 1, "error": 2, "critical": 3}


def _send_slack_alert(alert: Dict[str, Any]) -> None:
    if not _SLACK_WEBHOOK_URL:
        return
    if _SLACK_MIN_SEVERITY_RANK.get(alert.get("severity"), 0) < 1:
        return
    try:
        import requests

        emoji = {"warning": ":warning:", "error": ":x:", "critical": ":rotating_light:"}.get(
            alert.get("severity"), ":bell:"
        )
        text = f"{emoji} *{alert.get('title')}* ({alert.get('type')})\n{alert.get('message')}"
        requests.post(_SLACK_WEBHOOK_URL, json={"text": text}, timeout=5)
    except Exception as e:
        print(f"[alerts] Slack delivery failed (non-fatal): {e}")


class AlertType(Enum):
    PRICE_ALERT = "price_alert"
    POSITION_ALERT = "position_alert"
    SYSTEM_ALERT = "system_alert"
    PNL_ALERT = "pnl_alert"
    SIGNAL_ALERT = "signal_alert"
    RISK_ALERT = "risk_alert"


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertsSystem:
    """
    Real-time alerts and notifications system
    """

    def __init__(self, alerts_file: Optional[Path] = None):
        if alerts_file is None:
            alerts_file = Path(__file__).parent.parent.parent / "outputs" / "alerts.jsonl"
        self.alerts_file = alerts_file
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)
        self.subscribers = []

    def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        persistent: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a new alert

        Args:
            alert_type: Type of alert
            severity: Severity level
            title: Alert title
            message: Alert message
            data: Additional data
            persistent: Whether alert should persist

        Returns:
            Alert dictionary
        """
        alert = {
            "id": f"ALERT_{datetime.now(IST).strftime('%Y%m%d%H%M%S%f')}",
            "type": alert_type.value,
            "severity": severity.value,
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now(IST).isoformat(),
            "persistent": persistent,
            "read": False,
        }

        # Append to alerts file
        try:
            with open(self.alerts_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(alert, default=str) + "\n")
        except Exception as e:
            print(f"Error writing alert: {e}")

        # Notify subscribers
        self._notify_subscribers(alert)
        _send_slack_alert(alert)

        return alert

    def check_price_alerts(
        self, symbol: str, current_price: float, targets: List[float], stop_loss: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Check if price alerts should be triggered"""
        alerts = []

        # Check targets
        for target in targets:
            if current_price >= target:
                alerts.append(
                    self.create_alert(
                        AlertType.PRICE_ALERT,
                        AlertSeverity.INFO,
                        f"Target Hit: {symbol}",
                        f"{symbol} reached target price ₹{target:.2f}",
                        {"symbol": symbol, "price": current_price, "target": target},
                    )
                )

        # Check stop loss
        if stop_loss and current_price <= stop_loss:
            alerts.append(
                self.create_alert(
                    AlertType.PRICE_ALERT,
                    AlertSeverity.WARNING,
                    f"Stop Loss Hit: {symbol}",
                    f"{symbol} hit stop loss at ₹{stop_loss:.2f}",
                    {"symbol": symbol, "price": current_price, "stop_loss": stop_loss},
                )
            )

        return alerts

    def check_position_alerts(
        self, position: Dict[str, Any], previous_position: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Check if position alerts should be triggered"""
        alerts = []

        # New position
        if previous_position is None:
            alerts.append(
                self.create_alert(
                    AlertType.POSITION_ALERT,
                    AlertSeverity.INFO,
                    f"New Position: {position.get('symbol', 'Unknown')}",
                    f"New position opened: {position.get('symbol')} x {position.get('qty', 0)}",
                    {"position": position},
                )
            )

        # Position closed
        if position.get("status") == "CLOSED" and previous_position and previous_position.get("status") != "CLOSED":
            pnl = position.get("realized_pnl", 0)
            alerts.append(
                self.create_alert(
                    AlertType.POSITION_ALERT,
                    AlertSeverity.INFO if pnl >= 0 else AlertSeverity.WARNING,
                    f"Position Closed: {position.get('symbol', 'Unknown')}",
                    f"Position closed with PnL: ₹{pnl:.2f}",
                    {"position": position},
                )
            )

        # Large PnL change
        if previous_position:
            prev_pnl = previous_position.get("unrealized_pnl", 0)
            curr_pnl = position.get("unrealized_pnl", 0)
            pnl_change = abs(curr_pnl - prev_pnl)

            if pnl_change > 1000:  # Threshold
                alerts.append(
                    self.create_alert(
                        AlertType.PNL_ALERT,
                        AlertSeverity.WARNING if pnl_change < 5000 else AlertSeverity.ERROR,
                        f"Large PnL Change: {position.get('symbol', 'Unknown')}",
                        f"PnL changed by ₹{pnl_change:.2f}",
                        {"position": position, "pnl_change": pnl_change},
                    )
                )

        return alerts

    def check_system_alerts(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if system alerts should be triggered"""
        alerts = []

        # Broker disconnected
        if health_data.get("broker_status") != "connected":
            alerts.append(
                self.create_alert(
                    AlertType.SYSTEM_ALERT,
                    AlertSeverity.ERROR,
                    "Broker Disconnected",
                    "Broker connection lost. Trading may be affected.",
                    {"broker_status": health_data.get("broker_status")},
                )
            )

        # Market status change
        market_status = health_data.get("market_status", "")
        if "closed" in market_status.lower():
            alerts.append(
                self.create_alert(
                    AlertType.SYSTEM_ALERT,
                    AlertSeverity.INFO,
                    "Market Closed",
                    "Market is now closed. Broker not ready for real data.",
                    {"market_status": market_status},
                )
            )

        # QC failures
        qc_failures = health_data.get("qc_failures", [])
        if qc_failures:
            alerts.append(
                self.create_alert(
                    AlertType.SYSTEM_ALERT,
                    AlertSeverity.WARNING,
                    "QC Failures Detected",
                    f"{len(qc_failures)} QC failures: {', '.join(qc_failures[:3])}",
                    {"qc_failures": qc_failures},
                )
            )

        # Performance SLA breach
        perf_sla = health_data.get("performance_sla", {})
        if not perf_sla.get("sla_pass", True):
            alerts.append(
                self.create_alert(
                    AlertType.SYSTEM_ALERT,
                    AlertSeverity.WARNING,
                    "Performance SLA Breach",
                    f"Cycle duration: {perf_sla.get('cycle_duration_sec', 0):.2f}s exceeds SLA",
                    {"performance_sla": perf_sla},
                )
            )

        return alerts

    def check_risk_alerts(self, positions: List[Dict[str, Any]], risk_limits: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check if risk alerts should be triggered"""
        alerts = []

        # Max positions
        max_positions = risk_limits.get("max_positions", 5)
        if len(positions) >= max_positions:
            alerts.append(
                self.create_alert(
                    AlertType.RISK_ALERT,
                    AlertSeverity.WARNING,
                    "Max Positions Reached",
                    f"Current positions: {len(positions)}/{max_positions}",
                    {"positions_count": len(positions), "max_positions": max_positions},
                )
            )

        # Total exposure
        total_exposure = sum((p.get("entry_price", 0) * p.get("qty", 0)) for p in positions)
        max_exposure = risk_limits.get("max_exposure", 100000)
        if total_exposure > max_exposure:
            alerts.append(
                self.create_alert(
                    AlertType.RISK_ALERT,
                    AlertSeverity.ERROR,
                    "Exposure Limit Exceeded",
                    f"Total exposure: ₹{total_exposure:.2f} exceeds limit ₹{max_exposure:.2f}",
                    {"total_exposure": total_exposure, "max_exposure": max_exposure},
                )
            )

        # Large loss
        total_pnl = sum(p.get("unrealized_pnl", 0) for p in positions)
        max_loss = risk_limits.get("max_loss", -5000)
        if total_pnl < max_loss:
            alerts.append(
                self.create_alert(
                    AlertType.RISK_ALERT,
                    AlertSeverity.CRITICAL,
                    "Large Loss Detected",
                    f"Total PnL: ₹{total_pnl:.2f} below limit ₹{max_loss:.2f}",
                    {"total_pnl": total_pnl, "max_loss": max_loss},
                )
            )

        return alerts

    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        alerts = []

        if not self.alerts_file.exists():
            return alerts

        try:
            with open(self.alerts_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    line = line.strip()
                    if line:
                        try:
                            alerts.append(json.loads(line))
                        except:
                            pass
        except Exception as e:
            print(f"Error reading alerts: {e}")

        return alerts

    def mark_alert_read(self, alert_id: str) -> bool:
        """Mark an alert as read. Was a no-op stub that always returned
        True regardless of whether alert_id existed - UI 'mark read'
        actions had zero effect. alerts.jsonl is append-only and small
        at this scale (not a high-volume event stream), so rewriting it
        is cheap; atomic write-temp-then-rename avoids corrupting it on
        a crash mid-write, same pattern as runtime_state_store."""
        if not self.alerts_file.exists():
            return False
        found = False
        lines_out = []
        with open(self.alerts_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    alert = json.loads(line)
                except json.JSONDecodeError:
                    lines_out.append(line)
                    continue
                if alert.get("id") == alert_id:
                    alert["read"] = True
                    found = True
                lines_out.append(json.dumps(alert, default=str))
        if not found:
            return False
        tmp_path = self.alerts_file.with_suffix(self.alerts_file.suffix + f".tmp{os.getpid()}")
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines_out) + "\n")
        os.replace(tmp_path, self.alerts_file)
        return True

    def _notify_subscribers(self, alert: Dict[str, Any]):
        """Notify all subscribers about new alert"""
        for subscriber in self.subscribers:
            try:
                subscriber(alert)
            except:
                pass

    def subscribe(self, callback):
        """Subscribe to alerts"""
        self.subscribers.append(callback)


# Global instance
_alerts_system = AlertsSystem()


def get_alerts_system() -> AlertsSystem:
    """Get global alerts system instance"""
    return _alerts_system
