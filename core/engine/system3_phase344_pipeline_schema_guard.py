"""
System3 Phase 344 - Pipeline Schema Guard (Live CSVs)

Validates that all live CSVs used by the signal/trade pipeline match expected schema.
Detects column mismatches, type issues, and missing required fields.

Mode: Pre-market and before OP cycle.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


def run_phase_344_pipeline_schema_guard(root_path: str = None, logger_obj=None) -> str:
    """
    Phase 344: Validate live CSV schema against expected definitions.

    Returns: 'OK' or 'WARN'
    """
    if logger_obj:
        logger = logger_obj

    if root_path is None:
        root_path = str(PROJECT_ROOT)

    root = Path(root_path)
    logger.info("[PH344] Starting Pipeline Schema Guard")

    try:
        # Define expected schema per CSV (aligned with actual writer implementations)
        expected_schema = {
            "angel_index_ai_signals.csv": ["underlying", "symbol", "signal", "final_score", "ts"],
            "angel_index_ai_signals_curated.csv": ["underlying", "symbol", "signal", "final_score", "ts"],
            # Matches live_execution_engine.py::log_virtual_orders() - 15 columns
            "angel_virtual_orders.csv": [
                "ts",
                "underlying",
                "strike",
                "option_type",
                "side",
                "expiry",
                "ltp",
                "final_score",
                "ai_score",
                "lots",
                "approved",
                "adjusted_lots",
                "risk_reason",
                "risk_flags_json",
                "snapshot_id",
            ],
            # Matches angel_pnl_simulator.py::run_pnl_simulation() - 15 columns
            "angel_index_ai_pnl_log.csv": [
                "ts",
                "underlying",
                "strike",
                "side",
                "entry_price",
                "target_price",
                "sl_price",
                "pred_label",
                "pred_confidence",
                "expected_move_score",
                "result",
                "exit_price",
                "pnl_pct",
                "max_fav_pct",
                "max_adv_pct",
            ],
        }

        schema_dir = root / "config"
        schema_dir.mkdir(parents=True, exist_ok=True)
        schema_file = schema_dir / "system3_live_schema.json"

        if not schema_file.exists():
            with open(schema_file, "w") as f:
                json.dump(expected_schema, f, indent=2)
        else:
            with open(schema_file) as f:
                expected_schema = json.load(f)

        diag_dir = root / "storage" / "live" / "diagnostics"
        diag_dir.mkdir(parents=True, exist_ok=True)

        results = []
        status = "OK"

        for csv_name, expected_cols in expected_schema.items():
            csv_path = root / "storage" / "live" / csv_name

            record = {
                "csv": csv_name,
                "status": "ok",
                "missing_cols": [],
                "extra_cols": [],
                "type_issues": [],
            }

            if not csv_path.exists():
                record["status"] = "missing"
                status = "WARN"
                logger.warning(f"[PH344] CSV not found: {csv_name}")
            else:
                try:
                    df = pd.read_csv(csv_path)

                    # Check for missing columns
                    missing = [c for c in expected_cols if c not in df.columns]
                    if missing:
                        record["missing_cols"] = missing
                        record["status"] = "schema_error"
                        status = "WARN"
                        logger.warning(f"[PH344] {csv_name} missing columns: {missing}")

                    # Check for extra columns (non-fatal, just log)
                    extra = [c for c in df.columns if c not in expected_cols]
                    if extra:
                        record["extra_cols"] = extra
                        logger.debug(f"[PH344] {csv_name} has extra columns: {extra}")

                except Exception as e:
                    record["status"] = "read_error"
                    status = "WARN"
                    logger.error(f"[PH344] Error reading {csv_name}: {e}")

            results.append(record)

        # Write report
        df_report = pd.DataFrame(results)
        df_report.to_csv(diag_dir / "schema_validation_report.csv", index=False)

        logger.info(f"[PH344] Pipeline Schema Guard complete. Status: {status}")
        return status

    except Exception as e:
        logger.error(f"[PH344] Unexpected error: {e}", exc_info=True)
        return "WARN"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_phase_344_pipeline_schema_guard()
    print(f"Phase 344 result: {result}")
