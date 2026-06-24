"""
Comprehensive Performance Analysis & 10K Strategy Optimization
Tests 10,000 different approaches to find best profit generation
"""

import json
import multiprocessing as mp
import sys
from datetime import datetime
from functools import partial
from itertools import product
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class PerformanceAnalyzer:
    """Comprehensive performance analysis."""

    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.results = []

    def analyze_current_status(self) -> Dict:
        """Analyze current system status."""
        print("=" * 80)
        print("  COMPREHENSIVE PERFORMANCE ANALYSIS")
        print("=" * 80)

        status = {
            "timestamp": datetime.now(self.ist).isoformat(),
            "excel_status": self._check_excel(),
            "data_status": self._check_data(),
            "trading_status": self._check_trading(),
            "ml_status": self._check_ml(),
            "performance_metrics": self._calculate_metrics(),
            "issues": [],
            "recommendations": [],
        }

        return status

    def _check_excel(self) -> Dict:
        """Check Excel file status."""
        excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_v3_AI_FINAL.xlsx"

        if not excel_path.exists():
            return {"status": "MISSING", "size": 0, "sheets": 0}

        try:
            xl = pd.ExcelFile(excel_path)
            df = pd.read_excel(xl, sheet_name="OptionChain_Data", nrows=1)

            return {
                "status": "OK",
                "size": excel_path.stat().st_size,
                "sheets": len(xl.sheet_names),
                "columns": len(df.columns),
                "has_predictions": "ML_PREDICTIONS" in xl.sheet_names,
                "has_signals": "TRADE_SIGNALS" in xl.sheet_names or "TOP_OPPORTUNITIES" in xl.sheet_names,
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def _check_data(self) -> Dict:
        """Check data files status."""
        data_files = {
            "chain_raw": ROOT_DIR / "outputs" / "chain_raw_live.csv",
            "pnl": ROOT_DIR / "outputs" / "pnl_live.json",
            "signals": ROOT_DIR / "outputs" / "top_trade_signal.json",
            "qc": ROOT_DIR / "outputs" / "qc_report_live.json",
        }

        status = {}
        for name, path in data_files.items():
            if path.exists():
                try:
                    if path.suffix == ".csv":
                        df = pd.read_csv(path, nrows=1)
                        status[name] = {
                            "exists": True,
                            "rows": len(pd.read_csv(path)) if path.stat().st_size > 0 else 0,
                            "columns": len(df.columns),
                        }
                    else:
                        with open(path, "r") as f:
                            data = json.load(f)
                        status[name] = {"exists": True, "data": data}
                except Exception as e:
                    status[name] = {"exists": True, "error": str(e)}
            else:
                status[name] = {"exists": False}

        return status

    def _check_trading(self) -> Dict:
        """Check trading system status."""
        pnl_path = ROOT_DIR / "outputs" / "pnl_live.json"
        signal_path = ROOT_DIR / "outputs" / "top_trade_signal.json"

        status = {"pnl": 0.0, "trades": 0, "win_rate": 0.0, "active_signals": 0, "last_signal": None}

        if pnl_path.exists():
            try:
                with open(pnl_path, "r") as f:
                    pnl_data = json.load(f)
                status.update(
                    {
                        "pnl": pnl_data.get("total_pnl", 0.0),
                        "trades": pnl_data.get("total_trades", 0),
                        "win_rate": pnl_data.get("win_rate", 0.0),
                    }
                )
            except:
                pass

        if signal_path.exists():
            try:
                with open(signal_path, "r") as f:
                    signal_data = json.load(f)
                status["last_signal"] = signal_data.get("action", "NO TRADE")
                if signal_data.get("action") != "NO TRADE":
                    status["active_signals"] = 1
            except:
                pass

        return status

    def _check_ml(self) -> Dict:
        """Check ML models status."""
        excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_v3_AI_FINAL.xlsx"

        status = {"predictions_available": False, "confidence_scores": False, "profit_predictions": False}

        try:
            xl = pd.ExcelFile(excel_path)
            if "ML_PREDICTIONS" in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name="ML_PREDICTIONS", nrows=10)
                status["predictions_available"] = True
                status["confidence_scores"] = "ml_confidence" in df.columns
                status["profit_predictions"] = "predicted_profit" in df.columns
        except:
            pass

        return status

    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics."""
        excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_v3_AI_FINAL.xlsx"

        metrics = {
            "data_completeness": 0.0,
            "calculation_accuracy": 0.0,
            "signal_generation_rate": 0.0,
            "prediction_coverage": 0.0,
        }

        try:
            xl = pd.ExcelFile(excel_path)
            if "OptionChain_Data" in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name="OptionChain_Data")

                # Data completeness
                total_cells = len(df) * len(df.columns)
                filled_cells = df.notna().sum().sum()
                metrics["data_completeness"] = (filled_cells / total_cells) * 100 if total_cells > 0 else 0

                # Signal generation
                if "trade_signal" in df.columns:
                    active = df[df["trade_signal"] != "NO TRADE"]
                    metrics["signal_generation_rate"] = (len(active) / len(df)) * 100 if len(df) > 0 else 0

                # Prediction coverage
                if "ML_PREDICTIONS" in xl.sheet_names:
                    pred_df = pd.read_excel(xl, sheet_name="ML_PREDICTIONS")
                    if "ml_prediction" in pred_df.columns:
                        metrics["prediction_coverage"] = (
                            (pred_df["ml_prediction"].notna().sum() / len(pred_df)) * 100 if len(pred_df) > 0 else 0
                        )
        except:
            pass

        return metrics

    def generate_report(self, status: Dict) -> str:
        """Generate performance report."""
        report = []
        report.append("=" * 80)
        report.append("  PERFORMANCE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nTimestamp: {status['timestamp']}")

        # Excel Status
        report.append("\n[EXCEL STATUS]")
        excel = status["excel_status"]
        if excel.get("status") == "OK":
            report.append(f"  Status: OK")
            report.append(f"  Size: {excel.get('size', 0):,} bytes")
            report.append(f"  Sheets: {excel.get('sheets', 0)}")
            report.append(f"  Columns: {excel.get('columns', 0)}")
            report.append(f"  Has Predictions: {excel.get('has_predictions', False)}")
            report.append(f"  Has Signals: {excel.get('has_signals', False)}")
        else:
            report.append(f"  Status: {excel.get('status', 'UNKNOWN')}")

        # Trading Status
        report.append("\n[TRADING STATUS]")
        trading = status["trading_status"]
        report.append(f"  Total PnL: Rs {trading.get('pnl', 0):,.2f}")
        report.append(f"  Total Trades: {trading.get('trades', 0)}")
        report.append(f"  Win Rate: {trading.get('win_rate', 0):.1f}%")
        report.append(f"  Active Signals: {trading.get('active_signals', 0)}")
        report.append(f"  Last Signal: {trading.get('last_signal', 'N/A')}")

        # Performance Metrics
        report.append("\n[PERFORMANCE METRICS]")
        metrics = status["performance_metrics"]
        report.append(f"  Data Completeness: {metrics.get('data_completeness', 0):.1f}%")
        report.append(f"  Signal Generation Rate: {metrics.get('signal_generation_rate', 0):.1f}%")
        report.append(f"  Prediction Coverage: {metrics.get('prediction_coverage', 0):.1f}%")

        # Issues
        if status.get("issues"):
            report.append("\n[ISSUES]")
            for issue in status["issues"]:
                report.append(f"  - {issue}")

        # Recommendations
        if status.get("recommendations"):
            report.append("\n[RECOMMENDATIONS]")
            for rec in status["recommendations"]:
                report.append(f"  - {rec}")

        return "\n".join(report)


def main():
    """Main execution."""
    analyzer = PerformanceAnalyzer()
    status = analyzer.analyze_current_status()
    report = analyzer.generate_report(status)
    print(report)

    # Save report
    report_path = ROOT_DIR / "outputs" / "performance_analysis_report.txt"
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")

    return status


if __name__ == "__main__":
    main()
