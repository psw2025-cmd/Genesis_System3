"""
System3 Static Threshold Sanity Check

Validates live thresholds JSON structure and verifies signal counts match expectations.
This is a pre-market check to ensure thresholds are safe before market opens.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
META_DIR = PROJECT_ROOT / "storage" / "meta"
CLEAN_DIR = PROJECT_ROOT / "storage" / "clean"
THRESHOLDS_JSON = META_DIR / "system3_live_thresholds.json"
EV_READY_CSV = CLEAN_DIR / "dhan_index_ai_signals_with_forward_ev_ready.csv"

# Expected signal counts (from distribution analysis)
EXPECTED_BUY_SIGNALS = 40
EXPECTED_SELL_SIGNALS = 39
SIGNAL_TOLERANCE = 2  # Allow +/- 2 signals for dataset changes

# Threshold sanity ranges
MIN_THRESHOLD = -1.0
MAX_THRESHOLD = 1.0

# Supported underlyings
SUPPORTED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def load_thresholds_json() -> Tuple[Dict[str, Any], List[str]]:
    """
    Load and validate thresholds JSON structure.

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
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in thresholds file: {e}")
        return {}, errors
    except Exception as e:
        errors.append(f"Failed to load thresholds file: {e}")
        return {}, errors

    # Check for required keys
    if "global" not in data:
        errors.append("Missing 'global' key in thresholds JSON")
    else:
        global_thresh = data["global"]
        if "buy" not in global_thresh or "sell" not in global_thresh:
            errors.append("Missing 'buy' or 'sell' in global thresholds")
        else:
            try:
                buy_val = float(global_thresh["buy"])
                sell_val = float(global_thresh["sell"])

                # Validate ranges
                if not (MIN_THRESHOLD <= buy_val <= MAX_THRESHOLD):
                    errors.append(f"Global BUY threshold {buy_val} out of range [{MIN_THRESHOLD}, {MAX_THRESHOLD}]")
                if not (MIN_THRESHOLD <= sell_val <= MAX_THRESHOLD):
                    errors.append(f"Global SELL threshold {sell_val} out of range [{MIN_THRESHOLD}, {MAX_THRESHOLD}]")

                # Validate logic (BUY should be positive, SELL should be negative)
                if buy_val <= 0:
                    errors.append(f"Global BUY threshold {buy_val} should be positive")
                if sell_val >= 0:
                    errors.append(f"Global SELL threshold {sell_val} should be negative")

                thresholds["global"] = {"buy": buy_val, "sell": sell_val}
            except (ValueError, TypeError) as e:
                errors.append(f"Invalid numeric values in global thresholds: {e}")

    # Check per-underlying thresholds
    if "per_underlying" not in data:
        errors.append("Missing 'per_underlying' key in thresholds JSON")
    else:
        per_underlying = data["per_underlying"]
        thresholds["per_underlying"] = {}

        for underlying in SUPPORTED_UNDERLYINGS:
            if underlying not in per_underlying:
                errors.append(f"Missing thresholds for underlying: {underlying}")
            else:
                und_thresh = per_underlying[underlying]
                if "buy" not in und_thresh or "sell" not in und_thresh:
                    errors.append(f"Missing 'buy' or 'sell' in {underlying} thresholds")
                else:
                    try:
                        buy_val = float(und_thresh["buy"])
                        sell_val = float(und_thresh["sell"])

                        # Validate ranges
                        if not (MIN_THRESHOLD <= buy_val <= MAX_THRESHOLD):
                            errors.append(f"{underlying} BUY threshold {buy_val} out of range")
                        if not (MIN_THRESHOLD <= sell_val <= MAX_THRESHOLD):
                            errors.append(f"{underlying} SELL threshold {sell_val} out of range")

                        # Validate logic
                        if buy_val <= 0:
                            errors.append(f"{underlying} BUY threshold {buy_val} should be positive")
                        if sell_val >= 0:
                            errors.append(f"{underlying} SELL threshold {sell_val} should be negative")

                        thresholds["per_underlying"][underlying] = {"buy": buy_val, "sell": sell_val}
                    except (ValueError, TypeError) as e:
                        errors.append(f"Invalid numeric values in {underlying} thresholds: {e}")

    return thresholds, errors


