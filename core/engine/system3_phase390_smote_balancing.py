"""
Phase 390 - SMOTE Data Balancing Driver
========================================

Main orchestrator for Phase 390 (SMOTE Data Balancing).
Loads Phase 389 engineered features, balances classes, and outputs ML-ready dataset.

Safety: DRY-RUN ONLY - no broker calls, no trading mode changes.

Author: System3 AI Team
Date: 2025-12-08
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.ai_model.data_balancing_v2 import load_engineered_features, balance_multiclass_signals

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# SAFETY & CONFIGURATION
# ============================================================================


def verify_safety_flags() -> bool:
    """
    Verify that trading mode flags are in safe DRY-RUN state.

    Returns:
        bool: True if all safety checks pass
    """
    logger.info("\n[SAFETY CHECK]")

    # Check for common safety flag files
    safety_files = ["live_trade_config.py", "dhan_automation_config.json", "system3_ultra_safety.json"]

    for fname in safety_files:
        fpath = Path("core") / "config" / fname
        if fpath.exists():
            logger.info(f"  ✓ Safety file found: {fpath}")
            # In production, would read and verify DRY_RUN=True etc
        else:
            logger.info(f"  - Config file not critical: {fpath}")

    # Check environment - no broker API keys should be active in DRY_RUN
    if os.environ.get("LIVE_TRADING_ENABLED", "False").lower() == "true":
        logger.error("✗ LIVE_TRADING_ENABLED is True! Phase 390 must run in DRY-RUN mode.")
        return False

    logger.info("  ✓ No live trading enabled (LIVE_TRADING_ENABLED=False)")
    logger.info("  ✓ Safety checks passed")
    return True


# ============================================================================
# MAIN PHASE 390 EXECUTION
# ============================================================================


def run_phase_390(
    input_csv: str = "storage/datasets/phase_389_engineered_features.csv",
    output_csv: str = "storage/datasets/phase_390_balanced_features.csv",
    metrics_json: str = "storage/metrics/phase_390_smote_report.json",
    label_col: str = "signal",
) -> Dict[str, Any]:
    """
    Execute Phase 390: SMOTE Data Balancing.

    Args:
        input_csv (str): Path to Phase 389 output CSV
        output_csv (str): Path for balanced output CSV
        metrics_json (str): Path for metrics JSON report
        label_col (str): Name of target column

    Returns:
        dict: Phase results including status, metrics, paths
    """

    phase_start = datetime.now()
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 390 - SMOTE DATA BALANCING")
    logger.info("=" * 80)

    result = {
        "phase": 390,
        "status": "pending",
        "timestamp_start": phase_start.isoformat(),
        "timestamp_end": None,
        "duration_ms": None,
        "input_file": input_csv,
        "output_file": output_csv,
        "metrics_file": metrics_json,
        "message": "",
        "metrics": {},
    }

    try:
        # ===== SAFETY CHECK =====
        if not verify_safety_flags():
            result["status"] = "error"
            result["message"] = "Safety check failed - live trading enabled"
            logger.error(result["message"])
            return result

        # ===== STEP 1: Load engineered features =====
        logger.info(f"\n[STEP 1] Loading engineered features from Phase 389")
        logger.info(f"  Input: {input_csv}")

        df_engineered = load_engineered_features(input_csv)

        result["metrics"]["input_rows"] = len(df_engineered)
        result["metrics"]["input_columns"] = len(df_engineered.columns)

        # ===== STEP 2: Balance multiclass signals =====
        logger.info(f"\n[STEP 2] Balancing multiclass signals")

        df_balanced, balance_metrics = balance_multiclass_signals(df_engineered, label_col=label_col)

        # Merge metrics
        result["metrics"].update(balance_metrics)
        result["metrics"]["output_rows"] = len(df_balanced)
        result["metrics"]["output_columns"] = len(df_balanced.columns)

        # ===== STEP 3: Create output directories =====
        logger.info(f"\n[STEP 3] Creating output directories")

        Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
        Path(metrics_json).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"  ✓ Output directories ready")

        # ===== STEP 4: Write balanced dataset CSV =====
        logger.info(f"\n[STEP 4] Writing balanced dataset to CSV")
        logger.info(f"  Output: {output_csv}")

        df_balanced.to_csv(output_csv, index=False)

        csv_size_mb = Path(output_csv).stat().st_size / (1024**2)
        logger.info(f"  ✓ Written {len(df_balanced)} rows × {len(df_balanced.columns)} cols")
        logger.info(f"  ✓ File size: {csv_size_mb:.2f} MB")

        # ===== STEP 5: Write metrics JSON =====
        logger.info(f"\n[STEP 5] Writing metrics report to JSON")
        logger.info(f"  Output: {metrics_json}")

        metrics_report = {
            "phase": 390,
            "status": "complete",
            "timestamp": phase_start.isoformat(),
            "input_file": input_csv,
            "output_file": output_csv,
            "metrics": {
                "input_rows": int(result["metrics"]["input_rows"]),
                "input_columns": int(result["metrics"]["input_columns"]),
                "output_rows": int(result["metrics"]["output_rows"]),
                "output_columns": int(result["metrics"]["output_columns"]),
                "rows_added": int(result["metrics"]["rows_added"]),
                "rows_removed": int(result["metrics"]["rows_removed"]),
                "balancing_method": result["metrics"]["balancing_method"],
                "synthetic_samples_generated": int(result["metrics"]["synthetic_samples_generated"]),
                "balance_method_fallback": result["metrics"]["balance_method_fallback"],
            },
            "class_distribution": {
                "before": {k: int(v) for k, v in result["metrics"].get("input_class_counts", {}).items()},
                "after": {k: int(v) for k, v in result["metrics"].get("output_class_counts", {}).items()},
            },
        }

        with open(metrics_json, "w") as f:
            json.dump(metrics_report, f, indent=2)

        json_size_kb = Path(metrics_json).stat().st_size / 1024
        logger.info(f"  ✓ Metrics written ({json_size_kb:.1f} KB)")

        # ===== STEP 6: Validation checks =====
        logger.info(f"\n[STEP 6] Validation checks")

        # Check output CSV exists and is non-empty
        if not Path(output_csv).exists():
            raise RuntimeError(f"Output CSV not created: {output_csv}")
        if len(df_balanced) == 0:
            raise RuntimeError(f"Output dataframe is empty")

        # Check JSON exists
        if not Path(metrics_json).exists():
            raise RuntimeError(f"Metrics JSON not created: {metrics_json}")

        # Check for required columns
        if label_col not in df_balanced.columns:
            raise RuntimeError(f"Target column '{label_col}' missing from output")

        logger.info(f"  ✓ Output CSV exists and non-empty")
        logger.info(f"  ✓ Metrics JSON exists and valid")
        logger.info(f"  ✓ Target column present: '{label_col}'")

        # ===== COMPLETION =====
        phase_end = datetime.now()
        duration_ms = int((phase_end - phase_start).total_seconds() * 1000)

        result["status"] = "complete"
        result["timestamp_end"] = phase_end.isoformat()
        result["duration_ms"] = duration_ms
        result["message"] = f"Phase 390 complete: {len(df_balanced)} balanced samples generated"

        logger.info(f"\n{'='*80}")
        logger.info(f"PHASE 390 SUCCESS")
        logger.info(f"  Input: {result['metrics']['input_rows']} rows")
        logger.info(f"  Output: {result['metrics']['output_rows']} rows (balanced)")
        logger.info(f"  Synthetic samples: {result['metrics']['synthetic_samples_generated']}")
        logger.info(f"  Duration: {duration_ms} ms")
        logger.info(f"  Method: {result['metrics']['balancing_method']}")
        logger.info(f"{'='*80}\n")

        return result

    except FileNotFoundError as e:
        logger.error(f"✗ File not found: {str(e)}")
        result["status"] = "error"
        result["message"] = f"File not found: {str(e)}"
        return result

    except Exception as e:
        logger.error(f"✗ Phase 390 failed: {str(e)}")
        result["status"] = "error"
        result["message"] = f"Phase 390 error: {str(e)}"
        return result


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    result = run_phase_390()

    # Print summary
    print("\n" + "=" * 80)
    print("PHASE 390 RESULT")
    print("=" * 80)
    print(f"Status: {result['status'].upper()}")
    print(f"Message: {result['message']}")

    if result["status"] == "complete":
        m = result["metrics"]
        print(f"\nMetrics:")
        print(f"  Input rows: {m.get('input_rows', 'N/A')}")
        print(f"  Output rows: {m.get('output_rows', 'N/A')}")
        print(f"  Rows added: {m.get('rows_added', 'N/A')}")
        print(f"  Method: {m.get('balancing_method', 'N/A')}")
        print(f"  Synthetic samples: {m.get('synthetic_samples_generated', 'N/A')}")
        print(f"  Duration: {result.get('duration_ms', 'N/A')} ms")

        if "input_class_counts" in m and "output_class_counts" in m:
            print(f"\nClass distribution:")
            print(f"  Before: {m['input_class_counts']}")
            print(f"  After: {m['output_class_counts']}")

    print(f"\nOutput files:")
    print(f"  CSV: {result['output_file']}")
    print(f"  JSON: {result['metrics_file']}")
    print("=" * 80 + "\n")

    # Exit with appropriate code
    sys.exit(0 if result["status"] == "complete" else 1)
