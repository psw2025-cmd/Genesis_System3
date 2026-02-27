"""
System3 Phase 275 - Position Sizing Optimizer (UPGRADED)

Optimizes position sizes based on risk and confidence.

UPGRADES (World-Class AI Trading System):
- Kelly Criterion integration (from advanced_position_sizing.py)
- Confidence-based scaling
- Volatility adjustment
- Dynamic risk calculation
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)
POSITION_SIZING_JSON = STORAGE_META / "system3_position_sizing.json"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_position_sizing_optimizer.md"


def calculate_kelly_criterion(win_rate: float, avg_win_pct: float, avg_loss_pct: float) -> float:
    """
    Calculate Kelly Criterion optimal bet size.

    Formula: f = (p * W - q * L) / W
    Where:
        p = win rate
        q = 1 - p (loss rate)
        W = average win percentage
        L = average loss percentage

    Args:
        win_rate: Win rate (0-1)
        avg_win_pct: Average win as percentage (e.g., 0.50 for 50%)
        avg_loss_pct: Average loss as percentage (e.g., 0.30 for 30%)

    Returns:
        Kelly fraction (0-1)
    """
    if avg_win_pct <= 0:
        return 0.0

    p = win_rate
    q = 1 - p
    W = avg_win_pct
    L = avg_loss_pct

    kelly = (p * W - q * L) / W

    # Ensure non-negative and cap at 1.0
    kelly = max(0.0, min(1.0, kelly))

    return kelly


def calculate_optimal_position_size(
    entry_price: float,
    stop_loss_price: float,
    confidence: float,
    iv: float,
    capital: float = 100000.0,
    win_rate: Optional[float] = None,
    avg_win_pct: Optional[float] = None,
    avg_loss_pct: Optional[float] = None,
    atr: Optional[float] = None,
    spot: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate optimal position size using Kelly Criterion and multiple methods.

    Args:
        entry_price: Entry price
        stop_loss_price: Stop loss price
        confidence: Model confidence (0-1)
        iv: Implied volatility
        capital: Trading capital
        win_rate: Historical win rate (optional)
        avg_win_pct: Average win percentage (optional)
        avg_loss_pct: Average loss percentage (optional)
        atr: Average True Range (optional)
        spot: Spot price (optional)

    Returns:
        Dict with position size details
    """
    # Default performance stats (can be updated from historical data)
    win_rate = win_rate or 0.667  # 66.7% default
    avg_win_pct = avg_win_pct or 0.50  # 50% default
    avg_loss_pct = avg_loss_pct or 0.30  # 30% default

    # Method 1: Kelly Criterion
    kelly_fraction = calculate_kelly_criterion(win_rate, avg_win_pct, avg_loss_pct)
    kelly_size = int(capital * kelly_fraction * 0.5 / entry_price)  # Use 50% of Kelly (fractional Kelly)
    kelly_size = max(1, kelly_size)

    # Method 2: Risk-based (2% risk per trade)
    risk_per_unit = abs(entry_price - stop_loss_price)
    if risk_per_unit > 0:
        risk_amount = capital * 0.02  # 2% risk
        risk_size = int(risk_amount / risk_per_unit)
        risk_size = max(1, risk_size)
    else:
        risk_size = 1

    # Method 3: Confidence adjustment
    confidence_mult = 0.5 + (confidence * 0.5)  # 0.5 to 1.0

    # Method 4: Volatility adjustment
    vol_mult = 1.0
    if iv > 0.30:  # High IV
        vol_mult = 0.8
    elif iv < 0.15:  # Low IV
        vol_mult = 1.1

    # Combine: Use minimum of Kelly and Risk-based, then apply adjustments
    base_size = min(kelly_size, risk_size)
    adjusted_size = int(base_size * confidence_mult * vol_mult)
    adjusted_size = max(1, min(3, adjusted_size))  # Cap at 3 lots

    # Calculate actual risk
    actual_risk = adjusted_size * risk_per_unit if risk_per_unit > 0 else 0
    actual_risk_pct = (actual_risk / capital) * 100.0 if capital > 0 else 0

    return {
        "quantity": adjusted_size,
        "kelly_size": kelly_size,
        "risk_size": risk_size,
        "kelly_fraction": kelly_fraction,
        "confidence_multiplier": confidence_mult,
        "volatility_multiplier": vol_mult,
        "actual_risk": float(actual_risk),
        "actual_risk_pct": float(actual_risk_pct),
        "method": "kelly_risk_confidence_volatility",
        "win_rate": win_rate,
        "avg_win_pct": avg_win_pct,
        "avg_loss_pct": avg_loss_pct,
    }


