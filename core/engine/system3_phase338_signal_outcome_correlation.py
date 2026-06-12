"""
System3 Phase 338 - Signal-to-Outcome Correlation Monitor

Monitors correlation between signal scores and actual forward returns.
Helps identify if scoring model is still predictive.
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Correlation thresholds
MIN_CORRELATION = 0.05  # Minimum acceptable correlation between score and forward return


def run_phase338_signal_outcome_correlation(root_path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Phase 338: Signal-to-Outcome Correlation Monitor

    Returns:
        Dict with phase status and results
    """
    logger.info("=" * 70)
    logger.info("PHASE 338: Signal-to-Outcome Correlation Monitor")
    logger.info("=" * 70)

    root = Path(root_path) if root_path else PROJECT_ROOT

    # Load forward signals
    forward_file = root / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"

    if not forward_file.exists():
        logger.warning(f"Forward signals file not found: {forward_file}")
        return {"phase": 338, "status": "WARN", "outputs": {"error": "Forward signals file not found"}}

    try:
        df = pd.read_csv(forward_file, low_memory=False)

        # Filter to rows with valid score and forward returns
        required_cols = ["final_score", "fwd_ret_1"]
        if not all(col in df.columns for col in required_cols):
            logger.warning(f"Missing required columns: {required_cols}")
            return {"phase": 338, "status": "WARN", "outputs": {"error": f"Missing required columns: {required_cols}"}}

        valid_df = df.dropna(subset=required_cols)
        n_valid = len(valid_df)

        logger.info(f"Valid rows for correlation: {n_valid}")

        warnings = []
        correlations = {}

        if n_valid < 10:
            warnings.append(f"Insufficient data for correlation: only {n_valid} valid rows")
        else:
            # Compute correlation between final_score and forward returns
            for fwd_col in ["fwd_ret_1", "fwd_ret_3", "fwd_ret_5"]:
                if fwd_col in df.columns:
                    corr_df = df[["final_score", fwd_col]].dropna()

                    if len(corr_df) >= 10:
                        corr = corr_df["final_score"].corr(corr_df[fwd_col])
                        correlations[fwd_col] = float(corr)

                        logger.info(f"Correlation (final_score vs {fwd_col}): {corr:.4f}")

                        if abs(corr) < MIN_CORRELATION:
                            warnings.append(f"Low correlation for {fwd_col}: {corr:.4f} (threshold: {MIN_CORRELATION})")

        # Compute correlation by signal type
        signal_correlations = {}
        if "signal" in df.columns:
            for signal_type in ["BUY", "SELL", "BUY_CE", "BUY_PE"]:
                subset = df[df["signal"] == signal_type]
                corr_df = subset[["final_score", "fwd_ret_1"]].dropna()

                if len(corr_df) >= 10:
                    corr = corr_df["final_score"].corr(corr_df["fwd_ret_1"])
                    signal_correlations[signal_type] = float(corr)
                    logger.info(f"Correlation for {signal_type}: {corr:.4f}")

        # Write correlation report
        diagnostics_dir = root / "storage" / "live" / "diagnostics"
        diagnostics_dir.mkdir(parents=True, exist_ok=True)

        correlation_report = {
            "timestamp": datetime.now().isoformat(),
            "phase": 338,
            "n_valid_rows": n_valid,
            "overall_correlations": correlations,
            "by_signal_type": signal_correlations,
            "warnings": warnings,
            "threshold": MIN_CORRELATION,
        }

        report_file = diagnostics_dir / "signal_outcome_correlation_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(correlation_report, f, indent=2)

        logger.info(f"Correlation report written to: {report_file}")

        # Determine status
        status = "WARN" if warnings else "OK"

        logger.info("=" * 70)
        logger.info(f"Phase 338 Complete: {status}")
        logger.info(f"Valid rows: {n_valid}")
        logger.info(f"Warnings: {len(warnings)}")
        logger.info("=" * 70)

        return {
            "phase": 338,
            "status": status,
            "outputs": correlation_report,
        }

    except Exception as e:
        logger.error(f"Error in Phase 338: {e}")
        return {"phase": 338, "status": "ERROR", "outputs": {"error": str(e)}}


def run_phase_338(**kwargs) -> str:
    """Wrapper for autorun integration - returns status string."""
    result = run_phase338_signal_outcome_correlation(**kwargs)
    return result.get("status", "ERROR")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    result = run_phase338_signal_outcome_correlation()
    print(f"\nPhase 338 Status: {result['status']}")
