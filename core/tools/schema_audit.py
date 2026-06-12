"""
System3 CSV Schema Audit Module

Performs schema audit and generates documentation for dhan_index_ai_signals_with_forward.csv
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CSV_FILE = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"
OUTPUT_REPORT = PROJECT_ROOT / "docs" / "SYSTEM3_CSV_SCHEMA_AUTOMATED.md"


def detect_bad_rows(df: pd.DataFrame) -> Dict[str, List[int]]:
    """
    Detect and return indices of bad rows.

    Returns:
        Dictionary with keys: 'duplicate_headers', 'invalid_rows'
    """
    bad_rows = {"duplicate_headers": [], "invalid_rows": []}

    # Detect duplicate header rows
    if "signal" in df.columns:
        mask_signal = df["signal"] == "signal"
        bad_rows["duplicate_headers"].extend(df[mask_signal].index.tolist())

    if "pred_label" in df.columns:
        mask_pred = df["pred_label"] == "pred_label"
        bad_rows["duplicate_headers"].extend(df[mask_pred].index.tolist())

    # Remove duplicates
    bad_rows["duplicate_headers"] = list(set(bad_rows["duplicate_headers"]))

    # Detect completely empty rows (all NaN except identifiers)
    identifier_cols = ["underlying", "index_exch", "opt_exch", "symbol", "token"]
    if all(col in df.columns for col in identifier_cols):
        # Check if row has only identifiers and everything else is NaN
        for idx, row in df.iterrows():
            non_id_cols = [col for col in df.columns if col not in identifier_cols]
            if all(pd.isna(row[col]) for col in non_id_cols):
                bad_rows["invalid_rows"].append(idx)

    return bad_rows


def categorize_columns(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Categorize columns into logical groups.

    Returns:
        Dictionary mapping category names to column lists
    """
    categories = {
        "identifiers": [],
        "market_data": [],
        "greeks": [],
        "technical_indicators": [],
        "volatility_metrics": [],
        "momentum_features": [],
        "ml_outputs": [],
        "scores": [],
        "signals": [],
        "trade_planning": [],
        "derived_features": [],
        "forward_returns": [],
        "metadata": [],
    }

    # Define column mappings
    identifier_cols = ["underlying", "index_exch", "opt_exch", "symbol", "token", "expiry", "strike", "side"]
    market_data_cols = ["spot", "ltp", "time_to_expiry", "iv", "iv_estimate"]
    greeks_cols = ["delta", "gamma", "theta", "vega"]
    technical_cols = [
        "rsi",
        "macd",
        "macd_signal",
        "macd_histogram",
        "vwap",
        "price_vs_vwap",
        "supertrend",
        "supertrend_direction",
        "sma_5",
        "sma_10",
        "sma_20",
        "trend_score",
        "multi_tf_trend_score",
        "trend_strength",
        "trend_1m",
        "trend_3m",
        "trend_5m",
        "trend_15m",
    ]
    volatility_cols = [
        "iv_percentile",
        "iv_rank",
        "volatility_regime",
        "volatility_score",
        "iv_change_rate",
        "iv_spike",
        "regime_transition",
    ]
    momentum_cols = [
        "breakout_score",
        "momentum_score",
        "roc_1",
        "roc_3",
        "roc_5",
        "roc_10",
        "acceleration",
        "momentum_strength",
        "momentum_direction",
    ]
    ml_cols = ["ml_prediction", "ml_probability", "ai_score", "prob_BUY_CE", "prob_BUY_PE", "prob_HOLD"]
    scores_cols = ["greeks_score", "final_score", "signal_strength", "expected_move_score", "pred_confidence"]
    signals_cols = ["signal", "pred_label", "entry_buy", "entry_sell", "entry_hold"]
    trade_cols = [
        "entry_confidence",
        "stop_loss",
        "target_price",
        "risk_amount",
        "entry_price",
        "exit_sl_hit",
        "exit_target_hit",
        "trailing_sl",
        "exit_signal",
    ]
    derived_cols = [
        "moneyness",
        "ce_pe_ratio",
        "atm_dist_pct",
        "atm_dist_abs",
        "ce_pe_diff",
        "spot_chg_1_pct",
        "ltp_chg_1_pct",
        "spot_roll_std_5",
        "ltp_roll_std_5",
    ]
    forward_cols = ["fwd_ret_1", "fwd_ret_3", "fwd_ret_5"]
    metadata_cols = ["ts"]

    # Categorize columns
    for col in df.columns:
        if col in identifier_cols:
            categories["identifiers"].append(col)
        elif col in market_data_cols:
            categories["market_data"].append(col)
        elif col in greeks_cols:
            categories["greeks"].append(col)
        elif col in technical_cols:
            categories["technical_indicators"].append(col)
        elif col in volatility_cols:
            categories["volatility_metrics"].append(col)
        elif col in momentum_cols:
            categories["momentum_features"].append(col)
        elif col in ml_cols:
            categories["ml_outputs"].append(col)
        elif col in scores_cols:
            categories["scores"].append(col)
        elif col in signals_cols:
            categories["signals"].append(col)
        elif col in trade_cols:
            categories["trade_planning"].append(col)
        elif col in derived_cols:
            categories["derived_features"].append(col)
        elif col in forward_cols:
            categories["forward_returns"].append(col)
        elif col in metadata_cols:
            categories["metadata"].append(col)
        else:
            # Unclassified - add to metadata for now
            categories["metadata"].append(col)

    return categories