def run_phase275(**kwargs) -> Dict[str, Any]:
    """Run Phase 275: Position Sizing Optimizer (UPGRADED with Kelly Criterion)."""
    errors = []

    try:
        # Define position sizing rules (enhanced with Kelly Criterion)
        sizing_rules = {
            "base_lot_size": 1,
            "max_lot_size": 3,
            "confidence_multipliers": {
                "high": 1.5,
                "medium": 1.0,
                "low": 0.5,
            },
            "risk_adjustment": True,
            "kelly_criterion_enabled": True,
            "kelly_fraction": 0.5,  # Use 50% of Kelly (fractional Kelly for safety)
            "default_win_rate": 0.667,
            "default_avg_win_pct": 0.50,
            "default_avg_loss_pct": 0.30,
            "volatility_adjustment": True,
            "generated": datetime.now().isoformat(),
        }

        # Save position sizing config
        with POSITION_SIZING_JSON.open("w", encoding="utf-8") as f:
            json.dump(sizing_rules, f, indent=2)

        # Generate report
        report_lines = [
            "# System3 Position Sizing Optimizer\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Base Lot Size**: {sizing_rules['base_lot_size']}\n",
            f"**Max Lot Size**: {sizing_rules['max_lot_size']}\n",
            "\n## Confidence Multipliers\n",
            "| Confidence | Multiplier |\n",
            "|------------|------------|\n",
        ]

        for conf, mult in sizing_rules["confidence_multipliers"].items():
            report_lines.append(f"| {conf} | {mult:.2f} |\n")

        # Add Kelly Criterion info to report
        report_lines.extend(
            [
                "\n## Kelly Criterion\n",
                f"**Enabled**: {sizing_rules['kelly_criterion_enabled']}\n",
                f"**Kelly Fraction**: {sizing_rules['kelly_fraction']}\n",
                f"**Default Win Rate**: {sizing_rules['default_win_rate']:.1%}\n",
                f"**Default Avg Win**: {sizing_rules['default_avg_win_pct']:.1%}\n",
                f"**Default Avg Loss**: {sizing_rules['default_avg_loss_pct']:.1%}\n",
                "\n## Volatility Adjustment\n",
                f"**Enabled**: {sizing_rules['volatility_adjustment']}\n",
                "- High IV (>30%): Reduce size by 20%\n",
                "- Low IV (<15%): Increase size by 10%\n",
            ]
        )

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        # Test Kelly Criterion calculation
        test_kelly = calculate_kelly_criterion(
            sizing_rules["default_win_rate"], sizing_rules["default_avg_win_pct"], sizing_rules["default_avg_loss_pct"]
        )

        status = "OK"
        details = (
            f"Optimized position sizing: base={sizing_rules['base_lot_size']}, "
            f"max={sizing_rules['max_lot_size']}, "
            f"Kelly={test_kelly:.3f} (fractional: {sizing_rules['kelly_fraction']})"
        )

        return {
            "phase": 275,
            "status": status,
            "details": details,
            "outputs": {
                "base_lot_size": sizing_rules["base_lot_size"],
                "max_lot_size": sizing_rules["max_lot_size"],
                "kelly_criterion_enabled": sizing_rules["kelly_criterion_enabled"],
                "kelly_fraction": test_kelly,
                "sizing_file": str(POSITION_SIZING_JSON),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 275,
            "status": "ERROR",
            "details": f"Phase 275 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase275()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
