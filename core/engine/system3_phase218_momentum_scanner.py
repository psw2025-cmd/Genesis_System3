"""
System3 Phase 218 - Momentum Pattern Scanner

Detects momentum patterns using technical indicators.
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
PATTERNS_CSV = STORAGE_META / "system3_momentum_patterns.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_momentum_scan_report.md"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"


def compute_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Compute RSI indicator."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def run_phase218(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 218: Momentum Pattern Scanner.

    Returns:
        dict: {
            "phase": 218,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "patterns_detected": int,
                "patterns_file": str,
            },
            "errors": [],
        }
    """
    errors = []
    patterns = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 218,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"patterns_detected": 0, "patterns_file": str(PATTERNS_CSV)},
                "errors": [],
            }

        # Load data
        try:
            df = pd.read_csv(SIGNALS_CSV)
        except Exception:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        if "underlying" not in df.columns or "spot" not in df.columns:
            return {
                "phase": 218,
                "status": "WARN",
                "details": "Required columns not found",
                "outputs": {"patterns_detected": 0, "patterns_file": str(PATTERNS_CSV)},
                "errors": [],
            }

        # Group by underlying and detect patterns
        for underlying, group in df.groupby("underlying"):
            if len(group) < 20:  # Need minimum data
                continue

            group = group.sort_values("ts" if "ts" in group.columns else group.index)

            if "spot" in group.columns:
                prices = group["spot"].dropna()
                if len(prices) < 14:
                    continue

                # Compute RSI
                rsi = compute_rsi(prices, window=14)

                # Detect patterns
                if len(rsi) > 0:
                    last_rsi = rsi.iloc[-1]
                    if last_rsi > 70:
                        patterns.append(
                            {
                                "timestamp": (
                                    group["ts"].iloc[-1] if "ts" in group.columns else datetime.now().isoformat()
                                ),
                                "underlying": underlying,
                                "pattern": "BULLISH_OVERSOLD",
                                "rsi": last_rsi,
                            }
                        )
                    elif last_rsi < 30:
                        patterns.append(
                            {
                                "timestamp": (
                                    group["ts"].iloc[-1] if "ts" in group.columns else datetime.now().isoformat()
                                ),
                                "underlying": underlying,
                                "pattern": "BEARISH_OVERSOLD",
                                "rsi": last_rsi,
                            }
                        )

        # Save patterns
        if patterns:
            patterns_df = pd.DataFrame(patterns)
            patterns_df.to_csv(PATTERNS_CSV, index=False)
        else:
            pd.DataFrame(columns=["timestamp", "underlying", "pattern", "rsi"]).to_csv(PATTERNS_CSV, index=False)

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Momentum Pattern Scan Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Patterns Detected**: {len(patterns)}\n\n")

            if patterns:
                f.write("## Detected Patterns\n\n")
                f.write("| Timestamp | Underlying | Pattern | RSI |\n")
                f.write("|-----------|------------|---------|-----|\n")
                for pattern in patterns:
                    f.write(
                        f"| {pattern['timestamp']} | {pattern['underlying']} | "
                        f"{pattern['pattern']} | {pattern.get('rsi', 'N/A'):.2f} |\n"
                    )
            else:
                f.write("## Status\n\n")
                f.write("⚠️ No momentum patterns detected (insufficient data or no signals).\n")

        status = "OK" if patterns else "WARN"
        details = f"Detected {len(patterns)} momentum patterns"

        return {
            "phase": 218,
            "status": status,
            "details": details,
            "outputs": {
                "patterns_detected": len(patterns),
                "patterns_file": str(PATTERNS_CSV),
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 218,
            "status": "ERROR",
            "details": f"Phase 218 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 218 - MOMENTUM PATTERN SCANNER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase218()

    print(f"Phase 218: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nPatterns CSV: {result['outputs']['patterns_file']}")
        print(f"Patterns: {result['outputs']['patterns_detected']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
