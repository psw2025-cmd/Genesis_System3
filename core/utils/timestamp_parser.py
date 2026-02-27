"""
System3 Centralized Timestamp Parser

Single robust timestamp parser for all System3 components:
- Handles mixed formats (ISO, %d%b%Y, numeric timestamps)
- Returns clean datetime64[ns] with UTC normalization
- Logs parse failures for diagnostics
- Used by Phase 221, 304, 305, 239, and all enrichment pipelines

DRY-RUN ONLY: No trading flags touched.
"""

from __future__ import annotations

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Union, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_DIR = PROJECT_ROOT / "storage" / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = Path(__file__).parent / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "timestamp_parser.log"


def _log(msg: str) -> None:
    """Lightweight logger."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def _write_metrics(path: Path, payload: dict) -> None:
    """Write metrics JSON safely."""
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = json.loads(json.dumps(payload, default=str))
    with path.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)


def parse_timestamps(
    series: pd.Series,
    fallback_series: Optional[pd.Series] = None,
    name: str = "timestamp",
) -> pd.Series:
    """
    Robust timestamp parser with multiple format support.

    Args:
        series: Primary timestamp series to parse
        fallback_series: Optional fallback series if primary fails
        name: Column name for logging

    Returns:
        pd.Series: Parsed datetime64[ns] with NaT for unparseable values

    Strategies:
        1. Try mixed format (handles ISO, various string formats)
        2. Try DDmmmYYYY format (e.g., 02DEC2025)
        3. Try unix timestamp (numeric)
        4. Try fallback series if provided
        5. Forward/backward fill gaps
        6. Log remaining NaT count
    """
    parsed = pd.to_datetime(series, format="mixed", errors="coerce")
    initial_null = parsed.isna().sum()

    # Strategy 1: Mixed format already applied
    if parsed.isna().all():
        # Strategy 2: Try DDmmmYYYY format
        parsed = pd.to_datetime(series, format="%d%b%Y", errors="coerce")
        if not parsed.isna().all():
            _log(f"{name}: Parsed using %d%b%Y format")

    # Strategy 3: Try unix timestamp if still all NaN
    if parsed.isna().all():
        numeric = pd.to_numeric(series, errors="coerce")
        if not numeric.isna().all():
            parsed = pd.to_datetime(numeric, unit="s", errors="coerce")
            if not parsed.isna().all():
                _log(f"{name}: Parsed as unix timestamp")

    # Strategy 4: Fallback series
    if fallback_series is not None and parsed.isna().any():
        fallback_parsed = pd.to_datetime(fallback_series, format="mixed", errors="coerce")
        parsed = parsed.combine_first(fallback_parsed)
        healed = (fallback_parsed.notna() & parsed.notna()).sum()
        if healed > 0:
            _log(f"{name}: Filled {healed} NaT from fallback")

    # Strategy 5: Forward/backward fill
    if parsed.isna().any():
        before_fill = parsed.isna().sum()
        parsed = parsed.ffill().bfill()
        after_fill = parsed.isna().sum()
        if after_fill < before_fill:
            _log(f"{name}: Filled {before_fill - after_fill} NaT via ffill/bfill")

    # Final stats
    final_null = parsed.isna().sum()
    if final_null > 0:
        _log(f"{name}: WARNING - {final_null}/{len(parsed)} remain NaT after all strategies")
    elif initial_null > 0:
        _log(f"{name}: SUCCESS - healed all {initial_null} NaT values")

    return parsed


def parse_system3_timestamp(
    obj: Union[pd.Series, str, float, int, None],
    name: str = "ts",
    tz: str = "UTC",
    metrics_path: Optional[Path] = None,
    allow_fallback: Optional[pd.Series] = None,
    strict: bool = True,
) -> Union[pd.Series, pd.Timestamp, None]:
    """
    Canonical timestamp parser for System3 (metrics-aware, flexible fill mode).

    - Accepts Series or scalar.
    - Uses pandas mixed-format parsing with utc normalization to avoid inference warnings.
    - strict=True: does NOT fill NaT (for production pipelines).
    - strict=False: applies ffill/bfill for report generation (lenient mode).
    - Reports NaT rate via optional metrics file.
    """
    if isinstance(obj, pd.Series):
        parsed = pd.to_datetime(obj, format="mixed", errors="coerce", utc=True)
        if allow_fallback is not None:
            fallback_parsed = pd.to_datetime(allow_fallback, format="mixed", errors="coerce", utc=True)
            parsed = parsed.combine_first(fallback_parsed)

        # Apply lenient filling if strict=False (for reports)
        if not strict and parsed.isna().any():
            before_fill = parsed.isna().sum()
            parsed = parsed.ffill().bfill()
            after_fill = parsed.isna().sum()
            if after_fill < before_fill:
                _log(f"{name}: filled {before_fill - after_fill} NaT via ffill/bfill (lenient mode)")

        nat_count = int(parsed.isna().sum())
        total = len(parsed)
        metrics = {
            "name": name,
            "total": total,
            "nat_count": nat_count,
            "nat_rate": round(nat_count / total, 6) if total else 0.0,
            "utc": True,
            "strict": strict,
        }
        _log(f"{name}: parsed {total} rows, NaT {nat_count} ({metrics['nat_rate']*100:.2f}%), strict={strict}")
        if metrics_path:
            _write_metrics(metrics_path, metrics)
        return parsed

    # Scalar path
    parsed_scalar = pd.to_datetime([obj], format="mixed", errors="coerce", utc=True)
    return parsed_scalar[0]


def normalize_timestamp_column_strict(
    df: pd.DataFrame,
    col_name: str = "ts",
    fallback_col: Optional[str] = None,
    metrics_path: Optional[Path] = None,
    name: str = "ts",
) -> Tuple[pd.DataFrame, dict]:
    """
    Normalize a timestamp column using the canonical parser without forward/backfill.
    Returns dataframe copy and metrics dict.
    """
    df = df.copy()
    fallback_series = df[fallback_col] if fallback_col and fallback_col in df.columns else None
    if col_name not in df.columns and fallback_series is None:
        raise ValueError(f"Column {col_name} not found and no fallback available")

    target_series = df[col_name] if col_name in df.columns else fallback_series
    parsed = parse_system3_timestamp(
        target_series, name=name, metrics_path=metrics_path, allow_fallback=fallback_series
    )
    df[col_name] = parsed

    metrics = {
        "name": name,
        "total": int(len(df)),
        "nat_count": int(df[col_name].isna().sum()),
        "nat_rate": round(df[col_name].isna().mean(), 6) if len(df) else 0.0,
        "column": col_name,
    }
    if metrics_path:
        _write_metrics(metrics_path, metrics)
    return df, metrics


def normalize_timestamp_column_strict_enhanced(
    df: pd.DataFrame,
    col_name: str = "ts",
    fallback_col: Optional[str] = None,
    metrics_path: Optional[Path] = None,
    name: str = "enhanced_normalization",
) -> Tuple[pd.DataFrame, dict]:
    """
    Enhanced timestamp normalization with recovery mechanisms for NULL timestamps.
    Includes fallback column recovery and detailed logging.
    """
    df = df.copy()
    original_count = len(df)

    # Primary normalization
    df, primary_metrics = normalize_timestamp_column_strict(df, col_name, fallback_col, metrics_path, name)

    # Recovery for NULL timestamps
    null_mask = df[col_name].isna()
    if null_mask.any():
        # Attempt recovery from other columns
        recovery_cols = ["timestamp", "created_at", "signal_time"]
        for recovery_col in recovery_cols:
            if recovery_col in df.columns:
                recovered = df.loc[null_mask & df[recovery_col].notna(), recovery_col]
                if len(recovered) > 0:
                    # Parse the recovered values
                    parsed_recovered = parse_system3_timestamp(
                        recovered, name=f"{name}_recovery_{recovery_col}", metrics_path=None, allow_fallback=None
                    )
                    df.loc[recovered.index, col_name] = parsed_recovered
                    null_mask = df[col_name].isna()

        # Log recovery statistics
        recovered_count = original_count - len(df) + null_mask.sum()
        if recovered_count > 0:
            _log(f"{name}: Recovered {recovered_count} timestamps from fallback columns")

    # Enhanced metrics
    final_nat_count = int(df[col_name].isna().sum())
    enhanced_metrics = {
        "name": name,
        "total": int(len(df)),
        "original_total": original_count,
        "nat_count": final_nat_count,
        "nat_rate": round(final_nat_count / len(df), 6) if len(df) else 0.0,
        "column": col_name,
        "recovery_attempted": True,
        "primary_nat_count": primary_metrics["nat_count"],
        "recovered_count": primary_metrics["nat_count"] - final_nat_count,
    }

    if metrics_path:
        _write_metrics(metrics_path, enhanced_metrics)

    return df, enhanced_metrics


def normalize_timestamp_column(
    df: pd.DataFrame,
    col_name: str = "ts",
    fallback_col: Optional[str] = "timestamp",
) -> pd.DataFrame:
    """
    Normalize timestamp column in dataframe using robust parser.

    Args:
        df: DataFrame with timestamp column
        col_name: Primary timestamp column name
        fallback_col: Fallback column name if primary is NaT

    Returns:
        DataFrame with normalized timestamp column
    """
    df = df.copy()

    if col_name not in df.columns:
        if fallback_col and fallback_col in df.columns:
            df[col_name] = parse_timestamps(df[fallback_col], name=col_name)
        else:
            raise ValueError(f"Column {col_name} not found and no fallback available")
    else:
        fallback_series = df[fallback_col] if fallback_col and fallback_col in df.columns else None
        df[col_name] = parse_timestamps(df[col_name], fallback_series, name=col_name)

    return df


def write_iso_timestamps(series: pd.Series) -> pd.Series:
    """
    Convert datetime series to clean ISO strings (YYYY-MM-DD HH:MM:SS).

    Args:
        series: datetime64[ns] series

    Returns:
        pd.Series: ISO formatted strings
    """
    return pd.to_datetime(series, errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    # Self-test with various formats
    test_data = pd.DataFrame(
        {
            "ts_iso": ["2025-12-08 10:30:00", "2025-12-08T10:31:00.123456", None],
            "ts_dmy": ["08DEC2025", "09DEC2025", "10DEC2025"],
            "ts_unix": [1733655000, 1733655060, 1733655120],
        }
    )

    print("Testing ISO format:")
    result = parse_timestamps(test_data["ts_iso"], name="test_iso")
    print(result)

    print("\nTesting DDmmmYYYY format:")
    result = parse_timestamps(test_data["ts_dmy"], name="test_dmy")
    print(result)

    print("\nTesting unix timestamp:")
    result = parse_timestamps(test_data["ts_unix"], name="test_unix")
    print(result)
