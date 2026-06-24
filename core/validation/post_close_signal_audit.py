"""
System3 Post-Close Signal Consistency Audit

Verifies that logged signals are consistent with thresholds and scores.
Performs daily diagnostics and anomaly detection.
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
META_DIR = PROJECT_ROOT / "storage" / "meta"
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
LOGS_DIR = PROJECT_ROOT / "storage" / "logs"
THRESHOLDS_JSON = META_DIR / "system3_live_thresholds.json"
SIGNALS_CSV = LIVE_DIR / "dhan_index_ai_signals.csv"

# Required columns for signal audit
REQUIRED_COLUMNS = ["underlying", "ts", "final_score", "signal", "side", "strike", "expiry"]

# Supported underlyings
SUPPORTED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def load_thresholds() -> Tuple[Dict[str, Any], List[str]]:
    """
    Load live thresholds from JSON.

    Returns:
        Tuple of (thresholds_dict, errors_list)
    """
    errors = []
    thresholds = {}

    if not THRESHOLDS_JSON.exists():
        errors.append(f"Thresholds file not found: {THRESHOLDS_JSON}")
        return {}, errors

    try:
        with THRESHOLDS_JSON.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if "global" in data:
            thresholds["global"] = {"buy": float(data["global"]["buy"]), "sell": float(data["global"]["sell"])}

        if "per_underlying" in data:
            thresholds["per_underlying"] = {}
            for underlying in SUPPORTED_UNDERLYINGS:
                if underlying in data["per_underlying"]:
                    thresholds["per_underlying"][underlying] = {
                        "buy": float(data["per_underlying"][underlying]["buy"]),
                        "sell": float(data["per_underlying"][underlying]["sell"]),
                    }
    except Exception as e:
        errors.append(f"Failed to load thresholds: {e}")

    return thresholds, errors


def load_today_signals(target_date: Optional[date] = None) -> Tuple[pd.DataFrame, List[str]]:
    """
    Load signals from today's CSV.

    Args:
        target_date: Date to filter (default: today)

    Returns:
        Tuple of (DataFrame, errors_list)
    """
    errors = []

    if target_date is None:
        target_date = date.today()

    if not SIGNALS_CSV.exists():
        errors.append(f"Signals CSV not found: {SIGNALS_CSV}")
        return pd.DataFrame(), errors

    try:
        df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        if df.empty:
            errors.append("Signals CSV is empty")
            return pd.DataFrame(), errors

        # Check required columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
            return pd.DataFrame(), errors

        # Filter by date if ts column exists
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            df["date"] = df["ts"].dt.date
            df = df[df["date"] == target_date].copy()

        # Convert final_score to numeric
        df["final_score"] = pd.to_numeric(df["final_score"], errors="coerce")

        return df, errors

    except Exception as e:
        errors.append(f"Failed to load signals CSV: {e}")
        return pd.DataFrame(), errors


def verify_signal_consistency(df: pd.DataFrame, thresholds: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Verify signal decisions are consistent with scores and thresholds.

    Returns:
        Tuple of (inconsistencies_list, warnings_list)
    """
    inconsistencies = []
    warnings = []

    if df.empty:
        return inconsistencies, warnings

    global_buy = thresholds.get("global", {}).get("buy", 0.1)
    global_sell = thresholds.get("global", {}).get("sell", -0.1)

    # Check each signal
    for idx, row in df.iterrows():
        underlying = row.get("underlying", "")
        score = row.get("final_score", 0.0)
        signal = row.get("signal", "")

        # Get threshold for this underlying
        if "per_underlying" in thresholds and underlying in thresholds["per_underlying"]:
            buy_thr = thresholds["per_underlying"][underlying]["buy"]
            sell_thr = thresholds["per_underlying"][underlying]["sell"]
        else:
            buy_thr = global_buy
            sell_thr = global_sell

        # Check consistency
        if pd.isna(score):
            warnings.append(f"Row {idx}: Missing final_score")
            continue

        # Expected signal based on score
        if score >= buy_thr:
            expected_signal = "BUY"
        elif score <= sell_thr:
            expected_signal = "SELL"
        else:
            expected_signal = "HOLD"

        # Check if signal matches expectation
        if signal != expected_signal:
            # Check if it's just barely above/below threshold (tolerance)
            tolerance = 0.001
            if signal == "BUY" and score < buy_thr - tolerance:
                inconsistencies.append(
                    f"Row {idx}: BUY signal with score {score:.4f} < threshold {buy_thr:.4f} "
                    f"(underlying: {underlying})"
                )
            elif signal == "SELL" and score > sell_thr + tolerance:
                inconsistencies.append(
                    f"Row {idx}: SELL signal with score {score:.4f} > threshold {sell_thr:.4f} "
                    f"(underlying: {underlying})"
                )
            elif signal == "HOLD" and (score >= buy_thr or score <= sell_thr):
                warnings.append(
                    f"Row {idx}: HOLD signal with score {score:.4f} outside HOLD range " f"(underlying: {underlying})"
                )

        # Check for score = 0 with BUY/SELL
        if abs(score) < 0.0001 and signal in ["BUY", "SELL"]:
            warnings.append(f"Row {idx}: {signal} signal with score near zero ({score:.6f})")

    return inconsistencies, warnings


