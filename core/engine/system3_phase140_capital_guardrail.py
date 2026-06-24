"""
System3 Phase 140 - Capital Guard & One-Lot Guardrail

Computes capital guardrails for 1-lot-only test mode.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

LOT_MARGIN_CSV_PATH = STORAGE_ULTRA / "phase139_lot_margin.csv"
OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase140_capital_guardrail.csv"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase140_capital_guardrail.md"


def run_phase140_capital_guardrail(total_test_capital: float = 50000.0) -> Dict[str, Any]:
    """
    Compute capital guardrails for 1-lot-only test mode.

    Args:
        total_test_capital: Total test capital in INR (default 50k)

    Returns:
        dict: {
            "phase": 140,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load lot/margin data
        lot_margin_data = []
        if LOT_MARGIN_CSV_PATH.exists():
            try:
                df_lot_margin = pd.read_csv(LOT_MARGIN_CSV_PATH)
                lot_margin_data = df_lot_margin.to_dict(orient="records")
            except Exception as e:
                errors.append(f"Error reading lot/margin CSV: {e}")
        else:
            # Fallback to defaults
            lot_margin_data = [
                {"underlying": "NIFTY", "est_margin_per_lot": 50000},
                {"underlying": "BANKNIFTY", "est_margin_per_lot": 60000},
                {"underlying": "FINNIFTY", "est_margin_per_lot": 40000},
                {"underlying": "MIDCPNIFTY", "est_margin_per_lot": 35000},
                {"underlying": "SENSEX", "est_margin_per_lot": 45000},
            ]

        # Compute guardrails
        guardrail_rows = []
        allowed_underlyings = []

        for row in lot_margin_data:
            underlying = row["underlying"]
            est_margin = row.get("est_margin_per_lot", 50000)

            # Check if 1 lot fits
            capital_usage_percent = (est_margin / total_test_capital) * 100

            # Enforce 1-lot-only: max_lots_allowed is 0 or 1
            if capital_usage_percent <= 80.0:  # Allow up to 80% usage for safety
                max_lots_allowed = 1
                allowed_underlyings.append(underlying)
            else:
                max_lots_allowed = 0

            guardrail_rows.append(
                {
                    "underlying": underlying,
                    "est_margin_per_lot": est_margin,
                    "total_test_capital": total_test_capital,
                    "capital_usage_percent": round(capital_usage_percent, 2),
                    "max_lots_allowed": max_lots_allowed,
                }
            )

        # Create dataframe
        df = pd.DataFrame(guardrail_rows)

        # Save CSV
        df.to_csv(OUTPUT_CSV_PATH, index=False)

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Capital Guardrail Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Capital Configuration\n\n")
            f.write(f"- **Total Test Capital**: ₹{total_test_capital:,.2f}\n")
            f.write(f"- **Mode**: ONE-LOT ONLY TEST MODE ACTIVE ✅\n\n")

            f.write("## Per-Underlying Guardrails\n\n")
            f.write("| Underlying | Est Margin/Lot | Capital Usage % | Max Lots Allowed |\n")
            f.write("|------------|----------------|-----------------|------------------|\n")
            for row in guardrail_rows:
                f.write(
                    f"| {row['underlying']} | ₹{row['est_margin_per_lot']:,.0f} | {row['capital_usage_percent']:.2f}% | {row['max_lots_allowed']} |\n"
                )

            f.write("\n## Allowed Underlyings for 1-Lot Test\n\n")
            if allowed_underlyings:
                f.write("**ONE-LOT ONLY TEST MODE ACTIVE**\n\n")
                f.write("The following underlyings are allowed for 1-lot testing:\n\n")
                for underlying in allowed_underlyings:
                    f.write(f"- ✅ {underlying}\n")
            else:
                f.write("⚠️ **No underlyings fit within test capital for 1-lot testing.**\n")
                f.write("Consider increasing test capital or reducing margin estimates.\n")

        status = "OK" if not errors else "ERROR"
        details = f"Capital guardrails computed: {len(allowed_underlyings)} underlyings allowed for 1-lot test"

        return {
            "phase": 140,
            "status": status,
            "details": details,
            "outputs": {
                "csv_path": str(OUTPUT_CSV_PATH),
                "md_path": str(OUTPUT_MD_PATH),
                "allowed_underlyings": allowed_underlyings,
                "total_test_capital": total_test_capital,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 140,
            "status": "ERROR",
            "details": f"Phase 140 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="System3 Phase 140 - Capital Guard & One-Lot Guardrail")
    parser.add_argument("--total-test-capital", type=float, default=50000.0, help="Total test capital in INR")
    args = parser.parse_args()

    print("=" * 70)
    print("SYSTEM3 PHASE 140 - CAPITAL GUARD & ONE-LOT GUARDRAIL")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase140_capital_guardrail(total_test_capital=args.total_test_capital)

    print(f"Phase140: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nAllowed Underlyings: {len(result['outputs']['allowed_underlyings'])}")
        for underlying in result["outputs"]["allowed_underlyings"]:
            print(f"  ✅ {underlying}")
        print(f"\nCSV: {result['outputs']['csv_path']}")
        print(f"MD: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
