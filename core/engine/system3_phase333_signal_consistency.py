"""
System3 Phase 333 - Signal Consistency & Duplicate Detector

Detects suspicious duplicates or inconsistent entries in the curated signal file.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


def run_phase333_signal_consistency(root_path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Phase 333: Signal Consistency & Duplicate Detector

    Returns:
        Dict with phase status and results
    """
    logger.info("=" * 70)
    logger.info("PHASE 333: Signal Consistency & Duplicate Detector")
    logger.info("=" * 70)

    root = Path(root_path) if root_path else PROJECT_ROOT

    # Load curated signals
    signals_file = root / "storage" / "live" / "dhan_index_ai_signals_curated.csv"

    if not signals_file.exists():
        logger.error(f"Signal file not found: {signals_file}")
        return {"phase": 333, "status": "ERROR", "outputs": {"error": "Signal file not found"}}

    try:
        df = pd.read_csv(signals_file, low_memory=False)

        duplicate_count = 0
        conflict_count = 0
        warnings = []
        duplicates = []
        conflicts = []

        # Define uniqueness key columns
        key_cols = []
        for col in ["underlying", "symbol", "expiry", "strike", "side", "ts"]:
            if col in df.columns:
                key_cols.append(col)

        if not key_cols:
            logger.warning("No key columns found for duplicate detection")
            status = "WARN"
            warnings.append("Cannot perform duplicate detection: missing key columns")
        else:
            logger.info(f"Using key columns for uniqueness: {key_cols}")

            # Check for exact duplicates (same key, same signal)
            if "signal" in df.columns:
                full_key = key_cols + ["signal"]
                dup_mask = df.duplicated(subset=full_key, keep="first")
                duplicate_count = dup_mask.sum()

                if duplicate_count > 0:
                    logger.warning(f"Found {duplicate_count} exact duplicate rows")
                    warnings.append(f"{duplicate_count} exact duplicate rows detected")

                    # Get sample duplicates
                    dup_rows = df[dup_mask].head(5)
                    for _, row in dup_rows.iterrows():
                        dup_info = {col: str(row[col]) for col in key_cols if col in row}
                        dup_info["signal"] = str(row["signal"])
                        duplicates.append(dup_info)

            # Check for conflicts (same key but different signal)
            grouped = df.groupby(key_cols, dropna=False)
            for key, group in grouped:
                if len(group) > 1 and "signal" in df.columns:
                    unique_signals = group["signal"].unique()
                    if len(unique_signals) > 1:
                        conflict_count += 1

                        # Build key description
                        key_dict = {
                            key_cols[i]: key[i] if isinstance(key, tuple) else key for i in range(len(key_cols))
                        }
                        conflict_info = {"key": key_dict, "signals": list(unique_signals), "count": len(group)}
                        conflicts.append(conflict_info)

                        if conflict_count <= 5:  # Log first 5
                            logger.warning(f"Conflicting signals for {key_dict}: {list(unique_signals)}")

            if conflict_count > 0:
                warnings.append(f"{conflict_count} conflicting signal groups detected")

        # Write diagnostics report
        diagnostics_dir = root / "storage" / "live" / "diagnostics"
        diagnostics_dir.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": datetime.now().isoformat(),
            "phase": 333,
            "total_rows": len(df),
            "duplicate_count": int(duplicate_count),
            "conflict_count": int(conflict_count),
            "warnings": warnings,
            "sample_duplicates": duplicates[:10],
            "sample_conflicts": conflicts[:10],
            "key_columns": key_cols,
        }

        report_file = diagnostics_dir / "signal_consistency_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report written to: {report_file}")

        # Determine status
        status = "WARN" if (duplicate_count > 0 or conflict_count > 0) else "OK"

        logger.info("=" * 70)
        logger.info(f"Phase 333 Complete: {status}")
        logger.info(f"Duplicates: {duplicate_count}")
        logger.info(f"Conflicts: {conflict_count}")
        logger.info("=" * 70)

        return {
            "phase": 333,
            "status": status,
            "outputs": report,
        }

    except Exception as e:
        logger.error(f"Error in Phase 333: {e}")
        return {"phase": 333, "status": "ERROR", "outputs": {"error": str(e)}}


def run_phase_333(**kwargs) -> str:
    """Wrapper for autorun integration - returns status string."""
    result = run_phase333_signal_consistency(**kwargs)
    return result.get("status", "ERROR")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    result = run_phase333_signal_consistency()
    print(f"\nPhase 333 Status: {result['status']}")
