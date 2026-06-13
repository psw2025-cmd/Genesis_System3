"""
System3 Phase 272 - Feature Selection Optimizer

Identifies optimal feature subsets for ML models.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)
FEATURE_SELECTION_JSON = STORAGE_META / "system3_feature_selection.json"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_feature_selection.md"


def run_phase272(**kwargs) -> Dict[str, Any]:
    """Run Phase 272: Feature Selection Optimizer."""
    errors = []

    try:
        # Load curated training data to analyze features
        CURATED_PATH = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_curated.csv"

        if not CURATED_PATH.exists():
            return {
                "phase": 272,
                "status": "WARN",
                "details": "Curated training data not found",
                "outputs": {"features_selected": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(CURATED_PATH, engine="python", on_bad_lines="skip", nrows=1000)
        except Exception as e:
            return {
                "phase": 272,
                "status": "WARN",
                "details": f"Error loading data: {e}",
                "outputs": {"features_selected": 0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        # Identify feature columns (exclude metadata columns)
        exclude_cols = ["ts", "underlying", "strike", "side", "expiry", "pred_label", "signal"]
        feature_cols = [c for c in df.columns if c not in exclude_cols and df[c].dtype in ["float64", "int64"]]

        # Simple feature selection: keep features with non-zero variance
        selected_features = []
        for col in feature_cols:
            if df[col].std() > 0.001:  # Non-zero variance threshold
                selected_features.append(col)

        # Save feature selection results
        selection_data = {
            "selected_features": selected_features,
            "total_features": len(feature_cols),
            "generated": datetime.now().isoformat(),
        }

        with FEATURE_SELECTION_JSON.open("w", encoding="utf-8") as f:
            json.dump(selection_data, f, indent=2)

        # Generate report
        report_lines = [
            "# System3 Feature Selection\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Total Features**: {len(feature_cols)}\n",
            f"**Selected Features**: {len(selected_features)}\n",
            "\n## Selected Features\n",
        ]

        for feat in selected_features[:20]:  # Show first 20
            report_lines.append(f"- {feat}\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Selected {len(selected_features)} features from {len(feature_cols)}"

        return {
            "phase": 272,
            "status": status,
            "details": details,
            "outputs": {
                "features_selected": len(selected_features),
                "total_features": len(feature_cols),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 272,
            "status": "ERROR",
            "details": f"Phase 272 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase272()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
