#!/usr/bin/env python
"""
SYSTEM3 MULTI-VALIDATE MASTER (CASE 1 LAPTOP)

Read-only auditor for:
- Core file presence
- CSV schema / header integrity
- Timestamp consistency (tz-naive vs tz-aware, NaT rate)
- Merge-key alignment between forward returns and virtual orders
- Forward-return feature coverage (fwd_ret_*)
- Basic model-feature coverage

Outputs:
- Human-readable summary to console
- JSON report at: storage/live/meta/system3_multivalidate_report.json

Does NOT modify any files. Safe to run anytime (market or off-market).
"""

import os
import sys
import json
import glob
import traceback
from datetime import datetime
from textwrap import indent

import pandas as pd
import numpy as np


ROOT = os.path.dirname(os.path.abspath(__file__))


def print_section(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def safe_load_csv(path: str, nrows: int | None = None) -> tuple[pd.DataFrame | None, str | None]:
    if not os.path.exists(path):
        return None, f"File not found: {path}"
    try:
        df = pd.read_csv(path, nrows=nrows)
        return df, None
    except Exception as e:
        return None, f"Error loading {path}: {repr(e)}"


def safe_glob(pattern: str) -> list[str]:
    return sorted(glob.glob(pattern))


def describe_dtype(series: pd.Series) -> str:
    dtype = str(series.dtype)
    return dtype


def check_environment():
    print_section("CHECK 1: ENVIRONMENT & CORE DEPENDENCIES")
    result = {
        "root": ROOT,
        "storage_exists": os.path.isdir(os.path.join(ROOT, "storage")),
        "deps_ok": True,
        "missing_deps": [],
    }

    print(f"Project root: {ROOT}")
    print(f"storage/ present: {result['storage_exists']}")

    missing = []
    for mod in ["pandas", "numpy"]:
        try:
            __import__(mod)
        except Exception as e:
            missing.append((mod, repr(e)))

    if missing:
        result["deps_ok"] = False
        result["missing_deps"] = missing
        print("Dependencies: MISSING")
        for name, err in missing:
            print(f"  - {name}: {err}")
    else:
        print("Dependencies: OK (pandas, numpy import succeeded)")

    return result


def check_file_presence():
    print_section("CHECK 2: CRITICAL FILE PRESENCE")

    paths = {
        "phase220_aggregated_signals": os.path.join(ROOT, "storage", "live", "forward", "phase220_aggregated_signals.csv"),
        "phase221_forward_returns": os.path.join(ROOT, "storage", "live", "forward", "phase221_forward_returns.csv"),
        "angel_virtual_orders_with_pnl": os.path.join(ROOT, "storage", "live", "enriched", "angel_virtual_orders_with_pnl.csv"),
    }

    report = {}
    for key, path in paths.items():
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        report[key] = {"path": path, "exists": exists, "size_bytes": int(size)}
        print(f"{key}: exists={exists}, size={size} bytes, path={path}")

    # Also capture latest pipeline execution report if present
    meta_dir = os.path.join(ROOT, "storage", "live", "meta")
    pipeline_reports = safe_glob(os.path.join(meta_dir, "pipeline_execution_report_*.json"))
    latest_pipeline_report = pipeline_reports[-1] if pipeline_reports else None
    report["latest_pipeline_report"] = latest_pipeline_report
    print(f"Latest pipeline report JSON: {latest_pipeline_report}")

    return report


def validate_csv_schema():
    print_section("CHECK 3: CSV SCHEMA / HEADER INTEGRITY")

    phase221_path = os.path.join(ROOT, "storage", "live", "forward", "phase221_forward_returns.csv")
    orders_path = os.path.join(ROOT, "storage", "live", "enriched", "angel_virtual_orders_with_pnl.csv")

    schema_report: dict[str, dict] = {}

    # Phase 221
    df221, err221 = safe_load_csv(phase221_path)
    if df221 is None:
        print(f"Phase221: ERROR - {err221}")
        schema_report["phase221_forward_returns"] = {
            "path": phase221_path,
            "loaded": False,
            "error": err221,
        }
    else:
        print(f"Phase221: loaded shape={df221.shape}")
        required_cols_221 = [
            "underlying",
            "expiry",
            "strike",
            "side",
            "symbol",
            "ts",
            "fwd_ret_1",
            "fwd_ret_2",
            "fwd_ret_5",
            "fwd_ret_10",
            "fwd_ret_15",
        ]
        missing = [c for c in required_cols_221 if c not in df221.columns]
        print("Phase221 columns sample (first 15):")
        print("  " + ", ".join(df221.columns[:15]))
        if missing:
            print("Phase221 missing required columns:")
            for m in missing:
                print(f"  - {m}")
        else:
            print("Phase221: all required columns present.")
        schema_report["phase221_forward_returns"] = {
            "path": phase221_path,
            "loaded": True,
            "shape": list(df221.shape),
            "num_columns": int(len(df221.columns)),
            "missing_required": missing,
        }

    # Orders with PnL
    df_orders, err_orders = safe_load_csv(orders_path)
    if df_orders is None:
        print(f"Virtual orders: ERROR - {err_orders}")
        schema_report["angel_virtual_orders_with_pnl"] = {
            "path": orders_path,
            "loaded": False,
            "error": err_orders,
        }
    else:
        print(f"Virtual orders: loaded shape={df_orders.shape}")
        required_cols_orders = [
            "underlying",
            "expiry",
            "strike",
            "side",
            "symbol",
            "ts",
            "lots",
        ]
        missing_o = [c for c in required_cols_orders if c not in df_orders.columns]
        print("Virtual orders columns sample (first 15):")
        print("  " + ", ".join(df_orders.columns[:15]))
        if missing_o:
            print("Virtual orders missing required columns:")
            for m in missing_o:
                print(f"  - {m}")
        else:
            print("Virtual orders: all required columns present.")
        schema_report["angel_virtual_orders_with_pnl"] = {
            "path": orders_path,
            "loaded": True,
            "shape": list(df_orders.shape),
            "num_columns": int(len(df_orders.columns)),
            "missing_required": missing_o,
        }

    # Compare header overlaps if both loaded
    if df221 is not None and df_orders is not None:
        common = sorted(set(df221.columns) & set(df_orders.columns))
        only_221 = sorted(set(df221.columns) - set(df_orders.columns))
        only_orders = sorted(set(df_orders.columns) - set(df221.columns))

        print("Common columns between Phase221 and Virtual Orders:")
        print("  " + ", ".join(common[:20]) + ("..." if len(common) > 20 else ""))
        print(f"Columns only in Phase221: {len(only_221)}")
        print(f"Columns only in Virtual Orders: {len(only_orders)}")

        schema_report["header_comparison"] = {
            "common_columns_count": int(len(common)),
            "phase221_only_count": int(len(only_221)),
            "orders_only_count": int(len(only_orders)),
            "common_columns_sample": common[:30],
        }

    return schema_report


def validate_timestamps(df: pd.DataFrame, name: str) -> dict:
    res = {
        "name": name,
        "ts_column_present": "ts" in df.columns,
        "ts_dtype": None,
        "ts_nat_count": None,
        "ts_nat_rate": None,
        "timestamp_column_present": "timestamp" in df.columns,
        "timestamp_dtype": None,
        "timestamp_nat_count": None,
        "timestamp_nat_rate": None,
        "notes": [],
    }

    if "ts" in df.columns:
        s = df["ts"]
        res["ts_dtype"] = describe_dtype(s)
        parsed = pd.to_datetime(s, errors="coerce", utc=False)
        nat_count = int(parsed.isna().sum())
        total = int(len(parsed))
        res["ts_nat_count"] = nat_count
        res["ts_nat_rate"] = float(nat_count / total) if total > 0 else None
        if "datetime64[ns, UTC]" in str(parsed.dtype):
            res["notes"].append("ts parsed as tz-aware (UTC).")
        if nat_count > 0:
            res["notes"].append(f"ts has {nat_count} NaT entries.")

    if "timestamp" in df.columns:
        s2 = df["timestamp"]
        res["timestamp_dtype"] = describe_dtype(s2)
        parsed2 = pd.to_datetime(s2, errors="coerce", utc=False)
        nat2 = int(parsed2.isna().sum())
        tot2 = int(len(parsed2))
        res["timestamp_nat_count"] = nat2
        res["timestamp_nat_rate"] = float(nat2 / tot2) if tot2 > 0 else None
        if nat2 > 0:
            res["notes"].append(f"timestamp has {nat2} NaT entries.")

    return res


def check_timestamp_consistency():
    print_section("CHECK 4: TIMESTAMP CONSISTENCY (ts / timestamp)")

    phase221_path = os.path.join(ROOT, "storage", "live", "forward", "phase221_forward_returns.csv")
    orders_path = os.path.join(ROOT, "storage", "live", "enriched", "angel_virtual_orders_with_pnl.csv")

    report: dict[str, dict] = {}

    df221, err221 = safe_load_csv(phase221_path)
    if df221 is not None:
        rep221 = validate_timestamps(df221, "phase221_forward_returns")
        report["phase221_forward_returns"] = rep221
        print(f"phase221_forward_returns: ts_present={rep221['ts_column_present']}, "
              f"ts_dtype={rep221['ts_dtype']}, ts_NaT={rep221['ts_nat_count']}")
    else:
        print(f"Phase221 timestamp check skipped: {err221}")
        report["phase221_forward_returns"] = {"error": err221}

    df_orders, err_orders = safe_load_csv(orders_path)
    if df_orders is not None:
        rep_o = validate_timestamps(df_orders, "angel_virtual_orders_with_pnl")
        report["angel_virtual_orders_with_pnl"] = rep_o
        print(f"angel_virtual_orders_with_pnl: ts_present={rep_o['ts_column_present']}, "
              f"ts_dtype={rep_o['ts_dtype']}, ts_NaT={rep_o['ts_nat_count']}")
    else:
        print(f"Virtual orders timestamp check skipped: {err_orders}")
        report["angel_virtual_orders_with_pnl"] = {"error": err_orders}

    # Compare ts parsed dtype if both available
    if df221 is not None and df_orders is not None and "ts" in df221.columns and "ts" in df_orders.columns:
        s1 = pd.to_datetime(df221["ts"], errors="coerce", utc=False)
        s2 = pd.to_datetime(df_orders["ts"], errors="coerce", utc=False)
        dtype1 = str(s1.dtype)
        dtype2 = str(s2.dtype)
        same_type = dtype1 == dtype2
        print(f"Parsed ts dtype phase221={dtype1}, orders={dtype2}, same_type={same_type}")
        report["ts_dtype_comparison"] = {
            "phase221_ts_dtype": dtype1,
            "orders_ts_dtype": dtype2,
            "same_type": same_type,
        }

    return report


def check_merge_key_alignment():
    print_section("CHECK 5: MERGE-KEY ALIGNMENT (FORWARD vs VIRTUAL ORDERS)")

    phase221_path = os.path.join(ROOT, "storage", "live", "forward", "phase221_forward_returns.csv")
    orders_path = os.path.join(ROOT, "storage", "live", "enriched", "angel_virtual_orders_with_pnl.csv")

    df221, err221 = safe_load_csv(phase221_path)
    df_orders, err_orders = safe_load_csv(orders_path)

    report: dict[str, object] = {}

    if df221 is None or df_orders is None:
        print("Merge-key alignment skipped: at least one CSV missing or unreadable.")
        report["error"] = {
            "phase221_error": err221,
            "orders_error": err_orders,
        }
        return report

    keys = ["underlying", "expiry", "strike", "side", "ts"]
    missing_221 = [k for k in keys if k not in df221.columns]
    missing_o = [k for k in keys if k not in df_orders.columns]

    if missing_221 or missing_o:
        print("Merge-key alignment: required merge keys missing.")
        print(f"  Missing in phase221: {missing_221}")
        print(f"  Missing in orders: {missing_o}")
        report["missing_keys"] = {
            "phase221_missing": missing_221,
            "orders_missing": missing_o,
        }
        return report

    # Coerce to comparable dtypes for join keys
    df1 = df221.copy()
    df2 = df_orders.copy()

    for col in ["underlying", "side", "symbol"]:
        if col in df1.columns:
            df1[col] = df1[col].astype(str)
        if col in df2.columns:
            df2[col] = df2[col].astype(str)

    for col in ["expiry"]:
        if col in df1.columns:
            df1[col] = df1[col].astype(str)
        if col in df2.columns:
            df2[col] = df2[col].astype(str)

    for col in ["strike"]:
        if col in df1.columns:
            df1[col] = pd.to_numeric(df1[col], errors="coerce")
        if col in df2.columns:
            df2[col] = pd.to_numeric(df2[col], errors="coerce")

    for col in ["ts"]:
        if col in df1.columns:
            df1[col] = pd.to_datetime(df1[col], errors="coerce")
        if col in df2.columns:
            df2[col] = pd.to_datetime(df2[col], errors="coerce")

    total_orders = int(len(df2))
    valid_orders = int(df2[keys].dropna().shape[0])
    print(f"Total orders: {total_orders}, orders with non-null merge keys: {valid_orders}")

    if valid_orders == 0 or total_orders == 0:
        print("Merge-key alignment: no valid orders with full keys; cannot compute alignment.")
        report["stats"] = {
            "total_orders": total_orders,
            "valid_orders_with_keys": valid_orders,
            "alignment_rate": 0.0,
        }
        return report

    try:
        merged = df2.merge(
            df1[["underlying", "expiry", "strike", "side", "ts", "fwd_ret_1"]],
            on=keys,
            how="left",
            suffixes=("", "_fwd"),
        )
        matched = int(merged["fwd_ret_1"].notna().sum())
        alignment_rate = float(matched / total_orders)
        print(f"Orders matched with fwd_ret_1: {matched}/{total_orders} "
              f"({alignment_rate * 100:.2f}%)")

        report["stats"] = {
            "total_orders": total_orders,
            "valid_orders_with_keys": valid_orders,
            "matched_orders": matched,
            "alignment_rate": alignment_rate,
        }
    except Exception as e:
        print("Merge-key alignment join failed:")
        print(repr(e))
        report["error"] = repr(e)

    return report


def check_forward_feature_coverage():
    print_section("CHECK 6: FORWARD-RETURN FEATURE COVERAGE")

    phase221_path = os.path.join(ROOT, "storage", "live", "forward", "phase221_forward_returns.csv")
    df221, err221 = safe_load_csv(phase221_path)

    report: dict[str, object] = {}

    if df221 is None:
        print(f"Forward feature coverage skipped: {err221}")
        report["error"] = err221
        return report

    horizons = ["fwd_ret_1", "fwd_ret_2", "fwd_ret_5", "fwd_ret_10", "fwd_ret_15"]
    cov = {}
    total = int(len(df221))

    for h in horizons:
        if h in df221.columns:
            non_null = int(df221[h].notna().sum())
            cov[h] = {
                "non_null": non_null,
                "coverage": float(non_null / total) if total > 0 else None,
            }
            print(f"{h}: {non_null}/{total} non-null "
                  f"({cov[h]['coverage'] * 100:.2f}% coverage)")
        else:
            cov[h] = {
                "non_null": 0,
                "coverage": 0.0,
            }
            print(f"{h}: MISSING COLUMN")

    report["total_rows"] = total
    report["coverage"] = cov

    return report


def check_model_feature_health():
    print_section("CHECK 7: MODEL FEATURE HEALTH (BASIC)")

    phase221_path = os.path.join(ROOT, "storage", "live", "forward", "phase221_forward_returns.csv")
    df221, err221 = safe_load_csv(phase221_path)

    report: dict[str, object] = {}

    if df221 is None:
        print(f"Model feature health skipped: {err221}")
        report["error"] = err221
        return report

    feature_cols = [
        "pred_label",
        "pred_confidence",
        "prob_BUY_CE",
        "prob_BUY_PE",
        "prob_HOLD",
        "signal",
        "signal_strength",
        "ml_probability",
        "ce_pe_ratio",
        "moneyness",
    ]

    stats = {}
    for col in feature_cols:
        if col not in df221.columns:
            stats[col] = {"present": False}
            print(f"{col}: MISSING")
            continue
        s = df221[col]
        non_null = int(s.notna().sum())
        is_numeric = np.issubdtype(s.dtype, np.number)
        zero_fraction = None
        if is_numeric and non_null > 0:
            zero_fraction = float((s.fillna(0) == 0).sum() / len(s))
        stats[col] = {
            "present": True,
            "dtype": str(s.dtype),
            "non_null": non_null,
            "zero_fraction": zero_fraction,
        }
        print(f"{col}: present, dtype={s.dtype}, non_null={non_null}, "
              f"zero_fraction={zero_fraction}")

    report["feature_stats"] = stats
    return report


def main():
    print("# SYSTEM3 MULTI-VALIDATE MASTER REPORT (CASE 1 LAPTOP)")
    print(f"- Generated at: {datetime.now().isoformat(timespec='seconds')}")
    print(f"- Project root: {ROOT}")

    overall: dict[str, object] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "root": ROOT,
    }

    try:
        env = check_environment()
        files = check_file_presence()
        schema = validate_csv_schema()
        ts_report = check_timestamp_consistency()
        merge_report = check_merge_key_alignment()
        fwd_cov = check_forward_feature_coverage()
        feat_health = check_model_feature_health()
    except Exception as e:
        print_section("FATAL ERROR")
        print("An unexpected exception occurred:")
        print(traceback.format_exc())
        overall["fatal_error"] = repr(e)
    else:
        overall["environment"] = env
        overall["files"] = files
        overall["schema"] = schema
        overall["timestamps"] = ts_report
        overall["merge_keys"] = merge_report
        overall["forward_feature_coverage"] = fwd_cov
        overall["model_feature_health"] = feat_health

    # Compute simple readiness flags (data-only; NOT trading readiness)
    print_section("CHECK 8: SUMMARY FLAGS")
    data_ok = True

    # Files present
    for key, meta in overall.get("files", {}).items():
        if key == "latest_pipeline_report":
            continue
        if isinstance(meta, dict) and not meta.get("exists", True):
            data_ok = False
            print(f"- Missing critical file: {key} -> {meta.get('path')}")

    # Forward coverage threshold
    fwd_cov_data = overall.get("forward_feature_coverage", {})
    cov = fwd_cov_data.get("coverage", {}) if isinstance(fwd_cov_data, dict) else {}
    cov1 = cov.get("fwd_ret_1", {}).get("coverage")
    if cov1 is None or cov1 < 0.9:
        data_ok = False
        print(f"- fwd_ret_1 coverage below 90%: {cov1}")

    # Merge-key alignment threshold
    merge_stats = overall.get("merge_keys", {}).get("stats") if isinstance(overall.get("merge_keys"), dict) else None
    if merge_stats:
        align_rate = merge_stats.get("alignment_rate")
        if align_rate is None or align_rate < 0.3:
            data_ok = False
            print(f"- Merge-key alignment below 30%: {align_rate}")
    else:
        data_ok = False
        print("- Merge-key alignment stats missing.")

    print()
    print(f"DATA PIPELINE HEALTH (STRUCTURAL): {'OK' if data_ok else 'ISSUES DETECTED'}")

    # Save JSON report
    meta_dir = os.path.join(ROOT, "storage", "live", "meta")
    os.makedirs(meta_dir, exist_ok=True)
    out_path = os.path.join(meta_dir, "system3_multivalidate_report.json")
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(overall, f, indent=2, default=lambda x: str(x))
        print(f"\nJSON report saved to: {out_path}")
    except Exception as e:
        print(f"\nFailed to write JSON report: {repr(e)}")


if __name__ == "__main__":
    main()