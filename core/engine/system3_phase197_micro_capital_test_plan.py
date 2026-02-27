"""
System3 Phase 197 - Micro Capital Test Plan MD

Builds a concrete 1-lot-only test plan.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

CAPITAL_GUARDRAIL_CSV = STORAGE_ULTRA / "phase140_capital_guardrail.csv"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase197_micro_capital_test_plan.md"


def run_phase197_micro_capital_test_plan() -> Dict[str, Any]:
    """
    Build 1-lot-only test plan.

    Returns:
        dict: {
            "phase": 197,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load capital guardrail
        allowed_underlyings = []
        max_trades_per_day = 10
        max_drawdown = 5000.0  # 10% of 50k test capital

        if CAPITAL_GUARDRAIL_CSV.exists():
            try:
                df = pd.read_csv(CAPITAL_GUARDRAIL_CSV)
                allowed_underlyings = df[df["max_lots_allowed"] > 0]["underlying"].tolist()
            except Exception as e:
                errors.append(f"Error reading capital guardrail: {e}")

        # Generate MD test plan
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Micro Capital Test Plan (1-Lot Only)\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Test Configuration\n\n")
            f.write(f"- **Mode**: 1-LOT ONLY TEST MODE\n")
            f.write(f"- **Max Trades/Day**: {max_trades_per_day}\n")
            f.write(f"- **Max Drawdown Stop**: ₹{max_drawdown:,.2f} (10% of test capital)\n\n")

            f.write("## Allowed Underlyings\n\n")
            if allowed_underlyings:
                for underlying in allowed_underlyings:
                    f.write(f"- ✅ {underlying}\n")
            else:
                f.write("- No underlyings currently allowed (check capital guardrail)\n")

            f.write("\n## Stop Conditions\n\n")
            f.write("1. **Max Drawdown**: Stop if cumulative loss exceeds ₹{max_drawdown:,.2f}\n")
            f.write("2. **Daily Trade Limit**: Stop if {max_trades_per_day} trades executed in one day\n")
            f.write("3. **Kill Switch**: Stop immediately if kill switch is activated\n")
            f.write("4. **Market Close**: Stop at market close (15:30 IST)\n")

        status = "OK" if not errors else "ERROR"
        details = f"Micro capital test plan: {len(allowed_underlyings)} underlyings allowed"

        return {
            "phase": 197,
            "status": status,
            "details": details,
            "outputs": {
                "md_path": str(OUTPUT_MD_PATH),
                "allowed_underlyings": allowed_underlyings,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 197,
            "status": "ERROR",
            "details": f"Phase 197 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 197 - MICRO CAPITAL TEST PLAN")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase197_micro_capital_test_plan()

    print(f"Phase197: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nAllowed Underlyings: {len(result['outputs']['allowed_underlyings'])}")
        print(f"Plan: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
