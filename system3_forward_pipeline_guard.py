"""
System3 Forward Pipeline Guard

Pre-flight validation for forward signals before Phase 239:
- Checks ts/expiry/side completeness
- Applies lightweight auto-heal (ts from timestamp, side normalization, expiry from time_to_expiry)
- Emits forward_signals_health.json
- Non-fatal: returns status + warnings without throwing
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd

ROOT = Path(__file__).parent
STORAGE_LIVE = ROOT / "storage" / "live"
FORWARD_CSV = STORAGE_LIVE / "angel_index_ai_signals_with_forward.csv"
HEALTH_JSON = STORAGE_LIVE / "meta" / "forward_signals_health.json"
HEALTH_JSON.parent.mkdir(parents=True, exist_ok=True)
LOG_PATH = ROOT / "logs" / "research" / "forward_pipeline_guard.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

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


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def _normalize_side(series: pd.Series) -> pd.Series:
    def mapper(val):
        raw = str(val).upper().strip()
        return SIDE_MAP.get(raw, "HOLD")
    return series.astype(str).apply(mapper)


def run_guard(auto_heal: bool = True) -> Dict[str, Any]:
    errors: List[str] = []
    if not FORWARD_CSV.exists():
        status = "ERROR"
        details = "Forward CSV missing"
        payload = {
            "status": status,
            "details": details,
            "ts_missing": None,
            "expiry_missing": None,
            "side_counts": {},
        }
        with HEALTH_JSON.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return payload

    try:
        df = pd.read_csv(FORWARD_CSV, engine="python", on_bad_lines="skip")
        original_rows = len(df)
        df["ts"] = pd.to_datetime(df.get("ts"), errors="coerce")
        if auto_heal and df["ts"].isna().any() and "timestamp" in df.columns:
            healed = pd.to_datetime(df.loc[df["ts"].isna(), "timestamp"], errors="coerce")
            df.loc[df["ts"].isna(), "ts"] = healed
            _log(f"Auto-healed ts from timestamp for {healed.notna().sum()} rows")
        if auto_heal and df["ts"].isna().any():
            df["ts"] = df["ts"].ffill().bfill()

        df["side"] = _normalize_side(df.get("side", pd.Series(["HOLD"] * len(df))))

        df["expiry"] = pd.to_datetime(df.get("expiry"), errors="coerce").dt.normalize()
        if auto_heal and "time_to_expiry" in df.columns:
            tte = pd.to_numeric(df["time_to_expiry"], errors="coerce")
            mask = df["expiry"].isna() & df["ts"].notna() & tte.notna()
            if mask.any():
                df.loc[mask, "expiry"] = df.loc[mask, "ts"] + pd.to_timedelta(tte[mask].apply(lambda x: math.ceil(x)), unit="D")
                _log(f"Filled expiry from time_to_expiry for {mask.sum()} rows")

        ts_missing = int(df["ts"].isna().sum())
        expiry_missing = int(df["expiry"].isna().sum())
        side_counts = df["side"].value_counts(dropna=False).to_dict()

        status = "OK" if ts_missing == 0 and expiry_missing / max(len(df), 1) < 0.02 else "WARN"
        details = f"Forward signals health: ts_missing={ts_missing}, expiry_missing={expiry_missing}"

        payload = {
            "status": status,
            "details": details,
            "ts_missing": ts_missing,
            "expiry_missing": expiry_missing,
            "rows": original_rows,
            "side_counts": side_counts,
            "auto_heal": auto_heal,
            "timestamp": datetime.now().isoformat(),
        }

        with HEALTH_JSON.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        if auto_heal:
            df.to_csv(FORWARD_CSV, index=False)
            _log("Forward CSV rewritten after guard auto-heal")

        return payload

    except Exception as exc:  # pragma: no cover
        errors.append(str(exc))
        payload = {
            "status": "ERROR",
            "details": f"Guard failed: {exc}",
            "errors": errors,
        }
        with HEALTH_JSON.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return payload


if __name__ == "__main__":
    result = run_guard()
    print(json.dumps(result, indent=2))
