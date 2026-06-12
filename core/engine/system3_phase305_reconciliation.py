"""
System3 Phase 305 - Forward Signal Reconciliation & Validation

Consumes healed forward signals (Phase 304) and produces reconciled output with:
- Guaranteed ts populated
- Normalized side
- Expiry filled using available metadata
- Invalid rows isolated to errors directory

Outputs: `dhan_index_ai_signals_reconciled.csv`
DRY-RUN ONLY: No trading flags touched.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)

FORWARD_CSV = STORAGE_LIVE / "dhan_index_ai_signals_with_forward.csv"
RECONCILED_CSV = STORAGE_LIVE / "dhan_index_ai_signals_reconciled.csv"
INVALID_CSV = STORAGE_LIVE / "errors" / "_invalid_reconciled_rows.csv"
REPORT_JSON = STORAGE_LIVE / "meta" / "phase305_reconcile_report.json"
INVALID_CSV.parent.mkdir(parents=True, exist_ok=True)
REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

# Reuse the side normalization logic from Phase 304
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
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with (LOG_DIR / "phase305_reconciliation.log").open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {message}\n")
    except Exception:
        pass


def _normalize_side(series: pd.Series) -> pd.Series:
    def map_side(val):
        raw = str(val).upper().strip()
        return SIDE_MAP.get(raw, "HOLD")

    return series.astype(str).apply(map_side)


def _fill_expiry(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["expiry"] = pd.to_datetime(df.get("expiry"), errors="coerce").dt.normalize()
    if "time_to_expiry" in df.columns:
        tte = pd.to_numeric(df["time_to_expiry"], errors="coerce")
        missing = df["expiry"].isna() & df["ts"].notna() & tte.notna()
        if missing.any():
            df.loc[missing, "expiry"] = df.loc[missing, "ts"] + pd.to_timedelta(
                tte[missing].apply(lambda x: int(x) + 1), unit="D"
            )
    return df


def run_phase305(**kwargs: Any) -> Dict[str, Any]:
    errors: List[str] = []
    try:
        if not FORWARD_CSV.exists():
            return {
                "phase": 305,
                "status": "WARN",
                "details": "Forward CSV not found (run Phase 304 first)",
                "outputs": {},
                "errors": [],
            }
        df = pd.read_csv(FORWARD_CSV, engine="python", on_bad_lines="skip")
        original_rows = len(df)
        _log(f"Loaded {original_rows} rows for reconciliation")

        df["ts"] = pd.to_datetime(df.get("ts"), errors="coerce")
        df["side"] = _normalize_side(df.get("side", pd.Series(["HOLD"] * len(df))))
        df = _fill_expiry(df)

        invalid_mask = df["ts"].isna() | df["expiry"].isna()
        invalid_rows = df[invalid_mask].copy()
        if len(invalid_rows) > 0:
            invalid_rows.to_csv(INVALID_CSV, index=False)
            errors.append(f"Isolated {len(invalid_rows)} invalid rows to {INVALID_CSV.name}")

        df_valid = df[~invalid_mask].copy()
        df_valid.to_csv(RECONCILED_CSV, index=False)
        _log(f"Saved reconciled signals to {RECONCILED_CSV}")

        expiry_missing = int(df_valid["expiry"].isna().sum())
        ts_missing = int(df_valid["ts"].isna().sum())
        side_counts = df_valid["side"].value_counts(dropna=False).to_dict()

        report = {
            "phase": 305,
            "timestamp": datetime.now().isoformat(),
            "input_rows": original_rows,
            "output_rows": int(len(df_valid)),
            "invalid_rows": int(len(invalid_rows)),
            "ts_missing": ts_missing,
            "expiry_missing": expiry_missing,
            "side_counts": side_counts,
            "notes": errors,
        }
        with REPORT_JSON.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        status = "OK" if ts_missing == 0 and expiry_missing == 0 else "WARN"
        details = f"Reconciled {len(df_valid)} rows, invalid {len(invalid_rows)}"
        return {
            "phase": 305,
            "status": status,
            "details": details,
            "outputs": {
                "reconciled_file": str(RECONCILED_CSV),
                "invalid_file": str(INVALID_CSV),
                "report_json": str(REPORT_JSON),
            },
            "errors": errors,
        }

    except Exception as exc:  # pragma: no cover - defensive
        errors.append(str(exc))
        _log(f"ERROR: {exc}")
        return {
            "phase": 305,
            "status": "ERROR",
            "details": f"Exception: {exc}",
            "outputs": {},
            "errors": errors,
        }


if __name__ == "__main__":
    result = run_phase305()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
