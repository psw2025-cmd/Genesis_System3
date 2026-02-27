"""
System3 Phase 381: Ultra Models Scanner

Purpose: Scan and inventory all available Ultra models
Outputs: JSON metrics + Markdown report

Safety: DRY-RUN only, no live trading, no safety config changes
"""

import sys
from pathlib import Path
import json
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger
from core.engine.ultra_models_loader import get_all_ultra_models_inventory

# Output paths
METRICS_DIR = ROOT_DIR / "storage" / "metrics"
REPORTS_DIR = ROOT_DIR / "reports"
METRICS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def run_phase_381() -> dict:
    """
    Phase 381: Ultra Models Presence Scanner

    Scans available Ultra model files and writes:
    - storage/metrics/ultra_models_inventory_381.json
    - reports/ULTRA_MODELS_INVENTORY_381.md

    Returns:
        {"status": "ok"|"warn"|"error", "message": str, "metrics": dict}
    """
    logger.info("=" * 60)
    logger.info("PHASE 381: ULTRA MODELS SCANNER")
    logger.info("=" * 60)

    try:
        # Get inventory from ultra_models_loader
        inventory = get_all_ultra_models_inventory()

        # Write JSON metrics
        metrics_file = METRICS_DIR / "ultra_models_inventory_381.json"
        with open(metrics_file, "w") as f:
            json.dump(inventory, f, indent=2)
        logger.info(f"✓ Metrics written: {metrics_file}")

        # Write Markdown report
        report_file = REPORTS_DIR / "ULTRA_MODELS_INVENTORY_381.md"
        with open(report_file, "w") as f:
            f.write("# ULTRA MODELS INVENTORY (PHASE 381)\n\n")
            f.write(f"**Scan Timestamp:** {inventory['scan_timestamp']}\n")
            f.write(f"**Models Found:** {inventory['models_found']}/{len(inventory['models'])}\n")
            f.write(f"**Models Missing:** {inventory['models_missing']}\n\n")

            f.write("## Models Inventory\n\n")
            f.write("| Underlying | Status | Size (KB) | Last Modified | Loadable |\n")
            f.write("|------------|--------|-----------|---------------|----------|\n")

            for model in inventory["models"]:
                status = "✅" if model["exists"] else "❌"
                size = f"{model['file_size_kb']:.2f}" if model["exists"] else "N/A"
                modified = model["last_modified"] if model["last_modified"] else "N/A"
                loadable = "✅" if model["loadable"] else "❌"

                f.write(f"| {model['underlying']} | {status} | {size} | {modified} | {loadable} |\n")

            f.write("\n## Model Paths\n\n")
            for model in inventory["models"]:
                f.write(f"- **{model['underlying']}**: `{model['model_path']}`\n")

            f.write("\n## Summary\n\n")
            if inventory["models_found"] == len(inventory["models"]):
                f.write("✅ **Status:** All Ultra models present and loadable\n")
                f.write("\n**Recommendation:** Proceed to Phase 382 (Sanity Validator)\n")
            elif inventory["models_found"] > 0:
                f.write(
                    f"⚠️ **Status:** Partial coverage ({inventory['models_found']}/{len(inventory['models'])} models)\n"
                )
                f.write("\n**Recommendation:** System will use delta fallback for missing models\n")
            else:
                f.write("❌ **Status:** No Ultra models found\n")
                f.write("\n**Recommendation:** System will use delta fallback for all underlyings\n")

        logger.info(f"✓ Report written: {report_file}")

        # Determine phase status
        if inventory["models_found"] == len(inventory["models"]):
            status = "ok"
            message = f"All {inventory['models_found']} Ultra models found and loadable"
        elif inventory["models_found"] > 0:
            status = "warn"
            message = f"Partial coverage: {inventory['models_found']}/{len(inventory['models'])} models"
        else:
            status = "error"
            message = "No Ultra models found"

        logger.info(f"Phase 381 Status: {status.upper()} - {message}")
        logger.info("=" * 60)

        return {"status": status, "message": message, "metrics": inventory}

    except Exception as e:
        logger.error(f"Phase 381 ERROR: {e}")
        return {"status": "error", "message": f"Phase 381 failed: {str(e)}", "metrics": {}}


if __name__ == "__main__":
    result = run_phase_381()
    print(f"\nPhase 381 Result: {result['status'].upper()} - {result['message']}")
    sys.exit(0 if result["status"] in ["ok", "warn"] else 1)
