#!/usr/bin/env python3
"""
Forensic Analysis System
Comprehensive forensic analysis of trading data, signals, and outcomes
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

IST = pytz.timezone("Asia/Kolkata")


class ForensicAnalysisSystem:
    """Comprehensive forensic analysis"""

    def __init__(self):
        self.outputs_dir = ROOT_DIR / "outputs"
        self.storage_dir = ROOT_DIR / "storage"
        self.reports_dir = ROOT_DIR / "reports" / "forensic"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def analyze_signal_accuracy(self) -> Dict:
        """Analyze signal accuracy vs outcomes"""
        print("[Forensic] Analyzing signal accuracy...")

        # Load signals
        signal_file = self.outputs_dir / "top_trade_signal.json"
        paper_trades_file = ROOT_DIR / "src" / "outputs" / "paper_trades_live.csv"

        results = {
            "total_signals": 0,
            "signals_executed": 0,
            "profitable_executions": 0,
            "accuracy": 0.0,
            "signal_types": {},
        }

        if paper_trades_file.exists():
            try:
                df = pd.read_csv(paper_trades_file, on_bad_lines="skip", engine="python")
                results["total_signals"] = len(df[df["action"] == "OPEN"])
                results["signals_executed"] = len(df[df["action"] == "CLOSE"])

                if "realized_pnl" in df.columns:
                    closed_trades = df[df["action"] == "CLOSE"]
                    profitable = closed_trades[closed_trades["realized_pnl"] > 0]
                    results["profitable_executions"] = len(profitable)
                    if results["signals_executed"] > 0:
                        results["accuracy"] = results["profitable_executions"] / results["signals_executed"]

                # Analyze by strategy
                if "strategy" in df.columns:
                    strategy_analysis = (
                        df[df["action"] == "CLOSE"].groupby("strategy")["realized_pnl"].agg(["count", "sum", "mean"])
                    )
                    # Convert to JSON-serializable format
                    results["signal_types"] = {
                        str(strategy): {
                            "count": int(row["count"]),
                            "sum": float(row["sum"]),
                            "mean": float(row["mean"]),
                        }
                        for strategy, row in strategy_analysis.iterrows()
                    }

                print(f"[OK] Signal accuracy: {results['accuracy']:.2%}")
            except Exception as e:
                print(f"[ERROR] Signal analysis failed: {e}")

        return results

    def analyze_data_integrity(self) -> Dict:
        """Analyze data integrity across all sources"""
        print("[Forensic] Analyzing data integrity...")

        results = {"chain_data": {}, "signal_data": {}, "position_data": {}, "pnl_data": {}, "issues": []}

        # Check chain data
        chain_file = self.outputs_dir / "chain_raw_live.csv"
        if chain_file.exists():
            try:
                df = pd.read_csv(chain_file, on_bad_lines="skip", engine="python")
                results["chain_data"] = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "null_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                    "duplicates": df.duplicated().sum(),
                }

                if results["chain_data"]["null_percentage"] > 10:
                    results["issues"].append("Chain data has >10% null values")
            except Exception as e:
                results["issues"].append(f"Chain data analysis failed: {e}")

        # Check signal data
        signal_file = self.outputs_dir / "top_trade_signal.json"
        if signal_file.exists():
            try:
                with open(signal_file, "r") as f:
                    signal = json.load(f)
                results["signal_data"] = {
                    "has_action": "action" in signal,
                    "has_underlying": "underlying" in signal,
                    "timestamp": signal.get("timestamp", "N/A"),
                }
            except Exception as e:
                results["issues"].append(f"Signal data analysis failed: {e}")

        # Check position data
        positions_file = self.outputs_dir / "positions_live.json"
        if positions_file.exists():
            try:
                with open(positions_file, "r") as f:
                    positions = json.load(f)
                if isinstance(positions, dict):
                    pos_list = positions.get("positions", [])
                    results["position_data"] = {
                        "open_positions": len(pos_list),
                        "has_required_fields": all("entry_price" in p for p in pos_list) if pos_list else True,
                    }
            except Exception as e:
                results["issues"].append(f"Position data analysis failed: {e}")

        print(f"[OK] Data integrity analysis complete - {len(results['issues'])} issues found")

        return results

    def analyze_performance_metrics(self) -> Dict:
        """Analyze performance metrics"""
        print("[Forensic] Analyzing performance metrics...")

        results = {
            "total_trades": 0,
            "win_rate": 0.0,
            "total_pnl": 0.0,
            "avg_pnl_per_trade": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
        }

        paper_trades_file = ROOT_DIR / "src" / "outputs" / "paper_trades_live.csv"
        if paper_trades_file.exists():
            try:
                df = pd.read_csv(paper_trades_file, on_bad_lines="skip", engine="python")
                closed_trades = df[df["action"] == "CLOSE"]

                if not closed_trades.empty and "realized_pnl" in closed_trades.columns:
                    results["total_trades"] = len(closed_trades)
                    results["total_pnl"] = closed_trades["realized_pnl"].sum()
                    results["avg_pnl_per_trade"] = closed_trades["realized_pnl"].mean()

                    profitable = closed_trades[closed_trades["realized_pnl"] > 0]
                    results["win_rate"] = len(profitable) / len(closed_trades) if len(closed_trades) > 0 else 0

                    # Calculate drawdown
                    if "realized_pnl" in closed_trades.columns:
                        cumulative = closed_trades["realized_pnl"].cumsum()
                        running_max = cumulative.expanding().max()
                        drawdown = cumulative - running_max
                        results["max_drawdown"] = abs(drawdown.min()) if len(drawdown) > 0 else 0

                print(
                    f"[OK] Performance analysis: {results['total_trades']} trades, {results['win_rate']:.2%} win rate"
                )
            except Exception as e:
                print(f"[ERROR] Performance analysis failed: {e}")

        return results

    def generate_forensic_report(self):
        """Generate comprehensive forensic report"""
        print("\n[Forensic] Generating comprehensive forensic report...")

        report = {
            "timestamp": datetime.now(IST).isoformat(),
            "signal_accuracy": self.analyze_signal_accuracy(),
            "data_integrity": self.analyze_data_integrity(),
            "performance_metrics": self.analyze_performance_metrics(),
        }

        # Save report
        report_file = self.reports_dir / f"forensic_report_{datetime.now(IST).strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"[OK] Forensic report saved: {report_file}")

        # Print summary
        print("\n[Forensic Report Summary]")
        print(f"Signal Accuracy: {report['signal_accuracy'].get('accuracy', 0):.2%}")
        print(f"Data Issues: {len(report['data_integrity'].get('issues', []))}")
        print(f"Total Trades: {report['performance_metrics'].get('total_trades', 0)}")
        print(f"Win Rate: {report['performance_metrics'].get('win_rate', 0):.2%}")

        return report


if __name__ == "__main__":
    forensic = ForensicAnalysisSystem()
    forensic.generate_forensic_report()
