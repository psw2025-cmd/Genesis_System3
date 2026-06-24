"""
System3 Phase 86 - Position Sizing Engine

Define per-trade position size based on risk rules (max capital % per trade,
volatility, underlying risk).
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"

# Output files
OUTPUT_JSON = STORAGE_ULTRA / "phase86_position_sizing_rules.json"
OUTPUT_MD = STORAGE_ULTRA / "phase86_position_sizing_examples.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

# Risk config
MAX_RISK_PER_TRADE_PCT = 1.0  # 1% of capital per trade
MAX_OPEN_RISK_PCT = 5.0  # 5% total open risk
PORTFOLIO_CAPITAL = 100000  # 1,00,000


def calculate_position_size(capital: float, risk_pct: float, entry_price: float, stop_loss_pct: float) -> int:
    """Calculate position size based on risk."""
    risk_amount = capital * (risk_pct / 100.0)
    risk_per_unit = entry_price * (stop_loss_pct / 100.0)

    if risk_per_unit <= 0:
        return 0

    quantity = int(risk_amount / risk_per_unit)
    return max(1, quantity)  # At least 1


def generate_position_sizing() -> Dict[str, Any]:
    """Generate position sizing rules and examples."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 86 - POSITION SIZING ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Base rules
    base_rules = {
        "max_risk_per_trade_pct": MAX_RISK_PER_TRADE_PCT,
        "max_open_risk_pct": MAX_OPEN_RISK_PCT,
        "portfolio_capital": PORTFOLIO_CAPITAL,
    }

    # Example scenarios
    examples = []
    underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY"]

    for underlying in underlyings:
        # Example 1: CE option
        entry_price_ce = 500.0
        stop_loss_pct = 5.0  # 5% stop loss
        quantity_ce = calculate_position_size(PORTFOLIO_CAPITAL, MAX_RISK_PER_TRADE_PCT, entry_price_ce, stop_loss_pct)
        examples.append(
            {
                "underlying": underlying,
                "option_type": "CE",
                "entry_price": entry_price_ce,
                "stop_loss_pct": stop_loss_pct,
                "capital": PORTFOLIO_CAPITAL,
                "risk_pct": MAX_RISK_PER_TRADE_PCT,
                "recommended_quantity": quantity_ce,
            }
        )

        # Example 2: PE option
        entry_price_pe = 300.0
        quantity_pe = calculate_position_size(PORTFOLIO_CAPITAL, MAX_RISK_PER_TRADE_PCT, entry_price_pe, stop_loss_pct)
        examples.append(
            {
                "underlying": underlying,
                "option_type": "PE",
                "entry_price": entry_price_pe,
                "stop_loss_pct": stop_loss_pct,
                "capital": PORTFOLIO_CAPITAL,
                "risk_pct": MAX_RISK_PER_TRADE_PCT,
                "recommended_quantity": quantity_pe,
            }
        )

    report = {
        "timestamp": datetime.now().isoformat(),
        "base_rules": base_rules,
        "examples": examples,
    }

    # Save JSON
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[PH86] Position sizing rules computed for {len(examples)} scenarios")

    # Generate MD
    generate_markdown(report)
    print(f"[PH86] Examples written to {OUTPUT_MD}")

    return report


def generate_markdown(report: Dict[str, Any]) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 86 - Position Sizing Examples\n\n")
        f.write(f"**Date**: {report['timestamp']}\n\n")

        f.write("## Example Cases\n\n")
        f.write("| Underlying | Option | Entry Price | Capital | Risk % | Recommended Qty |\n")
        f.write("|------------|--------|-------------|---------|-------|------------------|\n")

        for ex in report["examples"]:
            f.write(
                f"| {ex['underlying']} | {ex['option_type']} | {ex['entry_price']:.2f} | "
                f"{ex['capital']:,} | {ex['risk_pct']}% | {ex['recommended_quantity']} |\n"
            )


def main():
    """Main entry point."""
    try:
        report = generate_position_sizing()
        print("\n[PH86] Position sizing generation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH86] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
