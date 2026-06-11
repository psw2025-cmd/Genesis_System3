"""
System3 Phase 245 - Symbol Participation Summary
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
INPUT_CSV = STORAGE_LIVE / "angel_virtual_orders.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_symbol_participation_summary.md"


def run_phase245() -> dict:
    """Run Phase 245: Symbol Participation Summary."""
    if not INPUT_CSV.exists():
        return {
            "phase": 245,
            "status": "WARN",
            "details": "Input file not found",
            "outputs": {},
            "errors": []
        }
    
    try:
        df = pd.read_csv(INPUT_CSV, engine="python", on_bad_lines="skip")
        
        if df.empty:
            return {
                "phase": 245,
                "status": "WARN",
                "details": "File is empty",
                "outputs": {},
                "errors": []
            }
        
        # Per-underlying summary
        summary_lines = [
            "# System3 Symbol Participation Summary\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Per-Underlying Summary\n",
            "| Underlying | Total Trades | BUY | SELL |\n",
            "|------------|--------------|-----|------|\n"
        ]
        
        if "underlying" in df.columns:
            for underlying, group in df.groupby("underlying"):
                total = len(group)
                buy_count = len(group[group["side"] == "BUY"]) if "side" in group.columns else 0
                sell_count = len(group[group["side"] == "SELL"]) if "side" in group.columns else 0
                summary_lines.append(f"| {underlying} | {total} | {buy_count} | {sell_count} |\n")
        
        # Per-expiry summary
        if "expiry" in df.columns:
            summary_lines.extend([
                "\n## Per-Expiry Summary\n",
                "| Expiry | Total Trades |\n",
                "|--------|--------------|\n"
            ])
            for expiry, group in df.groupby("expiry"):
                summary_lines.append(f"| {expiry} | {len(group)} |\n")
        
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(summary_lines)
        
        return {
            "phase": 245,
            "status": "OK",
            "details": f"Participation summary generated: {len(df)} trades",
            "outputs": {
                "total_trades": len(df),
                "report_file": str(REPORT_PATH)
            },
            "errors": []
        }
        
    except Exception as e:
        return {
            "phase": 245,
            "status": "ERROR",
            "details": f"Error: {e}",
            "outputs": {},
            "errors": [str(e)]
        }


if __name__ == "__main__":
    result = run_phase245()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")