def check_missing_fields(df: pd.DataFrame) -> List[str]:
    """
    Check for missing essential fields.

    Returns:
        List of warnings
    """
    warnings = []

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            warnings.append(f"Missing required column: {col}")
        else:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                warnings.append(f"Column {col} has {missing_count} missing values")

    return warnings


def compute_daily_diagnostics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute daily diagnostics.

    Returns:
        Dict with diagnostics
    """
    if df.empty:
        return {"total_signals": 0, "by_signal_type": {}, "by_underlying": {}, "score_distribution": {}}

    # Total counts
    total = len(df)

    # By signal type
    by_signal = df["signal"].value_counts().to_dict() if "signal" in df.columns else {}

    # By underlying
    by_underlying = {}
    if "underlying" in df.columns:
        for underlying in SUPPORTED_UNDERLYINGS:
            und_df = df[df["underlying"] == underlying]
            by_underlying[underlying] = {
                "total": len(und_df),
                "buy": len(und_df[und_df["signal"] == "BUY"]) if "signal" in und_df.columns else 0,
                "sell": len(und_df[und_df["signal"] == "SELL"]) if "signal" in und_df.columns else 0,
                "hold": len(und_df[und_df["signal"] == "HOLD"]) if "signal" in und_df.columns else 0,
            }

    # Score distribution
    if "final_score" in df.columns:
        score_col = pd.to_numeric(df["final_score"], errors="coerce")
        score_distribution = {
            "mean": float(score_col.mean()) if not score_col.empty else 0.0,
            "median": float(score_col.median()) if not score_col.empty else 0.0,
            "std": float(score_col.std()) if not score_col.empty else 0.0,
            "min": float(score_col.min()) if not score_col.empty else 0.0,
            "max": float(score_col.max()) if not score_col.empty else 0.0,
        }
    else:
        score_distribution = {}

    return {
        "total_signals": total,
        "by_signal_type": by_signal,
        "by_underlying": by_underlying,
        "score_distribution": score_distribution,
    }


def generate_audit_report(
    thresholds: Dict[str, Any],
    diagnostics: Dict[str, Any],
    inconsistencies: List[str],
    warnings: List[str],
    missing_field_warnings: List[str],
    target_date: date,
) -> str:
    """
    Generate post-close audit report.

    Returns:
        Markdown report string
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# System3 Post-Close Signal Consistency Audit\n",
        f"**Date**: {target_date.strftime('%Y-%m-%d')}\n",
        f"**Generated**: {now}\n",
        "\n## Thresholds Used\n",
        f"- **Global BUY**: >= {thresholds.get('global', {}).get('buy', 0.1):.3f}\n",
        f"- **Global SELL**: <= {thresholds.get('global', {}).get('sell', -0.1):.3f}\n",
        "\n## Daily Diagnostics\n",
        f"- **Total Signals**: {diagnostics.get('total_signals', 0)}\n",
        "\n### By Signal Type\n",
    ]

    by_signal = diagnostics.get("by_signal_type", {})
    if by_signal:
        for signal, count in sorted(by_signal.items()):
            lines.append(f"- **{signal}**: {count}\n")
    else:
        lines.append("- No signals found\n")

    lines.append("\n### By Underlying\n")
    lines.append("| Underlying | Total | BUY | SELL | HOLD |\n")
    lines.append("|------------|-------|-----|------|------|\n")

    by_underlying = diagnostics.get("by_underlying", {})
    for underlying in SUPPORTED_UNDERLYINGS:
        if underlying in by_underlying:
            und = by_underlying[underlying]
            lines.append(f"| {underlying} | {und['total']} | {und['buy']} | {und['sell']} | {und['hold']} |\n")

    # Score distribution
    score_dist = diagnostics.get("score_distribution", {})
    if score_dist:
        lines.append("\n### Score Distribution\n")
        lines.append(f"- **Mean**: {score_dist.get('mean', 0.0):.4f}\n")
        lines.append(f"- **Median**: {score_dist.get('median', 0.0):.4f}\n")
        lines.append(f"- **Std Dev**: {score_dist.get('std', 0.0):.4f}\n")
        lines.append(f"- **Min**: {score_dist.get('min', 0.0):.4f}\n")
        lines.append(f"- **Max**: {score_dist.get('max', 0.0):.4f}\n")

    # Inconsistencies
    if inconsistencies:
        lines.append("\n## ❌ Inconsistencies\n")
        for inc in inconsistencies:
            lines.append(f"- ❌ {inc}\n")
    else:
        lines.append("\n## ✅ No Inconsistencies Found\n")

    # Warnings
    all_warnings = warnings + missing_field_warnings
    if all_warnings:
        lines.append("\n## ⚠️ Warnings\n")
        for warn in all_warnings:
            lines.append(f"- ⚠️ {warn}\n")
    else:
        lines.append("\n## ✅ No Warnings\n")

    # Final verdict
    lines.append("\n## Final Verdict\n")
    if inconsistencies:
        lines.append("❌ **FAIL** - Inconsistencies detected\n")
    elif all_warnings:
        lines.append("⚠️ **PASS WITH WARNINGS** - No inconsistencies, but warnings present\n")
    else:
        lines.append("✅ **PASS** - All checks passed\n")

    return "".join(lines)


