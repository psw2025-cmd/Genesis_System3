"""
System3 Phase 88 - Portfolio Risk Engine

Analyze exposures across underlyings and strikes to detect portfolio-level risk.
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"

# Input files
TRADES_PLAN_CSV = STORAGE_LIVE / "dhan_index_ai_trades_plan.csv"
PNL_LOG_CSV = STORAGE_LIVE / "dhan_index_ai_pnl_log.csv"

# Output files
OUTPUT_JSON = STORAGE_ULTRA / "phase88_portfolio_risk.json"
OUTPUT_MD = STORAGE_ULTRA / "phase88_portfolio_risk.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    """Load trade plan or PnL data."""
    # Prefer PnL if available, else trades plan
    if PNL_LOG_CSV.exists():
        try:
            return pd.read_csv(PNL_LOG_CSV)
        except Exception:
            pass

    if TRADES_PLAN_CSV.exists():
        try:
            return pd.read_csv(TRADES_PLAN_CSV)
        except Exception:
            pass

    return pd.DataFrame()


def calculate_notional(row: pd.Series) -> float:
    """Calculate notional value for a trade."""
    entry_price = row.get("entry_price", 0.0)
    # Assume quantity = 1 if not specified (would normally come from position sizing)
    quantity = row.get("quantity", 1)
    return entry_price * quantity * 50  # 50 is lot size for index options


def analyze_portfolio_risk() -> Dict[str, Any]:
    """Analyze portfolio-level risk."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 88 - PORTFOLIO RISK ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load data
    df = load_data()

    if df.empty:
        print("[PH88] No trade data found. Creating empty report.")
        return {
            "timestamp": datetime.now().isoformat(),
            "per_underlying_exposure": {},
            "ce_pe_bias": {},
            "max_strike_concentration": {},
            "risk_flags": [],
        }

    # Calculate notional exposures
    per_underlying = defaultdict(float)
    ce_count = defaultdict(int)
    pe_count = defaultdict(int)
    strike_exposures = defaultdict(float)

    for _, row in df.iterrows():
        underlying = row.get("underlying", "UNKNOWN")
        side = row.get("side", "")
        strike = row.get("strike", 0)
        notional = calculate_notional(row)

        per_underlying[underlying] += notional

        if side == "CE":
            ce_count[underlying] += 1
        elif side == "PE":
            pe_count[underlying] += 1

        strike_key = f"{underlying}_{strike}"
        strike_exposures[strike_key] += notional

    # Find max strike concentration
    max_strike = max(strike_exposures.items(), key=lambda x: x[1]) if strike_exposures else (None, 0.0)

    # Calculate CE vs PE bias
    ce_pe_bias = {}
    for underlying in set(list(ce_count.keys()) + list(pe_count.keys())):
        ce = ce_count[underlying]
        pe = pe_count[underlying]
        total = ce + pe
        if total > 0:
            ce_pe_bias[underlying] = {
                "ce_count": ce,
                "pe_count": pe,
                "net_bias": "CE" if ce > pe else "PE" if pe > ce else "NEUTRAL",
            }

    # Risk flags
    risk_flags = []
    max_exposure = max(per_underlying.values()) if per_underlying else 0.0
    if max_exposure > 100000:  # 1 lakh threshold
        risk_flags.append(
            {
                "level": "HIGH",
                "message": f"Maximum underlying exposure: {max_exposure:,.0f}",
            }
        )
    elif max_exposure > 50000:
        risk_flags.append(
            {
                "level": "MEDIUM",
                "message": f"Maximum underlying exposure: {max_exposure:,.0f}",
            }
        )
    else:
        risk_flags.append(
            {
                "level": "LOW",
                "message": f"Maximum underlying exposure: {max_exposure:,.0f}",
            }
        )

    report = {
        "timestamp": datetime.now().isoformat(),
        "per_underlying_exposure": dict(per_underlying),
        "ce_pe_bias": ce_pe_bias,
        "max_strike_concentration": {
            "strike_key": max_strike[0],
            "exposure": float(max_strike[1]),
        },
        "risk_flags": risk_flags,
    }

    # Save JSON
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[PH88] Portfolio risk analysis complete")

    # Generate MD
    generate_markdown(report)
    print(f"[PH88] Markdown report written to {OUTPUT_MD}")

    return report


def generate_markdown(report: Dict[str, Any]) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 88 - Portfolio Risk Report\n\n")
        f.write(f"**Date**: {report['timestamp']}\n\n")

        # Per underlying exposure
        f.write("## Per Underlying Exposure\n\n")
        f.write("| Underlying | Notional Exposure | Risk Flag |\n")
        f.write("|------------|-------------------|-----------|\n")

        for underlying, exposure in sorted(report["per_underlying_exposure"].items(), key=lambda x: x[1], reverse=True):
            if exposure > 100000:
                flag = "HIGH"
            elif exposure > 50000:
                flag = "MEDIUM"
            else:
                flag = "LOW"
            f.write(f"| {underlying} | {exposure:,.0f} | {flag} |\n")
        f.write("\n")

        # CE vs PE bias
        if report["ce_pe_bias"]:
            f.write("## CE vs PE Net Bias\n\n")
            f.write("| Underlying | CE Count | PE Count | Net Bias |\n")
            f.write("|------------|----------|----------|----------|\n")
            for underlying, bias in report["ce_pe_bias"].items():
                f.write(f"| {underlying} | {bias['ce_count']} | {bias['pe_count']} | {bias['net_bias']} |\n")
            f.write("\n")

        # Risk flags
        f.write("## Risk Flags\n\n")
        for flag in report["risk_flags"]:
            f.write(f"- **{flag['level']}**: {flag['message']}\n")


def main():
    """Main entry point."""
    try:
        report = analyze_portfolio_risk()
        print("\n[PH88] Portfolio risk analysis complete.")
        return 0
    except Exception as e:
        print(f"\n[PH88] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
