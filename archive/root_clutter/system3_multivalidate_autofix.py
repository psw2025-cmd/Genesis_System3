#!/usr/bin/env python
"""
SYSTEM3 Laptop – Multivalidate Auto-Fix

Fixes two concrete issues detected by system3_multivalidate_report.json:

1) If storage/live/forward/phase221_forward_returns.csv is missing but
   phase220_aggregated_signals.csv exists, try to regenerate it by calling
   system3_production_pipeline_clean.py (which already orchestrates
   Phase 220 → 221 → 239).

2) If storage/live/enriched/angel_virtual_orders_with_pnl.csv exists but
   does NOT contain the 'symbol' column, try to patch it by merging in the
   'symbol' column from storage/live/angel_virtual_orders.csv using common
   merge keys (ts, underlying, expiry, strike, side, token where available).

Outputs a summary JSON:
   storage/live/meta/system3_multivalidate_autofix_report.json
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
except Exception as e:
    print("[ERROR] pandas not available in venv:", repr(e))
    sys.exit(1)


ROOT = Path(__file__).resolve().parent
STORAGE_LIVE = ROOT / "storage" / "live"
FORWARD_DIR = STORAGE_LIVE / "forward"
ENRICHED_DIR = STORAGE_LIVE / "enriched"
META_DIR = STORAGE_LIVE / "meta"

PHASE220_PATH = FORWARD_DIR / "phase220_aggregated_signals.csv"
PHASE221_PATH = FORWARD_DIR / "phase221_forward_returns.csv"
ENRICHED_PNL_PATH = ENRICHED_DIR / "angel_virtual_orders_with_pnl.csv"
RAW_ORDERS_PATH = STORAGE_LIVE / "angel_virtual_orders.csv"

PIPELINE_SCRIPT = ROOT / "system3_production_pipeline_clean.py"

VENV_PY = ROOT / "venv" / "Scripts" / "python.exe"
if not VENV_PY.exists():
    # fallback to current interpreter if venv python not found
    VENV_PY = Path(sys.executable)


def ensure_dirs():
    META_DIR.mkdir(parents=True, exist_ok=True)


def regenerate_phase221():
    """
    Ensure phase221_forward_returns.csv exists.
    If missing and phase220 exists, call system3_production_pipeline_clean.py.
    """
    status = {
        "name": "phase221_forward_returns",
        "exists_before": PHASE221_PATH.exists(),
        "phase220_exists": PHASE220_PATH.exists(),
        "pipeline_called": False,
        "pipeline_exit_code": None,
        "exists_after": None,
        "error": None,
        "path": str(PHASE221_PATH),
    }

    if PHASE221_PATH.exists():
        status["action"] = "none_already_exists"
        status["exists_after"] = True
        return status

    if not PHASE220_PATH.exists():
        status["action"] = "error_no_phase220"
        status["error"] = (
            "phase220_aggregated_signals.csv not found; cannot regenerate phase221."
        )
        status["exists_after"] = False
        return status

    if not PIPELINE_SCRIPT.exists():
        status["action"] = "error_no_pipeline_script"
        status["error"] = (
            f"{PIPELINE_SCRIPT.name} not found; cannot regenerate phase221."
        )
        status["exists_after"] = False
        return status

    try:
        print("[INFO] Regenerating Phase 221 via system3_production_pipeline_clean.py")
        status["pipeline_called"] = True
        code = subprocess.call(
            [str(VENV_PY), str(PIPELINE_SCRIPT)],
            cwd=str(ROOT),
        )
        status["pipeline_exit_code"] = int(code)
    except Exception as e:
        status["error"] = f"Pipeline call failed: {repr(e)}"

    status["exists_after"] = PHASE221_PATH.exists()
    if not status["exists_after"] and status["error"] is None:
        status["error"] = "Pipeline ran but phase221_forward_returns.csv still missing."

    if status["exists_after"]:
        status["action"] = "regenerated_via_pipeline"
    else:
        if status["action"] is None:
            status["action"] = "regeneration_failed"

    return status


def patch_symbol_on_enriched():
    """
    Ensure angel_virtual_orders_with_pnl.csv contains 'symbol' column.

    Only patch if safe merge keys exist (excluding 'side').
    """
    enriched_path = ENRICHED_DIR / "angel_virtual_orders_with_pnl.csv"
    raw_orders_path = STORAGE_LIVE / "angel_virtual_orders.csv"

    result = {
        "name": "angel_virtual_orders_with_pnl_symbol",
        "enriched_exists": enriched_path.exists(),
        "raw_orders_exists": raw_orders_path.exists(),
        "had_symbol_before": False,
        "action": None,
        "rows": None,
        "cols_before": None,
        "cols_after": None,
        "merge_keys_used": [],
        "symbol_filled_count": 0,
        "error": None,
        "path": str(enriched_path),
    }

    if not enriched_path.exists():
        result["action"] = "enriched_missing"
        result["error"] = "enriched PnL file not found"
        return result

    try:
        df_enriched = pd.read_csv(enriched_path)
        result["rows"] = len(df_enriched)
        result["cols_before"] = df_enriched.shape[1]
        result["had_symbol_before"] = bool(("symbol" in df_enriched.columns) and df_enriched["symbol"].notna().any())

        if "symbol" not in df_enriched.columns:
            df_enriched["symbol"] = pd.NA

        if not raw_orders_path.exists():
            result["action"] = "symbol_source_missing"
            result["error"] = "angel_virtual_orders.csv not found"
            result["cols_after"] = df_enriched.shape[1]
            result["symbol_filled_count"] = int(df_enriched["symbol"].notna().sum())
            df_enriched.to_csv(enriched_path, index=False)
            return result

        df_raw = pd.read_csv(raw_orders_path)

        if "symbol" not in df_raw.columns:
            result["action"] = "symbol_source_missing"
            result["error"] = "raw orders file has no 'symbol' column"
            result["cols_after"] = df_enriched.shape[1]
            result["symbol_filled_count"] = int(df_enriched["symbol"].notna().sum())
            df_enriched.to_csv(enriched_path, index=False)
            return result

        candidate_keys = [
            "order_id", "timestamp", "ts",
            "underlying", "expiry", "strike",
            "side", "token",
        ]

        enriched_cols = set(df_enriched.columns)
        raw_cols = set(df_raw.columns)
        common_keys = [k for k in candidate_keys if k in enriched_cols and k in raw_cols]

        safe_keys = [k for k in common_keys if k != "side"]

        if not safe_keys:
            result["action"] = "symbol_not_filled_no_safe_keys"
            result["merge_keys_used"] = []
            result["error"] = "No safe merge keys between enriched PnL and raw orders (only 'side' overlaps). Cannot auto-fill symbol."
            result["cols_after"] = df_enriched.shape[1]
            result["symbol_filled_count"] = int(df_enriched["symbol"].notna().sum())
            df_enriched.to_csv(enriched_path, index=False)
            return result

        # safe_keys exist
        df_raw_small = df_raw[safe_keys + ["symbol"]].drop_duplicates()
        before_non_null = int(df_enriched["symbol"].notna().sum())

        df_merged = df_enriched.merge(
            df_raw_small,
            how="left",
            on=safe_keys,
            suffixes=("", "_src"),
        )

        if "symbol_src" in df_merged.columns:
            mask = df_merged["symbol"].isna() & df_merged["symbol_src"].notna()
            df_merged.loc[mask, "symbol"] = df_merged.loc[mask, "symbol_src"]
            df_merged.drop(columns=["symbol_src"], inplace=True)

        after_non_null = int(df_merged["symbol"].notna().sum())
        df_merged.to_csv(enriched_path, index=False)

        result["cols_after"] = df_merged.shape[1]
        result["merge_keys_used"] = safe_keys
        result["symbol_filled_count"] = after_non_null

        if after_non_null > before_non_null:
            result["action"] = "patched_symbol"
        else:
            result["action"] = "symbol_not_filled_even_with_safe_keys"
            result["error"] = "Merge completed but did not increase non-null symbols"

        return result

    except Exception as e:
        result["action"] = "symbol_patch_exception"
        result["error"] = repr(e)
        result["cols_after"] = df_enriched.shape[1] if 'df_enriched' in locals() else None
        result["symbol_filled_count"] = int(df_enriched["symbol"].notna().sum()) if 'df_enriched' in locals() else 0
        if 'df_enriched' in locals():
            df_enriched.to_csv(enriched_path, index=False)
        return result


def main():
    ensure_dirs()
    report = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "root": str(ROOT),
        "steps": {},
    }

    print("=== SYSTEM3 MULTIVALIDATE AUTOFIX (Laptop Case-1) ===")
    print(f"Root: {ROOT}")

    # Step 1: phase221 regeneration
    print("\n[STEP 1] Ensure phase221_forward_returns.csv exists")
    step1 = regenerate_phase221()
    report["steps"]["phase221_regeneration"] = step1
    print("  →", step1)

    # Step 2: symbol patch on enriched PnL file
    print("\n[STEP 2] Ensure 'symbol' column exists on angel_virtual_orders_with_pnl.csv")
    step2 = patch_symbol_on_enriched()
    report["steps"]["enriched_symbol_patch"] = step2
    print("  →", step2)

    # Save summary JSON
    out_path = META_DIR / "system3_multivalidate_autofix_report.json"
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\n[INFO] Auto-fix report written to: {out_path}")
    except Exception as e:
        print("[ERROR] Could not write autofix report:", repr(e))

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
