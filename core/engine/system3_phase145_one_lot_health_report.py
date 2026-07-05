"""
System3 Phase 145 - One-Lot Test-Mode Health Report

Summarizes 1-lot DRY-RUN testing health.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

CAPITAL_GUARDRAIL_CSV = STORAGE_ULTRA / "phase140_capital_guardrail.csv"
SLIPPAGE_CSV = STORAGE_ULTRA / "phase142_slippage_results.csv"
QUALITY_CSV = STORAGE_ULTRA / "phase143_execution_quality.csv"
PNL_SCENARIOS_CSV = STORAGE_ULTRA / "phase144_pnl_execution_scenarios.csv"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase145_one_lot_health_report.md"


def run_phase145_one_lot_health_report() -> Dict[str, Any]:
    """
    Generate 1-lot test-mode health report.

    Returns:
        dict: {
            "phase": 145,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load capital guardrail
        capital_data = {}
        if CAPITAL_GUARDRAIL_CSV.exists():
            try:
                import pandas as pd

                df_capital = pd.read_csv(CAPITAL_GUARDRAIL_CSV)
                for _, row in df_capital.iterrows():
                    capital_data[row["underlying"]] = {
                        "capital_usage_percent": row.get("capital_usage_percent", 0),
                        "max_lots_allowed": row.get("max_lots_allowed", 0),
                    }
            except Exception as e:
                errors.append(f"Error reading capital guardrail: {e}")

        # Load slippage summary
        slippage_summary = {}
        if SLIPPAGE_CSV.exists():
            try:
                import pandas as pd

                df_slippage = pd.read_csv(SLIPPAGE_CSV)
                if not df_slippage.empty:
                    for underlying in df_slippage["underlying"].unique():
                        underlying_data = df_slippage[df_slippage["underlying"] == underlying]
                        slippage_summary[underlying] = {
                            "avg_slippage": float(underlying_data["slippage_percent"].mean()),
                        }
            except Exception:
                pass

        # Load execution quality
        quality_summary = {}
        if QUALITY_CSV.exists():
            try:
                import pandas as pd

                df_quality = pd.read_csv(QUALITY_CSV)
                if not df_quality.empty:
                    for underlying in df_quality["underlying"].unique():
                        underlying_data = df_quality[df_quality["underlying"] == underlying]
                        total = len(underlying_data)
                        good_count = len(underlying_data[underlying_data["execution_quality"] == "GOOD"])
                        ok_count = len(underlying_data[underlying_data["execution_quality"] == "OK"])
                        quality_summary[underlying] = {
                            "good_ok_rate": ((good_count + ok_count) / total * 100) if total > 0 else 0,
                        }
            except Exception:
                pass

        # Load PnL scenarios
        pnl_summary = {}
        if PNL_SCENARIOS_CSV.exists():
            try:
                import pandas as pd

                df_pnl = pd.read_csv(PNL_SCENARIOS_CSV)
                if not df_pnl.empty:
                    for underlying in df_pnl["underlying"].unique():
                        underlying_data = df_pnl[df_pnl["underlying"] == underlying]
                        pnl_summary[underlying] = {
                            "worst_pnl_total": float(underlying_data["pnl_worst"].sum()),
                        }
            except Exception:
                pass

        # Determine health status per underlying
        health_statuses = {}
        for underlying in capital_data.keys():
            capital_usage = capital_data[underlying].get("capital_usage_percent", 100)
            max_lots = capital_data[underlying].get("max_lots_allowed", 0)

            # Check criteria
            capital_ok = capital_usage <= 80.0
            lot_ok = max_lots >= 1

            avg_slippage = slippage_summary.get(underlying, {}).get("avg_slippage", 0)
            slippage_ok = avg_slippage < 1.0  # Acceptable if < 1%

            good_ok_rate = quality_summary.get(underlying, {}).get("good_ok_rate", 0)
            quality_ok = good_ok_rate >= 70.0  # At least 70% GOOD/OK

            worst_pnl = pnl_summary.get(underlying, {}).get("worst_pnl_total", 0)
            # Assume acceptable drawdown is -10% of test capital (50k * 0.1 = 5k)
            pnl_ok = worst_pnl >= -5000.0

            # Determine overall status
            if capital_ok and lot_ok and slippage_ok and quality_ok and pnl_ok:
                status = "SAFE"
            elif capital_ok and lot_ok:
                status = "CAUTION"
            else:
                status = "UNSAFE"

            health_statuses[underlying] = {
                "status": status,
                "capital_ok": capital_ok,
                "lot_ok": lot_ok,
                "slippage_ok": slippage_ok,
                "quality_ok": quality_ok,
                "pnl_ok": pnl_ok,
            }

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 One-Lot Test-Mode Health Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Health Summary for 1-Lot DRY-RUN Testing\n\n")

            if health_statuses:
                f.write("| Underlying | Status | Capital OK | Lot OK | Slippage OK | Quality OK | PnL OK |\n")
                f.write("|------------|--------|------------|--------|-------------|------------|--------|\n")
                for underlying, health in health_statuses.items():
                    f.write(
                        f"| {underlying} | **{health['status']}** | {'✅' if health['capital_ok'] else '❌'} | {'✅' if health['lot_ok'] else '❌'} | {'✅' if health['slippage_ok'] else '❌'} | {'✅' if health['quality_ok'] else '❌'} | {'✅' if health['pnl_ok'] else '❌'} |\n"
                    )

                f.write("\n## Status Definitions\n\n")
                f.write("- **SAFE**: All checks passed, ready for 1-lot testing\n")
                f.write("- **CAUTION**: Some checks passed, proceed with caution\n")
                f.write("- **UNSAFE**: Critical checks failed, not ready for testing\n")

                f.write("\n## Per-Underlying Conclusions\n\n")
                for underlying, health in health_statuses.items():
                    f.write(f"### {underlying}\n\n")
                    f.write(f"**ONE_LOT_TEST_STATUS = {health['status']}**\n\n")
            else:
                f.write("No health data available. Run phases 140, 142, 143, 144 first.\n")

        status = "OK" if not errors else "ERROR"
        details = f"One-lot health report generated: {len(health_statuses)} underlyings analyzed"

        return {
            "phase": 145,
            "status": status,
            "details": details,
            "outputs": {
                "md_path": str(OUTPUT_MD_PATH),
                "underlying_count": len(health_statuses),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 145,
            "status": "ERROR",
            "details": f"Phase 145 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 145 - ONE-LOT TEST-MODE HEALTH REPORT")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase145_one_lot_health_report()

    print(f"Phase145: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nUnderlyings analyzed: {result['outputs']['underlying_count']}")
        print(f"Report: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
