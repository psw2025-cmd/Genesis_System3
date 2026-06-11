"""
System3 Phase 241 - Virtual Trade Diagnostics & Sanity Checks
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
INPUT_CSV = STORAGE_LIVE / "angel_virtual_orders_with_pnl.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_virtual_trades_diagnostics.md"


def run_phase241() -> dict:
    """Run Phase 241: Virtual Trade Diagnostics."""
    if not INPUT_CSV.exists():
        return {
            "phase": 241,
            "status": "WARN",
            "details": "Input file not found",
            "outputs": {},
            "errors": []
        }
    
    try:
        df = pd.read_csv(INPUT_CSV, engine="python", on_bad_lines="skip")
        
        if df.empty:
            return {
                "phase": 241,
                "status": "WARN",
                "details": "File is empty",
                "outputs": {},
                "errors": []
            }
        
        anomalies = []
        
        # Check lots <= 0
        if "lots" in df.columns:
            invalid_lots = len(df[df["lots"] <= 0])
            if invalid_lots > 0:
                anomalies.append(f"{invalid_lots} trades with lots <= 0")
        
        # Check unknown underlyings
        valid_underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
        if "underlying" in df.columns:
            unknown = df[~df["underlying"].isin(valid_underlyings)]
            if len(unknown) > 0:
                anomalies.append(f"{len(unknown)} trades with unknown underlyings")
        
        # Check outliers (PnL > 3 std devs)
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        outlier_count = 0
        for col in pnl_cols:
            if col in df.columns:
                mean_pnl = df[col].mean()
                std_pnl = df[col].std()
                if std_pnl > 0:
                    outliers = df[abs(df[col] - mean_pnl) > 3 * std_pnl]
                    outlier_count += len(outliers)
        
        # Correlation check
        correlation = 0.0
        if "final_score" in df.columns and pnl_cols:
            pnl_col = pnl_cols[0]
            if pnl_col in df.columns:
                correlation = df["final_score"].corr(df[pnl_col])
        
        # Generate report
        report_lines = [
            "# System3 Virtual Trades Diagnostics\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Total Trades**: {len(df)}\n",
            "\n## Anomalies\n",
        ]
        
        if anomalies:
            for anomaly in anomalies:
                report_lines.append(f"- ⚠️ {anomaly}\n")
        else:
            report_lines.append("- ✅ No anomalies detected\n")
        
        report_lines.extend([
            f"\n## Statistics\n",
            f"- Outliers (>3 std devs): {outlier_count}\n",
            f"- Correlation (final_score vs PnL): {correlation:.3f}\n",
        ])
        
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)
        
        status = "ERROR" if anomalies else "OK"
        
        return {
            "phase": 241,
            "status": status,
            "details": f"Diagnostics complete: {len(anomalies)} anomalies, correlation={correlation:.3f}",
            "outputs": {
                "anomalies": len(anomalies),
                "correlation": correlation,
                "report_file": str(REPORT_PATH)
            },
            "errors": anomalies
        }
        
    except Exception as e:
        return {
            "phase": 241,
            "status": "ERROR",
            "details": f"Error: {e}",
            "outputs": {},
            "errors": [str(e)]
        }


if __name__ == "__main__":
    result = run_phase241()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")

