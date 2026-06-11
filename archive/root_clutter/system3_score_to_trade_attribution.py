"""
System3 Phase 244 - Score-to-Trade Attribution Report
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
VIRTUAL_ORDERS_CSV = STORAGE_LIVE / "angel_virtual_orders_with_pnl.csv"
SIGNALS_CSV = STORAGE_LIVE / "angel_index_ai_signals.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_score_to_trade_attribution.md"


def run_phase244() -> dict:
    """Run Phase 244: Score-to-Trade Attribution."""
    if not VIRTUAL_ORDERS_CSV.exists() or not SIGNALS_CSV.exists():
        return {
            "phase": 244,
            "status": "WARN",
            "details": "Input files not found",
            "outputs": {},
            "errors": []
        }
    
    try:
        orders_df = pd.read_csv(VIRTUAL_ORDERS_CSV, engine="python", on_bad_lines="skip")
        signals_df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")
        
        # Join on keys
        join_keys = ["ts", "underlying", "strike", "side", "option_type", "expiry"]
        available_keys = [k for k in join_keys if k in orders_df.columns and k in signals_df.columns]
        
        if not available_keys:
            return {
                "phase": 244,
                "status": "WARN",
                "details": "No matching keys",
                "outputs": {},
                "errors": []
            }
        
        merged = orders_df.merge(signals_df, on=available_keys, how="left")
        
        # Score components
        score_cols = ["final_score", "ai_score", "greeks_score", "trend_score", "volatility_score", "momentum_score", "breakout_score"]
        available_score_cols = [c for c in score_cols if c in merged.columns]
        
        # Find PnL column
        pnl_col = [c for c in merged.columns if "pnl" in c.lower()][0] if any("pnl" in c.lower() for c in merged.columns) else None
        
        # Generate report
        report_lines = [
            "# System3 Score-to-Trade Attribution Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Total Trades**: {len(merged)}\n",
            "\n## Score Component Averages\n",
            "| Component | Average Value |\n",
            "|-----------|---------------|\n"
        ]
        
        for col in available_score_cols:
            avg_val = merged[col].mean()
            report_lines.append(f"| {col} | {avg_val:.4f} |\n")
        
        if pnl_col:
            report_lines.append(f"\n## Correlation with PnL\n")
            for col in available_score_cols:
                corr = merged[col].corr(merged[pnl_col])
                report_lines.append(f"- {col}: {corr:.3f}\n")
        
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)
        
        return {
            "phase": 244,
            "status": "OK",
            "details": f"Attribution report generated: {len(available_score_cols)} components",
            "outputs": {
                "components_analyzed": len(available_score_cols),
                "report_file": str(REPORT_PATH)
            },
            "errors": []
        }
        
    except Exception as e:
        return {
            "phase": 244,
            "status": "ERROR",
            "details": f"Error: {e}",
            "outputs": {},
            "errors": [str(e)]
        }


if __name__ == "__main__":
    result = run_phase244()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")

