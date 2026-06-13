"""
System3 Phase 332 - Signal Volume & Coverage Monitor

Monitors signal volume and coverage across indices/options to ensure meaningful operation.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Thresholds
MIN_TOTAL_ROWS = 50
MIN_INDEX_ROWS = 5
MIN_SIGNAL_TYPE_ROWS = 3

# Target indices
EXPECTED_INDICES = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]


def run_phase332_signal_volume_coverage(root_path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Phase 332: Signal Volume & Coverage Monitor

    Returns:
        Dict with phase status and results
    """
    logger.info("=" * 70)
    logger.info("PHASE 332: Signal Volume & Coverage Monitor")
    logger.info("=" * 70)

    root = Path(root_path) if root_path else PROJECT_ROOT

    # Load curated signals
    signals_file = root / "storage" / "live" / "dhan_index_ai_signals_curated.csv"

    warnings = []

    if not signals_file.exists():
        logger.error(f"Signal file not found: {signals_file}")
        return {
            "phase": 332,
            "status": "ERROR",
            "outputs": {
                "error": "Signal file not found",
                "warnings": ["Signal file missing"],
            },
        }

    try:
        df = pd.read_csv(signals_file, low_memory=False)

        # Total rows
        total_rows = len(df)
        logger.info(f"Total signal rows: {total_rows}")

        if total_rows < MIN_TOTAL_ROWS:
            warnings.append(f"Low total signal volume: {total_rows} rows, threshold {MIN_TOTAL_ROWS}")

        # Count by index (underlying)
        by_index = {}
        if "underlying" in df.columns:
            by_index = df["underlying"].value_counts().to_dict()

            logger.info("Signal distribution by underlying:")
            for idx, count in by_index.items():
                logger.info(f"  {idx}: {count} rows")
                if count < MIN_INDEX_ROWS:
                    warnings.append(f"Low signal volume for {idx}: {count} rows, threshold {MIN_INDEX_ROWS}")

        # Count by signal type
        by_signal = {}
        if "signal" in df.columns:
            by_signal = df["signal"].value_counts().to_dict()

            logger.info("Signal distribution by type:")
            for sig_type, count in by_signal.items():
                logger.info(f"  {sig_type}: {count} rows")
                if count < MIN_SIGNAL_TYPE_ROWS:
                    warnings.append(
                        f"Low volume for signal type '{sig_type}': {count} rows, threshold {MIN_SIGNAL_TYPE_ROWS}"
                    )

        # Check for expected indices
        missing_indices = [idx for idx in EXPECTED_INDICES if idx not in by_index]
        if missing_indices:
            warnings.append(f"Missing expected indices: {missing_indices}")

        # Write summary
        diagnostics_dir = root / "storage" / "live" / "diagnostics"
        diagnostics_dir.mkdir(parents=True, exist_ok=True)

        summary = {
            "timestamp": datetime.now().isoformat(),
            "phase": 332,
            "total_rows": total_rows,
            "by_index": by_index,
            "by_signal": by_signal,
            "warnings": warnings,
            "thresholds": {
                "min_total_rows": MIN_TOTAL_ROWS,
                "min_index_rows": MIN_INDEX_ROWS,
                "min_signal_type_rows": MIN_SIGNAL_TYPE_ROWS,
            },
        }

        summary_file = diagnostics_dir / "signal_volume_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Summary written to: {summary_file}")

        # Determine status
        status = "WARN" if warnings else "OK"

        logger.info("=" * 70)
        logger.info(f"Phase 332 Complete: {status}")
        logger.info(f"Total rows: {total_rows}")
        logger.info(f"Warnings: {len(warnings)}")
        logger.info("=" * 70)

        return {
            "phase": 332,
            "status": status,
            "outputs": summary,
        }

    except Exception as e:
        logger.error(f"Error in Phase 332: {e}")
        return {
            "phase": 332,
            "status": "ERROR",
            "outputs": {
                "error": str(e),
                "warnings": [f"Failed to process signals: {str(e)}"],
            },
        }


def run_phase_332(**kwargs) -> str:
    """Wrapper for autorun integration - returns status string."""
    result = run_phase332_signal_volume_coverage(**kwargs)
    return result.get("status", "ERROR")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    result = run_phase332_signal_volume_coverage()
    print(f"\nPhase 332 Status: {result['status']}")