def load_ev_ready_csv() -> Tuple[pd.DataFrame, List[str]]:
    """
    Load EV-ready CSV for signal counting.

    Returns:
        Tuple of (DataFrame, errors_list)
    """
    errors = []

    if not EV_READY_CSV.exists():
        errors.append(f"EV-ready CSV not found: {EV_READY_CSV}")
        return pd.DataFrame(), errors

    try:
        df = pd.read_csv(EV_READY_CSV, engine="python", on_bad_lines="skip")
    except Exception as e:
        errors.append(f"Failed to load EV-ready CSV: {e}")
        return pd.DataFrame(), errors

    # Check required columns
    required_cols = ["underlying", "final_score"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns in CSV: {missing_cols}")
        return pd.DataFrame(), errors

    # Convert final_score to numeric
    df["final_score"] = pd.to_numeric(df["final_score"], errors="coerce")
    df = df.dropna(subset=["final_score"])

    if len(df) == 0:
        errors.append("No valid final_score values in CSV")

    return df, errors


def count_signals_at_thresholds(
    df: pd.DataFrame, thresholds: Dict[str, Any]
) -> Tuple[Dict[str, Dict[str, int]], List[str]]:
    """
    Count BUY/SELL signals at given thresholds.

    Returns:
        Tuple of (signal_counts_dict, errors_list)
    """
    errors = []
    counts = {}

    if df.empty:
        errors.append("DataFrame is empty, cannot count signals")
        return {}, errors

    # Get global thresholds
    if "global" not in thresholds:
        errors.append("No global thresholds available")
        return {}, errors

    global_buy = thresholds["global"]["buy"]
    global_sell = thresholds["global"]["sell"]

    # Count global signals
    buy_mask = df["final_score"] >= global_buy
    sell_mask = df["final_score"] <= global_sell

    counts["global"] = {
        "buy": int(buy_mask.sum()),
        "sell": int(sell_mask.sum()),
        "total": int((buy_mask | sell_mask).sum()),
    }

    # Count per-underlying signals
    counts["per_underlying"] = {}

    if "per_underlying" in thresholds:
        for underlying in SUPPORTED_UNDERLYINGS:
            if underlying not in thresholds["per_underlying"]:
                continue

            und_df = df[df["underlying"] == underlying].copy()
            if len(und_df) == 0:
                counts["per_underlying"][underlying] = {"buy": 0, "sell": 0, "total": 0}
                continue

            und_buy = thresholds["per_underlying"][underlying]["buy"]
            und_sell = thresholds["per_underlying"][underlying]["sell"]

            buy_mask = und_df["final_score"] >= und_buy
            sell_mask = und_df["final_score"] <= und_sell

            counts["per_underlying"][underlying] = {
                "buy": int(buy_mask.sum()),
                "sell": int(sell_mask.sum()),
                "total": int((buy_mask | sell_mask).sum()),
            }

    return counts, errors


def validate_signal_counts(counts: Dict[str, Dict[str, int]], thresholds: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate signal counts match expectations.

    Returns:
        Tuple of (is_valid, warnings_list)
    """
    warnings = []
    is_valid = True

    # Check global counts
    if "global" in counts:
        global_counts = counts["global"]
        buy_count = global_counts.get("buy", 0)
        sell_count = global_counts.get("sell", 0)

        # Check against expected (with tolerance)
        buy_diff = abs(buy_count - EXPECTED_BUY_SIGNALS)
        sell_diff = abs(sell_count - EXPECTED_SELL_SIGNALS)

        if buy_diff > SIGNAL_TOLERANCE:
            warnings.append(
                f"Global BUY signal count {buy_count} differs from expected {EXPECTED_BUY_SIGNALS} "
                f"(diff: {buy_diff}, tolerance: {SIGNAL_TOLERANCE})"
            )
            if buy_diff > SIGNAL_TOLERANCE * 2:
                is_valid = False

        if sell_diff > SIGNAL_TOLERANCE:
            warnings.append(
                f"Global SELL signal count {sell_count} differs from expected {EXPECTED_SELL_SIGNALS} "
                f"(diff: {sell_diff}, tolerance: {SIGNAL_TOLERANCE})"
            )
            if sell_diff > SIGNAL_TOLERANCE * 2:
                is_valid = False

        # Check for zero signals
        if buy_count == 0 and sell_count == 0:
            warnings.append("WARNING: Zero BUY and SELL signals at global thresholds")
            is_valid = False
        elif buy_count == 0:
            warnings.append("WARNING: Zero BUY signals at global thresholds")
        elif sell_count == 0:
            warnings.append("WARNING: Zero SELL signals at global thresholds")

    # Check per-underlying counts
    if "per_underlying" in counts:
        for underlying in SUPPORTED_UNDERLYINGS:
            if underlying not in counts["per_underlying"]:
                continue

            und_counts = counts["per_underlying"][underlying]
            buy_count = und_counts.get("buy", 0)
            sell_count = und_counts.get("sell", 0)

            if buy_count == 0 and sell_count == 0:
                warnings.append(f"WARNING: {underlying} has zero BUY and SELL signals")
                # Don't fail for individual underlying, just warn

    return is_valid, warnings


def main() -> int:
    """
    Main validation function.

    Returns:
        Exit code: 0 for PASS, 1 for FAIL
    """
    print("=" * 80)
    print("SYSTEM3 STATIC THRESHOLD SANITY CHECK")
    print("=" * 80)
    print()

    all_errors = []
    all_warnings = []

    # Step 1: Load and validate thresholds JSON
    print("Step 1: Loading thresholds JSON...")
    thresholds, errors = load_thresholds_json()
    if errors:
        all_errors.extend(errors)
        print(f"❌ FAILED: {len(errors)} error(s)")
        for err in errors:
            print(f"   - {err}")
    else:
        print("✅ PASSED: Thresholds JSON structure valid")
        print(f"   Global: BUY >= {thresholds['global']['buy']:.3f}, SELL <= {thresholds['global']['sell']:.3f}")

    # Step 2: Load EV-ready CSV
    print("\nStep 2: Loading EV-ready CSV...")
    df, errors = load_ev_ready_csv()
    if errors:
        all_errors.extend(errors)
        print(f"❌ FAILED: {len(errors)} error(s)")
        for err in errors:
            print(f"   - {err}")
    else:
        print(f"✅ PASSED: Loaded {len(df)} rows from EV-ready CSV")

    # Step 3: Count signals at thresholds
    if not all_errors and not df.empty:
        print("\nStep 3: Counting signals at thresholds...")
        counts, errors = count_signals_at_thresholds(df, thresholds)
        if errors:
            all_errors.extend(errors)
            print(f"❌ FAILED: {len(errors)} error(s)")
            for err in errors:
                print(f"   - {err}")
        else:
            print("✅ PASSED: Signal counts computed")

            # Print counts
            if "global" in counts:
                g = counts["global"]
                print(f"   Global: {g['buy']} BUY, {g['sell']} SELL, {g['total']} total")

            if "per_underlying" in counts:
                print("   Per-underlying:")
                for underlying in SUPPORTED_UNDERLYINGS:
                    if underlying in counts["per_underlying"]:
                        u = counts["per_underlying"][underlying]
                        print(f"     {underlying}: {u['buy']} BUY, {u['sell']} SELL, {u['total']} total")

    # Step 4: Validate signal counts
    if not all_errors and "global" in counts:
        print("\nStep 4: Validating signal counts...")
        is_valid, warnings = validate_signal_counts(counts, thresholds)
        all_warnings.extend(warnings)

        if warnings:
            print(f"⚠️  WARNINGS: {len(warnings)} warning(s)")
            for warn in warnings:
                print(f"   - {warn}")

        if not is_valid:
            all_errors.append("Signal counts validation failed")
            print("❌ FAILED: Signal counts do not match expectations")
        else:
            print("✅ PASSED: Signal counts within acceptable range")

    # Final verdict
    print("\n" + "=" * 80)
    if all_errors:
        print("❌ FINAL VERDICT: FAIL")
        print(f"   {len(all_errors)} error(s) found")
        print("\nErrors:")
        for err in all_errors:
            print(f"   - {err}")
        if all_warnings:
            print("\nWarnings:")
            for warn in all_warnings:
                print(f"   - {warn}")
        return 1
    else:
        print("✅ FINAL VERDICT: PASS")
        if all_warnings:
            print(f"   {len(all_warnings)} warning(s) (non-blocking)")
            for warn in all_warnings:
                print(f"   - {warn}")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