def main(target_date: Optional[date] = None) -> int:
    """
    Main post-close audit function.

    Args:
        target_date: Date to audit (default: today)

    Returns:
        Exit code: 0 for PASS, 1 for FAIL
    """
    if target_date is None:
        target_date = date.today()

    print("=" * 80)
    print("SYSTEM3 POST-CLOSE SIGNAL CONSISTENCY AUDIT")
    print("=" * 80)
    print(f"Date: {target_date.strftime('%Y-%m-%d')}\n")

    all_errors = []

    # Step 1: Load thresholds
    print("Step 1: Loading thresholds...")
    thresholds, errors = load_thresholds()
    if errors:
        all_errors.extend(errors)
        print(f"⚠️  Warnings: {len(errors)}")
        for err in errors:
            print(f"   - {err}")
    else:
        print("✅ PASSED: Thresholds loaded")

    # Step 2: Load today's signals
    print(f"\nStep 2: Loading signals for {target_date}...")
    df, errors = load_today_signals(target_date)
    if errors:
        all_errors.extend(errors)
        for err in errors:
            print(f"   - {err}")

    if df.empty:
        print("⚠️  No signals found for this date")
        return 0

    print(f"✅ PASSED: Loaded {len(df)} signals")

    # Step 3: Check missing fields
    print("\nStep 3: Checking for missing fields...")
    missing_warnings = check_missing_fields(df)
    if missing_warnings:
        print(f"⚠️  Warnings: {len(missing_warnings)}")
        for warn in missing_warnings:
            print(f"   - {warn}")
    else:
        print("✅ PASSED: All required fields present")

    # Step 4: Verify consistency
    print("\nStep 4: Verifying signal consistency...")
    inconsistencies, warnings = verify_signal_consistency(df, thresholds)
    if inconsistencies:
        print(f"❌ FAILURES: {len(inconsistencies)}")
        for inc in inconsistencies[:10]:  # Show first 10
            print(f"   - {inc}")
        if len(inconsistencies) > 10:
            print(f"   ... and {len(inconsistencies) - 10} more")
    else:
        print("✅ PASSED: No inconsistencies found")

    if warnings:
        print(f"⚠️  Warnings: {len(warnings)}")
        for warn in warnings[:10]:  # Show first 10
            print(f"   - {warn}")
        if len(warnings) > 10:
            print(f"   ... and {len(warnings) - 10} more")

    # Step 5: Compute diagnostics
    print("\nStep 5: Computing daily diagnostics...")
    diagnostics = compute_daily_diagnostics(df)
    print("✅ PASSED: Diagnostics computed")
    print(f"   Total signals: {diagnostics.get('total_signals', 0)}")

    # Step 6: Generate report
    print("\nStep 6: Generating audit report...")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = LOGS_DIR / f"system3_post_close_audit_{target_date.strftime('%Y%m%d')}.md"

    report = generate_audit_report(thresholds, diagnostics, inconsistencies, warnings, missing_warnings, target_date)

    try:
        with report_path.open("w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ PASSED: Report saved to {report_path}")
    except Exception as e:
        print(f"❌ FAILED: Could not write report: {e}")
        return 1

    # Final verdict
    print("\n" + "=" * 80)
    if inconsistencies:
        print("❌ FINAL VERDICT: FAIL")
        print(f"   {len(inconsistencies)} inconsistency(ies) detected")
        return 1
    elif warnings or missing_warnings:
        print("⚠️  FINAL VERDICT: PASS WITH WARNINGS")
        print(f"   {len(warnings) + len(missing_warnings)} warning(s)")
        return 0
    else:
        print("✅ FINAL VERDICT: PASS")
        return 0


if __name__ == "__main__":
    import sys

    exit_code = main()
    sys.exit(exit_code)
