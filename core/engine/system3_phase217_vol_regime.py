"""
System3 Phase 217 - Volatility Regime Classifier

Classifies volatility regimes for major underlyings.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)
REGIMES_CSV = STORAGE_META / "system3_vol_regimes.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "risk"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_vol_regime_report.md"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"
UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def classify_regime(iv_rank: float) -> str:
    """Classify volatility regime based on IV rank."""
    if pd.isna(iv_rank):
        return "UNKNOWN"
    if iv_rank < 25:
        return "LOW"
    elif iv_rank > 75:
        return "HIGH"
    else:
        return "NORMAL"


def run_phase217(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 217: Volatility Regime Classifier.

    Returns:
        dict: {
            "phase": 217,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "underlyings_classified": int,
                "regimes_file": str,
            },
            "errors": [],
        }
    """
    errors = []
    regimes = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 217,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"underlyings_classified": 0, "regimes_file": str(REGIMES_CSV)},
                "errors": [],
            }

        # Load data
        try:
            df = pd.read_csv(SIGNALS_CSV)
        except Exception:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        if "underlying" not in df.columns or "iv_rank" not in df.columns:
            return {
                "phase": 217,
                "status": "WARN",
                "details": "Required columns not found",
                "outputs": {"underlyings_classified": 0, "regimes_file": str(REGIMES_CSV)},
                "errors": [],
            }

        # Parse dates
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            df["date"] = df["ts"].dt.date

        # Classify by underlying and date
        for underlying in UNDERLYINGS:
            underlying_df = df[df["underlying"] == underlying]
            if len(underlying_df) == 0:
                continue

            for date, group in underlying_df.groupby("date" if "date" in underlying_df.columns else "ts"):
                avg_iv_rank = group["iv_rank"].mean()
                regime = classify_regime(avg_iv_rank)

                regimes.append(
                    {
                        "date": str(date),
                        "underlying": underlying,
                        "iv_rank": avg_iv_rank,
                        "regime": regime,
                    }
                )

        # Save regimes
        if regimes:
            regimes_df = pd.DataFrame(regimes)
            regimes_df.to_csv(REGIMES_CSV, index=False)
        else:
            pd.DataFrame(columns=["date", "underlying", "iv_rank", "regime"]).to_csv(REGIMES_CSV, index=False)

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Volatility Regime Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Regimes Classified**: {len(regimes)}\n\n")

            if regimes:
                f.write("## Regime Distribution\n\n")
                regime_counts = pd.Series([r["regime"] for r in regimes]).value_counts()
                f.write("| Regime | Count |\n")
                f.write("|--------|-------|\n")
                for regime, count in regime_counts.items():
                    f.write(f"| {regime} | {count} |\n")
            else:
                f.write("## Status\n\n")
                f.write("⚠️ No volatility regimes classified (insufficient data).\n")

        status = "OK" if regimes else "WARN"
        details = f"Classified {len(regimes)} volatility regimes"

        return {
            "phase": 217,
            "status": status,
            "details": details,
            "outputs": {
                "underlyings_classified": len(set(r["underlying"] for r in regimes)),
                "regimes_file": str(REGIMES_CSV),
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 217,
            "status": "ERROR",
            "details": f"Phase 217 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 217 - VOLATILITY REGIME CLASSIFIER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase217()

    print(f"Phase 217: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nRegimes CSV: {result['outputs']['regimes_file']}")
        print(f"Underlyings: {result['outputs']['underlyings_classified']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
