"""
System3 Phase 276 - Risk-Reward Optimizer

Optimizes risk-reward ratios for trades.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
ENRICHED_ORDERS_CSV = STORAGE_LIVE / "angel_virtual_orders_with_pnl.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_risk_reward_optimizer.md"


def run_phase276(**kwargs) -> Dict[str, Any]:
    """Run Phase 276: Risk-Reward Optimizer."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 276,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"avg_risk_reward": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 276,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"avg_risk_reward": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 276,
                "status": "WARN",
                "details": "No data to analyze",
                "outputs": {"avg_risk_reward": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate risk-reward ratios
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 276,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"avg_risk_reward": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]

        # Simple risk-reward: average win / average loss
        wins = df[df[pnl_col] > 0][pnl_col]
        losses = df[df[pnl_col] < 0][pnl_col]

        avg_win = wins.mean() if len(wins) > 0 else 0.0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0.0
        risk_reward_ratio = (avg_win / avg_loss) if avg_loss > 0 else 0.0

        # Generate report
        report_lines = [
            "# System3 Risk-Reward Optimizer\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Average Win**: {avg_win:.2f}\n",
            f"**Average Loss**: {avg_loss:.2f}\n",
            f"**Risk-Reward Ratio**: {risk_reward_ratio:.2f}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Risk-reward ratio: {risk_reward_ratio:.2f}"

        return {
            "phase": 276,
            "status": status,
            "details": details,
            "outputs": {
                "avg_risk_reward": float(risk_reward_ratio),
                "avg_win": float(avg_win),
                "avg_loss": float(avg_loss),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 276,
            "status": "ERROR",
            "details": f"Phase 276 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase276()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
