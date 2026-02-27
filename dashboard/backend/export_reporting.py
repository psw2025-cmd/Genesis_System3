"""
Export & Reporting System
"""

import json
import csv
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import pytz

IST = pytz.timezone("Asia/Kolkata")


class ExportReporting:
    """
    Export and reporting system
    """

    def export_positions_to_csv(self, positions: List[Dict[str, Any]], output_file: Path) -> bool:
        """Export positions to CSV"""
        try:
            if not positions:
                return False

            with open(output_file, "w", newline="", encoding="utf-8") as f:
                fieldnames = [
                    "position_id",
                    "symbol",
                    "underlying",
                    "option_type",
                    "strike",
                    "expiry",
                    "qty",
                    "entry_price",
                    "current_price",
                    "unrealized_pnl",
                    "entry_time",
                    "status",
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for pos in positions:
                    row = {
                        "position_id": pos.get("position_id", ""),
                        "symbol": pos.get("symbol", ""),
                        "underlying": pos.get("underlying", ""),
                        "option_type": pos.get("option_type", ""),
                        "strike": pos.get("strike", 0),
                        "expiry": pos.get("expiry", ""),
                        "qty": pos.get("qty", 0),
                        "entry_price": pos.get("entry_price", 0),
                        "current_price": pos.get("current_price", 0),
                        "unrealized_pnl": pos.get("unrealized_pnl", 0),
                        "entry_time": pos.get("entry_time", ""),
                        "status": pos.get("status", "OPEN"),
                    }
                    writer.writerow(row)

            return True
        except Exception as e:
            print(f"Error exporting positions: {e}")
            return False

    def export_pnl_to_csv(self, pnl_data: Dict[str, Any], output_file: Path) -> bool:
        """Export PnL data to CSV"""
        try:
            history = pnl_data.get("history", [])
            summary = pnl_data.get("summary", {})

            with open(output_file, "w", newline="", encoding="utf-8") as f:
                # Write summary first
                f.write("# PnL Summary\n")
                f.write(f"Total Trades: {summary.get('total_trades', 0)}\n")
                f.write(f"Winning Trades: {summary.get('winning_trades', 0)}\n")
                f.write(f"Losing Trades: {summary.get('losing_trades', 0)}\n")
                f.write(f"Win Rate: {summary.get('win_rate', 0):.2f}%\n")
                f.write(f"Total Realized PnL: {summary.get('total_realized_pnl', 0):.2f}\n")
                f.write(f"Total Unrealized PnL: {summary.get('total_unrealized_pnl', 0):.2f}\n")
                f.write(f"Total PnL: {summary.get('total_pnl', 0):.2f}\n")
                f.write("\n# PnL History\n")

                # Write history
                if history:
                    fieldnames = list(history[0].keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(history)

            return True
        except Exception as e:
            print(f"Error exporting PnL: {e}")
            return False

    def generate_performance_report(
        self,
        health_data: Dict[str, Any],
        positions: List[Dict[str, Any]],
        pnl_data: Dict[str, Any],
        performance_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            "report_id": f"REPORT_{datetime.now(IST).strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now(IST).isoformat(),
            "system_status": {
                "mode": health_data.get("mode", "UNKNOWN"),
                "broker_status": health_data.get("broker_status", "UNKNOWN"),
                "market_status": health_data.get("market_status", "UNKNOWN"),
                "data_source": health_data.get("data_source", "real"),
            },
            "trading_performance": {
                "total_trades": pnl_data.get("summary", {}).get("total_trades", 0),
                "win_rate": pnl_data.get("summary", {}).get("win_rate", 0),
                "total_pnl": pnl_data.get("summary", {}).get("total_pnl", 0),
                "open_positions": len(positions),
            },
            "positions": positions,
            "pnl_summary": pnl_data.get("summary", {}),
            "performance_metrics": performance_data.get("current", {}),
        }

        return report

    def export_report_to_json(self, report: Dict[str, Any], output_file: Path) -> bool:
        """Export report to JSON"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False


# Global instance
_export_reporting = ExportReporting()


def get_export_reporting() -> ExportReporting:
    """Get global export reporting instance"""
    return _export_reporting
