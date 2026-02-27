"""
System3 Phase 304 - Forward Signal Repair & Timestamp Healer

Purpose:
- Guarantee populated `ts` for all forward signals (no blanks).
- Normalize `side` to BUY/SELL/HOLD (handles CE/PE/0 and option-type hints).
- Fill `expiry` using available metadata (time_to_expiry + ts) when missing.
- Isolate unrecoverable rows to `_invalid_forward_rows.csv` for transparency.
- Preserve existing forward return columns.

DRY-RUN ONLY: No trading flags touched.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)

FORWARD_INPUT = STORAGE_LIVE / "angel_index_ai_signals_with_forward.csv"
CURATED_INPUT = STORAGE_LIVE / "angel_index_ai_signals_curated.csv"
OUTPUT_CSV = FORWARD_INPUT  # overwrite in-place after healing
INVALID_CSV = STORAGE_LIVE / "errors" / "_invalid_forward_rows.csv"
REPORT_JSON = STORAGE_LIVE / "meta" / "phase304_heal_report.json"
REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
INVALID_CSV.parent.mkdir(parents=True, exist_ok=True)

SIDE_MAP = {
    "BUY": "BUY",
    "SELL": "SELL",
    "HOLD": "HOLD",
    "CE": "BUY",
    "PE": "SELL",
    "CALL": "BUY",
    "PUT": "SELL",
    "C": "BUY",
    "P": "SELL",
    "1": "BUY",
    "-1": "SELL",
    "0": "HOLD",
}


def _log(message: str) -> None:
    """Lightweight file logger."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with (LOG_DIR / "phase304_forward_heal.log").open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {message}\n")
    except Exception:
        pass


def _load_forward_source() -> pd.DataFrame:
    """Load forward signals from curated if available else forward file."""
    if CURATED_INPUT.exists():
        path = CURATED_INPUT
    elif FORWARD_INPUT.exists():
        path = FORWARD_INPUT
    else:
        raise FileNotFoundError("No forward signals source found")
    return pd.read_csv(path, engine="python", on_bad_lines="skip")


def _ensure_ts(df: pd.DataFrame, errors: List[str]) -> pd.DataFrame:
    """Guarantee ts is populated for all rows."""
    df = df.copy()
    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    else:
        df["ts"] = pd.NaT
        errors.append("ts column missing - created empty ts column")

    if "timestamp" in df.columns:
        ts_from_stamp = pd.to_datetime(df["timestamp"], errors="coerce")
        df.loc[df["ts"].isna(), "ts"] = ts_from_stamp[df["ts"].isna()]
        healed = df["ts"].notna().sum()
        _log(f"Healed ts from timestamp for {healed} rows")

    # Fill remaining NaN using monotonic sequence (prev + 1s)
    if df["ts"].isna().any():
        # Forward/back-fill using existing valid values
        df["ts"] = df["ts"].ffill().bfill()
        # For any still NaN (all-NaN case), build synthetic timeline
        if df["ts"].isna().any():
            start = datetime.now()
            df.loc[df["ts"].isna(), "ts"] = [start + timedelta(seconds=i) for i in range(df["ts"].isna().sum())]
            errors.append("Synthetic ts assigned for rows with no timestamp context")

    # Final guarantee: no NaN
    if df["ts"].isna().any():
        missing = int(df["ts"].isna().sum())
        errors.append(f"FAILED to fill ts for {missing} rows")
    return df


def _normalize_side(df: pd.DataFrame, errors: List[str]) -> pd.DataFrame:
    """Normalize side column to BUY/SELL/HOLD using SIDE_MAP and option_type hints."""
    df = df.copy()
    if "side" not in df.columns:
        df["side"] = "HOLD"
        errors.append("side column missing - defaulted to HOLD")

    # Option-type hints
    option_hint = df.get("option_type")
    if option_hint is not None:
        option_hint = option_hint.astype(str).str.upper()

    def map_side(val, hint=None):
        raw = str(val).upper().strip()
        if raw in SIDE_MAP:
            return SIDE_MAP[raw]
        if hint in SIDE_MAP:
            return SIDE_MAP[hint]
        return "HOLD"

    df["side"] = [
        map_side(s, h if option_hint is not None else None)
        for s, h in zip(df["side"], option_hint if option_hint is not None else [None] * len(df))
    ]

    invalid = df[~df["side"].isin(["BUY", "SELL", "HOLD"])]
    if not invalid.empty:
        errors.append(f"Invalid side values coerced to HOLD: {invalid['side'].unique().tolist()}")
        df.loc[~df["side"].isin(["BUY", "SELL", "HOLD"]), "side"] = "HOLD"
    return df


