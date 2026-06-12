"""
System3 Phase 224 - Score Component Attribution

Decomposes final_score into component contributions.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_score_component_attribution.md"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"

COMPONENT_COLS = ["greeks_score", "trend_score", "volatility_score", "breakout_score", "momentum_score", "ai_score"]


def run_phase224(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 224: Score Component Attribution.

    Returns:
        dict: {
            "phase": 224,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "components_analyzed": int,
                "report_path": str,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 224,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"components_analyzed": 0, "report_path": str(REPORT_PATH)},
                "errors": ["STEP 4: Signal generation did not create signals CSV"],
            }

        # Load data
        try:
            df = pd.read_csv(SIGNALS_CSV)
        except Exception:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        if df.empty:
            return {
                "phase": 224,
                "status": "WARN",
                "details": "Signals CSV is empty - no data to analyze",
                "outputs": {"components_analyzed": 0, "report_path": str(REPORT_PATH)},
                "errors": ["STEP 4: Signal generation produced no signals - check thresholds and component scores"],
            }

        if "final_score" not in df.columns:
            return {
                "phase": 224,
                "status": "WARN",
                "details": "final_score column not found",
                "outputs": {"components_analyzed": 0, "report_path": str(REPORT_PATH)},
                "errors": ["STEP 4: Signal generation incomplete - missing final_score column"],
            }

        # Find available component columns
        available_components = [col for col in COMPONENT_COLS if col in df.columns]

        if len(available_components) == 0:
            return {
                "phase": 224,
                "status": "WARN",
                "details": "No component score columns found",
                "outputs": {"components_analyzed": 0, "report_path": str(REPORT_PATH)},
                "errors": ["STEP 4: Component scores not computed - check signal engine steps 1-7"],
            }

        # Compute attribution statistics
        attribution_stats = []
        for component in available_components:
            component_abs = df[component].abs()
            final_abs = df["final_score"].abs()

            # Contribution ratio
            contribution_ratio = (component_abs / final_abs.replace(0, np.nan)).mean()

            # Correlation with final_score (handle zero variance cases)
            component_series = df[component].dropna()
            final_series = df["final_score"].dropna()

            # Align indices
            common_idx = component_series.index.intersection(final_series.index)
            if len(common_idx) < 2:
                correlation = np.nan
            else:
                comp_aligned = component_series.loc[common_idx]
                final_aligned = final_series.loc[common_idx]

                # Check for zero variance (all values same)
                if comp_aligned.std() == 0 or final_aligned.std() == 0:
                    correlation = np.nan
                else:
                    correlation = comp_aligned.corr(final_aligned)

            attribution_stats.append(
                {
                    "component": component,
                    "mean_contribution_ratio": contribution_ratio if not np.isnan(contribution_ratio) else 0.0,
                    "correlation": correlation if not np.isnan(correlation) else 0.0,
                    "mean_absolute_value": component_abs.mean(),
                }
            )

        # Sort by contribution
        attribution_stats.sort(key=lambda x: abs(x["mean_contribution_ratio"]), reverse=True)

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Score Component Attribution Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Components Analyzed**: {len(available_components)}\n\n")

            f.write("## Component Attribution Statistics\n\n")
            f.write("| Component | Mean Contribution Ratio | Correlation | Mean Abs Value |\n")
            f.write("|-----------|------------------------|-------------|----------------|\n")
            for stat in attribution_stats:
                f.write(
                    f"| {stat['component']} | {stat['mean_contribution_ratio']:.3f} | "
                    f"{stat['correlation']:.3f} | {stat['mean_absolute_value']:.3f} |\n"
                )

        status = "OK"
        details = f"Analyzed {len(available_components)} score components"

        return {
            "phase": 224,
            "status": status,
            "details": details,
            "outputs": {
                "components_analyzed": len(available_components),
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 224,
            "status": "ERROR",
            "details": f"Phase 224 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 224 - SCORE COMPONENT ATTRIBUTION")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase224()

    print(f"Phase 224: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")
        print(f"Components: {result['outputs']['components_analyzed']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
