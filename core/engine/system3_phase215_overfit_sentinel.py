"""
System3 Phase 215 - Model Overfit Sentinel

Detects overfitting in ML models.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "ml"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_overfit_sentinel_report.md"

PERFORMANCE_GAP_THRESHOLD = 0.15  # 15% gap indicates overfitting


def run_phase215(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 215: Model Overfit Sentinel.

    Returns:
        dict: {
            "phase": 215,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "models_checked": int,
                "overfit_cases": int,
            },
            "errors": [],
        }
    """
    errors = []
    overfit_cases = []

    try:
        # In a real implementation, this would load stored metrics
        # For now, this is a stub that checks for overfitting patterns

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Model Overfit Sentinel Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Threshold**: {PERFORMANCE_GAP_THRESHOLD * 100}% gap\n\n")

            f.write("## Model Evaluation\n\n")
            f.write("⚠️ **Note**: Model validation metrics not yet stored.\n")
            f.write("This phase requires training metrics to be logged during model training.\n\n")

            f.write("## Recommendations\n\n")
            f.write("1. Ensure training and validation metrics are logged during model training\n")
            f.write("2. Compare training vs validation accuracy/score\n")
            f.write("3. Flag models with gap > 15% as potentially overfit\n")
            f.write("4. Consider regularization or reducing model complexity\n")

        status = "WARN"
        details = "Overfit detection requires stored validation metrics"

        return {
            "phase": 215,
            "status": status,
            "details": details,
            "outputs": {
                "models_checked": 0,
                "overfit_cases": len(overfit_cases),
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 215,
            "status": "ERROR",
            "details": f"Phase 215 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 215 - MODEL OVERFIT SENTINEL")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase215()

    print(f"Phase 215: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