def _fill_expiry(df: pd.DataFrame, errors: List[str]) -> pd.DataFrame:
    """Fill expiry using time_to_expiry + ts where missing."""
    df = df.copy()
    if "expiry" not in df.columns:
        df["expiry"] = pd.NaT
        errors.append("expiry column missing - created empty expiry column")

    if "time_to_expiry" in df.columns:
        tte = pd.to_numeric(df["time_to_expiry"], errors="coerce")
        candidates = df["expiry"].isna() & df["ts"].notna() & tte.notna()
        if candidates.any():
            # Interpret tte as days; use ceiling to be conservative
            days = tte[candidates].apply(lambda x: math.ceil(x) if pd.notna(x) else None)
            df.loc[candidates, "expiry"] = df.loc[candidates, "ts"] + pd.to_timedelta(days, unit="D")

    # Normalize expiry to date (no time component)
    df["expiry"] = pd.to_datetime(df["expiry"], errors="coerce").dt.normalize()
    return df


def _write_invalid_rows(df: pd.DataFrame, errors: List[str]) -> int:
    """Persist unrecoverable rows and return count."""
    invalid_mask = df["expiry"].isna() | df["ts"].isna()
    invalid_rows = df[invalid_mask].copy()
    count = len(invalid_rows)
    if count > 0:
        INVALID_CSV.parent.mkdir(parents=True, exist_ok=True)
        invalid_rows.to_csv(INVALID_CSV, index=False)
        errors.append(f"Isolated {count} invalid rows to {INVALID_CSV.name}")
    return count


def run_phase304(**kwargs: Any) -> Dict[str, Any]:
    """Execute Phase 304 forward signal repair."""
    errors: List[str] = []
    try:
        df = _load_forward_source()
        original_rows = len(df)
        _log(f"Loaded {original_rows} rows for repair")

        df = _ensure_ts(df, errors)
        df = _normalize_side(df, errors)
        df = _fill_expiry(df, errors)

        invalid_count = _write_invalid_rows(df, errors)

        # Drop invalid rows from main output (keep record separately)
        df_valid = df[~(df["expiry"].isna() | df["ts"].isna())].copy()

        # Save healed dataset
        df_valid.to_csv(OUTPUT_CSV, index=False)
        _log(f"Saved healed forward signals to {OUTPUT_CSV}")

        expiry_missing = int(df_valid["expiry"].isna().sum()) if "expiry" in df_valid.columns else len(df_valid)
        ts_missing = int(df_valid["ts"].isna().sum())
        side_counts = df_valid["side"].value_counts(dropna=False).to_dict() if "side" in df_valid.columns else {}

        report = {
            "phase": 304,
            "timestamp": datetime.now().isoformat(),
            "input_rows": original_rows,
            "output_rows": int(len(df_valid)),
            "invalid_rows": int(invalid_count),
            "ts_missing": ts_missing,
            "expiry_missing": expiry_missing,
            "side_counts": side_counts,
            "notes": errors,
        }
        with REPORT_JSON.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        status = "OK" if ts_missing == 0 and expiry_missing / max(len(df_valid), 1) < 0.02 else "WARN"
        details = f"Healed forward signals: {len(df_valid)} rows, invalid {invalid_count}"
        if ts_missing > 0:
            status = "ERROR"
            details = "ts still missing after healing"
        return {
            "phase": 304,
            "status": status,
            "details": details,
            "outputs": {
                "output_file": str(OUTPUT_CSV),
                "invalid_file": str(INVALID_CSV),
                "report_json": str(REPORT_JSON),
            },
            "errors": errors,
        }

    except Exception as exc:  # pragma: no cover - defensive guard
        errors.append(str(exc))
        _log(f"ERROR: {exc}")
        return {
            "phase": 304,
            "status": "ERROR",
            "details": f"Exception: {exc}",
            "outputs": {},
            "errors": errors,
        }


if __name__ == "__main__":
    result = run_phase304()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