def run_schema_audit() -> Dict:
    """
    Run schema audit and generate report.

    Returns:
        Dictionary with audit results
    """
    print("=" * 80)
    print("SYSTEM3 CSV SCHEMA AUDIT")
    print("=" * 80)
    print(f"File: {CSV_FILE}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # Load CSV
    try:
        df = pd.read_csv(CSV_FILE, engine="python", on_bad_lines="skip")
        print(f"✅ CSV loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        return {"error": str(e)}

    # Basic statistics
    row_count = len(df)
    col_count = len(df.columns)

    print(f"\n📊 BASIC STATISTICS")
    print(f"  Total Rows: {row_count:,}")
    print(f"  Total Columns: {col_count}")

    # Detect bad rows
    bad_rows = detect_bad_rows(df)

    print(f"\n🔍 BAD ROW DETECTION")
    print(f"  Duplicate header rows: {len(bad_rows['duplicate_headers'])}")
    if bad_rows["duplicate_headers"]:
        print(
            f"    Indices: {bad_rows['duplicate_headers'][:10]}{'...' if len(bad_rows['duplicate_headers']) > 10 else ''}"
        )
    print(f"  Invalid rows (all NaN): {len(bad_rows['invalid_rows'])}")
    if bad_rows["invalid_rows"]:
        print(f"    Indices: {bad_rows['invalid_rows'][:10]}{'...' if len(bad_rows['invalid_rows']) > 10 else ''}")

    # Categorize columns
    categories = categorize_columns(df)

    # Generate markdown report
    report_lines = [
        "# System3 CSV Schema Audit - Automated Report",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**File**: `{CSV_FILE.name}`",
        "",
        "## Schema Overview",
        "",
        f"- **Total Rows**: {row_count:,}",
        f"- **Total Columns**: {col_count}",
        "",
        "## Column List",
        "",
        "| # | Column Name | Data Type | Non-Null Count | Null % |",
        "|---|-------------|-----------|----------------|--------|",
    ]

    for i, col in enumerate(df.columns, 1):
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        null_pct = ((row_count - non_null) / row_count * 100) if row_count > 0 else 0
        report_lines.append(f"| {i} | `{col}` | {dtype} | {non_null:,} | {null_pct:.1f}% |")

    report_lines.extend(
        ["", "## Bad Rows Detected", "", f"### Duplicate Header Rows: {len(bad_rows['duplicate_headers'])}", ""]
    )

    if bad_rows["duplicate_headers"]:
        report_lines.append("Row indices with duplicate headers:")
        for idx in bad_rows["duplicate_headers"][:20]:
            if "signal" in df.columns and "pred_label" in df.columns:
                signal_val = df.loc[idx, "signal"] if idx < len(df) else "N/A"
                pred_val = df.loc[idx, "pred_label"] if idx < len(df) else "N/A"
                report_lines.append(f"- Row {idx}: signal='{signal_val}', pred_label='{pred_val}'")
        if len(bad_rows["duplicate_headers"]) > 20:
            report_lines.append(f"- ... and {len(bad_rows['duplicate_headers']) - 20} more")
    else:
        report_lines.append("None detected.")

    report_lines.extend(["", f"### Invalid Rows (All NaN): {len(bad_rows['invalid_rows'])}", ""])

    if bad_rows["invalid_rows"]:
        report_lines.append("Row indices with all NaN values:")
        for idx in bad_rows["invalid_rows"][:20]:
            report_lines.append(f"- Row {idx}")
        if len(bad_rows["invalid_rows"]) > 20:
            report_lines.append(f"- ... and {len(bad_rows['invalid_rows']) - 20} more")
    else:
        report_lines.append("None detected.")

    report_lines.extend(["", "## Column Categories", ""])

    category_names = {
        "identifiers": "Identifiers / Keys",
        "market_data": "Market Data",
        "greeks": "Greeks",
        "technical_indicators": "Technical Indicators",
        "volatility_metrics": "Volatility Metrics",
        "momentum_features": "Momentum Features",
        "ml_outputs": "ML Outputs",
        "scores": "Scores",
        "signals": "Signals",
        "trade_planning": "Trade Planning",
        "derived_features": "Derived Features",
        "forward_returns": "Forward Returns",
        "metadata": "Metadata",
    }

    for cat_key, cat_name in category_names.items():
        cols = categories.get(cat_key, [])
        if cols:
            report_lines.append(f"### {cat_name} ({len(cols)} columns)")
            report_lines.append("")
            report_lines.append(", ".join([f"`{col}`" for col in cols]))
            report_lines.append("")

    # Write report
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"\n✅ Schema audit report saved: {OUTPUT_REPORT}")

    return {"row_count": row_count, "col_count": col_count, "bad_rows": bad_rows, "categories": categories}


if __name__ == "__main__":
    run_schema_audit()
