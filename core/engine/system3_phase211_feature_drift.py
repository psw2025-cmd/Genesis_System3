"""
System3 Phase 211 - Feature Drift Monitor

Monitors feature distribution shifts over time.
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

LOG_DIR = PROJECT_ROOT / "logs" / "ml"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_feature_drift_report.md"

CURATED_CSV = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals_curated.csv"
DRIFT_THRESHOLD_SIGMA = 3.0
KEY_FEATURES = ["delta", "gamma", "theta", "vega", "iv", "iv_rank", "iv_percentile"]


def run_phase211(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 211: Feature Drift Monitor.

    Returns:
        dict: {
            "phase": 211,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "features_checked": int,
                "drifted_features": list,
            },
            "errors": [],
        }
    """
    errors = []
    drifted_features = []

    try:
        if not CURATED_CSV.exists():
            return {
                "phase": 211,
                "status": "WARN",
                "details": "Curated CSV not found",
                "outputs": {"features_checked": 0, "drifted_features": []},
                "errors": [],
            }

        # Load data
        try:
            df = pd.read_csv(CURATED_CSV)
        except Exception:
            df = pd.read_csv(CURATED_CSV, engine="python", on_bad_lines="skip")

        # Check available features
        available_features = [f for f in KEY_FEATURES if f in df.columns]

        if len(available_features) == 0:
            return {
                "phase": 211,
                "status": "WARN",
                "details": "No key features found",
                "outputs": {"features_checked": 0, "drifted_features": []},
                "errors": [],
            }

        # Compute baseline (first half) vs recent (last half)
        mid_point = len(df) // 2
        baseline = df.iloc[:mid_point]
        recent = df.iloc[mid_point:]

        drift_results = []
        for feature in available_features:
            baseline_mean = baseline[feature].mean()
            baseline_std = baseline[feature].std()
            recent_mean = recent[feature].mean()

            if baseline_std > 0:
                z_score = abs(recent_mean - baseline_mean) / baseline_std
                if z_score > DRIFT_THRESHOLD_SIGMA:
                    drifted_features.append(feature)
                    drift_results.append(
                        {
                            "feature": feature,
                            "baseline_mean": baseline_mean,
                            "recent_mean": recent_mean,
                            "z_score": z_score,
                        }
                    )

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Feature Drift Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Threshold**: {DRIFT_THRESHOLD_SIGMA}σ\n\n")
            f.write(f"**Features Checked**: {len(available_features)}\n")
            f.write(f"**Drifted Features**: {len(drifted_features)}\n\n")

            if drift_results:
                f.write("## Drifted Features\n\n")
                f.write("| Feature | Baseline Mean | Recent Mean | Z-Score |\n")
                f.write("|---------|---------------|-------------|----------|\n")
                for result in drift_results:
                    f.write(
                        f"| {result['feature']} | {result['baseline_mean']:.4f} | "
                        f"{result['recent_mean']:.4f} | {result['z_score']:.2f} |\n"
                    )
            else:
                f.write("## Status\n\n")
                f.write("✅ No significant feature drift detected.\n")

        status = "WARN" if drifted_features else "OK"
        details = f"Checked {len(available_features)} features"
        if drifted_features:
            details += f", {len(drifted_features)} drifted"

        return {
            "phase": 211,
            "status": status,
            "details": details,
            "outputs": {
                "features_checked": len(available_features),
                "drifted_features": drifted_features,
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 211,
            "status": "ERROR",
            "details": f"Phase 211 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 211 - FEATURE DRIFT MONITOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase211()

    print(f"Phase 211: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")
        print(f"Checked: {result['outputs']['features_checked']}")
        print(f"Drifted: {len(result['outputs']['drifted_features'])}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
