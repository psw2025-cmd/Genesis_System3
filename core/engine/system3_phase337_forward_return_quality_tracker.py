"""
System3 Phase 337 - Live Forward-Return Quality Tracker

Tracks the quality of forward return data being captured in live signals.
Monitors: data freshness, completeness, anomalies.
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Quality thresholds
MIN_COMPLETENESS_PCT = 70.0  # % of signals that should have forward returns
MAX_AGE_HOURS = 24  # Max acceptable age for forward return data


def run_phase337_forward_return_quality_tracker(root_path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Phase 337: Live Forward-Return Quality Tracker

    Returns:
        Dict with phase status and results
    """
    logger.info("=" * 70)
    logger.info("PHASE 337: Live Forward-Return Quality Tracker")
    logger.info("=" * 70)

    root = Path(root_path) if root_path else PROJECT_ROOT

    # Load forward signals
    forward_file = root / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"

    if not forward_file.exists():
        logger.warning(f"Forward signals file not found: {forward_file}")
        return {"phase": 337, "status": "WARN", "outputs": {"error": "Forward signals file not found"}}

    try:
        df = pd.read_csv(forward_file, low_memory=False)

        total_rows = len(df)
        logger.info(f"Total signal rows: {total_rows}")

        warnings = []
        quality_metrics = {}

        # Check completeness of forward returns
        fwd_cols = ["fwd_ret_1", "fwd_ret_3", "fwd_ret_5"]
        for col in fwd_cols:
            if col in df.columns:
                non_null = df[col].notna().sum()
                completeness_pct = (non_null / total_rows * 100) if total_rows > 0 else 0.0
                quality_metrics[f"{col}_completeness_pct"] = completeness_pct

                logger.info(f"{col}: {non_null}/{total_rows} ({completeness_pct:.1f}%) complete")

                if completeness_pct < MIN_COMPLETENESS_PCT:
                    warnings.append(
                        f"{col} completeness below threshold: {completeness_pct:.1f}% < {MIN_COMPLETENESS_PCT}%"
                    )

        # Check for anomalous forward returns (extreme values)
        for col in fwd_cols:
            if col in df.columns:
                valid_data = df[col].dropna()
                if len(valid_data) > 0:
                    mean_ret = valid_data.mean()
                    std_ret = valid_data.std()
                    min_ret = valid_data.min()
                    max_ret = valid_data.max()

                    quality_metrics[f"{col}_mean"] = float(mean_ret)
                    quality_metrics[f"{col}_std"] = float(std_ret)
                    quality_metrics[f"{col}_min"] = float(min_ret)
                    quality_metrics[f"{col}_max"] = float(max_ret)

                    # Detect extreme outliers (>5 std from mean)
                    outliers = ((valid_data - mean_ret).abs() > 5 * std_ret).sum()
                    if outliers > 0:
                        warnings.append(f"{col} has {outliers} extreme outliers (>5σ from mean)")

        # Check data freshness (if timestamp column exists)
        if "ts" in df.columns:
            try:
                df["ts_parsed"] = pd.to_datetime(df["ts"], errors="coerce")
                latest_ts = df["ts_parsed"].max()

                if pd.notna(latest_ts):
                    age_hours = (datetime.now() - latest_ts).total_seconds() / 3600
                    quality_metrics["data_age_hours"] = float(age_hours)

                    logger.info(f"Latest timestamp: {latest_ts}, age: {age_hours:.1f} hours")

                    if age_hours > MAX_AGE_HOURS:
                        warnings.append(
                            f"Forward return data is stale: {age_hours:.1f} hours old (threshold: {MAX_AGE_HOURS}h)"
                        )
            except Exception as e:
                logger.warning(f"Could not parse timestamps: {e}")

        # Write quality report
        diagnostics_dir = root / "storage" / "live" / "diagnostics"
        diagnostics_dir.mkdir(parents=True, exist_ok=True)

        quality_report = {
            "timestamp": datetime.now().isoformat(),
            "phase": 337,
            "total_rows": total_rows,
            "quality_metrics": quality_metrics,
            "warnings": warnings,
            "thresholds": {
                "min_completeness_pct": MIN_COMPLETENESS_PCT,
                "max_age_hours": MAX_AGE_HOURS,
            },
        }

        report_file = diagnostics_dir / "forward_return_quality_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(quality_report, f, indent=2)

        logger.info(f"Quality report written to: {report_file}")

        # Determine status
        status = "WARN" if warnings else "OK"

        logger.info("=" * 70)
        logger.info(f"Phase 337 Complete: {status}")
        logger.info(f"Warnings: {len(warnings)}")
        logger.info("=" * 70)

        return {
            "phase": 337,
            "status": status,
            "outputs": quality_report,
        }

    except Exception as e:
        logger.error(f"Error in Phase 337: {e}")
        return {"phase": 337, "status": "ERROR", "outputs": {"error": str(e)}}


def run_phase_337(**kwargs) -> str:
    """Wrapper for autorun integration - returns status string."""
    result = run_phase337_forward_return_quality_tracker(**kwargs)
    return result.get("status", "ERROR")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    result = run_phase337_forward_return_quality_tracker()
    print(f"\nPhase 337 Status: {result['status']}")
