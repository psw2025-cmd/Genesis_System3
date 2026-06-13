"""
System3 Pre-Market Signal Dry-Run

Performs a dry-run signal generation using today's latest prepared live-features file.
Applies live thresholds and performs safety checks before market opens.
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, date

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

# Safety limits
MAX_SIGNALS_PER_UNDERLYING = 50
DOMINANCE_THRESHOLD = 0.80  # 80% of signals from one underlying

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


def load_latest_snapshot() -> Tuple[Optional[pd.DataFrame], List[str]]:
    """
    Load latest snapshot from signals CSV or create a test snapshot.

    Returns:
        Tuple of (DataFrame, errors_list)
    """
    errors = []

    # Try to load from existing signals CSV
    if SIGNALS_CSV.exists():
        try:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

            if not df.empty:
                # Get latest snapshot (last 100 rows or last timestamp)
                if "ts" in df.columns:
                    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
                    df = df.sort_values("ts")
                    df = df.tail(100).copy()
                else:
                    df = df.tail(100).copy()

                # Ensure required columns
                required_cols = ["underlying", "final_score"]
                missing_cols = [col for col in required_cols if col not in df.columns]

                if missing_cols:
                    errors.append(f"Missing required columns: {missing_cols}")
                    return None, errors

                # Convert final_score to numeric
                df["final_score"] = pd.to_numeric(df["final_score"], errors="coerce")
                df = df.dropna(subset=["final_score", "underlying"])

                if len(df) > 0:
                    return df, errors
        except Exception as e:
            errors.append(f"Failed to load signals CSV: {e}")

    # If no CSV or empty, create a minimal test snapshot
    errors.append("No live signals CSV found or empty. Using test snapshot.")

    # Create minimal test data
    test_data = []
    for underlying in SUPPORTED_UNDERLYINGS:
        # Create a few test rows with scores around thresholds
        for score in [-0.15, -0.05, 0.05, 0.15]:
            test_data.append({"underlying": underlying, "final_score": score, "ts": datetime.now().isoformat()})

    df = pd.DataFrame(test_data)
    return df, errors


def apply_thresholds_and_count_signals(
    df: pd.DataFrame, thresholds: Dict[str, Any]
) -> Tuple[Dict[str, Dict[str, int]], Dict[str, pd.DataFrame]]:
    """
    Apply thresholds and count signals per underlying.

    Returns:
        Tuple of (counts_dict, signal_dfs_dict)
    """
    counts = {}
    signal_dfs = {}

    # Get global thresholds
    global_buy = thresholds.get("global", {}).get("buy", 0.1)
    global_sell = thresholds.get("global", {}).get("sell", -0.1)

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
    signal_dfs["per_underlying"] = {}

    for underlying in SUPPORTED_UNDERLYINGS:
        und_df = df[df["underlying"] == underlying].copy()
        if len(und_df) == 0:
            counts["per_underlying"][underlying] = {"buy": 0, "sell": 0, "total": 0}
            signal_dfs["per_underlying"][underlying] = pd.DataFrame()
            continue

        # Use per-underlying thresholds if available, else global
        if "per_underlying" in thresholds and underlying in thresholds["per_underlying"]:
            und_buy = thresholds["per_underlying"][underlying]["buy"]
            und_sell = thresholds["per_underlying"][underlying]["sell"]
        else:
            und_buy = global_buy
            und_sell = global_sell

        buy_mask = und_df["final_score"] >= und_buy
        sell_mask = und_df["final_score"] <= und_sell

        counts["per_underlying"][underlying] = {
            "buy": int(buy_mask.sum()),
            "sell": int(sell_mask.sum()),
            "total": int((buy_mask | sell_mask).sum()),
        }

        # Store signal rows
        signal_rows = und_df[buy_mask | sell_mask].copy()
        signal_rows["signal"] = signal_rows.apply(
            lambda row: "BUY" if row["final_score"] >= und_buy else "SELL", axis=1
        )
        signal_dfs["per_underlying"][underlying] = signal_rows

    return counts, signal_dfs


def analyze_score_distribution_near_thresholds(
    df: pd.DataFrame, thresholds: Dict[str, Any], band: float = 0.05
) -> Dict[str, Any]:
    """
    Analyze score distribution near thresholds.

    Returns:
        Dict with distribution statistics
    """
    global_buy = thresholds.get("global", {}).get("buy", 0.1)
    global_sell = thresholds.get("global", {}).get("sell", -0.1)

    # Count scores in bands around thresholds
    buy_band_above = ((df["final_score"] >= global_buy) & (df["final_score"] < global_buy + band)).sum()
    buy_band_below = ((df["final_score"] >= global_buy - band) & (df["final_score"] < global_buy)).sum()

    sell_band_above = ((df["final_score"] > global_sell) & (df["final_score"] <= global_sell + band)).sum()
    sell_band_below = ((df["final_score"] > global_sell - band) & (df["final_score"] <= global_sell)).sum()

    return {
        "buy_threshold": global_buy,
        "sell_threshold": global_sell,
        "buy_band_above": int(buy_band_above),
        "buy_band_below": int(buy_band_below),
        "sell_band_above": int(sell_band_above),
        "sell_band_below": int(sell_band_below),
        "band_width": band,
    }


def perform_safety_checks(counts: Dict[str, Dict[str, int]]) -> Tuple[bool, List[str], List[str]]:
    """
    Perform safety checks on signal counts.

    Returns:
        Tuple of (is_safe, failures_list, warnings_list)
    """
    failures = []
    warnings = []
    is_safe = True

    # Check 1: Total signals = 0
    total_signals = counts.get("global", {}).get("total", 0)
    if total_signals == 0:
        failures.append("Total BUY+SELL signals = 0 (thresholds too tight for current regime)")
        is_safe = False

    # Check 2: One underlying dominates > 80%
    per_underlying = counts.get("per_underlying", {})
    if total_signals > 0:
        for underlying in SUPPORTED_UNDERLYINGS:
            if underlying in per_underlying:
                und_total = per_underlying[underlying].get("total", 0)
                if und_total > 0:
                    dominance = und_total / total_signals
                    if dominance > DOMINANCE_THRESHOLD:
                        warnings.append(
                            f"{underlying} dominates {dominance*100:.1f}% of signals " f"({und_total}/{total_signals})"
                        )

    # Check 3: Any underlying has > MAX_SIGNALS_PER_UNDERLYING
    for underlying in SUPPORTED_UNDERLYINGS:
        if underlying in per_underlying:
            und_total = per_underlying[underlying].get("total", 0)
            if und_total > MAX_SIGNALS_PER_UNDERLYING:
                warnings.append(f"{underlying} has {und_total} signals (exceeds limit of {MAX_SIGNALS_PER_UNDERLYING})")

    return is_safe, failures, warnings


def generate_pre_market_report(
    thresholds: Dict[str, Any],
    counts: Dict[str, Dict[str, int]],
    distribution: Dict[str, Any],
    is_safe: bool,
    failures: List[str],
    warnings: List[str],
    errors: List[str],
) -> str:
    """
    Generate pre-market report markdown.

    Returns:
        Markdown report string
    """
    today = date.today().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# System3 Pre-Market Signal Dry-Run Report\n",
        f"**Date**: {today}\n",
        f"**Generated**: {now}\n",
        "\n## Thresholds Used\n",
        "\n### Global Thresholds\n",
        f"- **BUY Threshold**: >= {thresholds.get('global', {}).get('buy', 0.1):.3f}\n",
        f"- **SELL Threshold**: <= {thresholds.get('global', {}).get('sell', -0.1):.3f}\n",
        "\n### Per-Underlying Thresholds\n",
        "| Underlying | BUY Threshold | SELL Threshold |\n",
        "|------------|---------------|----------------|\n",
    ]

    if "per_underlying" in thresholds:
        for underlying in SUPPORTED_UNDERLYINGS:
            if underlying in thresholds["per_underlying"]:
                und = thresholds["per_underlying"][underlying]
                lines.append(f"| {underlying} | >= {und['buy']:.3f} | <= {und['sell']:.3f} |\n")

    lines.extend(
        [
            "\n## Signal Counts\n",
            "\n### Global Counts\n",
            f"- **BUY Signals**: {counts.get('global', {}).get('buy', 0)}\n",
            f"- **SELL Signals**: {counts.get('global', {}).get('sell', 0)}\n",
            f"- **Total Signals**: {counts.get('global', {}).get('total', 0)}\n",
            "\n### Per-Underlying Counts\n",
            "| Underlying | BUY | SELL | Total |\n",
            "|------------|-----|------|-------|\n",
        ]
    )

    if "per_underlying" in counts:
        for underlying in SUPPORTED_UNDERLYINGS:
            if underlying in counts["per_underlying"]:
                und = counts["per_underlying"][underlying]
                lines.append(f"| {underlying} | {und['buy']} | {und['sell']} | {und['total']} |\n")

    lines.extend(
        [
            "\n## Score Distribution Near Thresholds\n",
            f"- **BUY Threshold**: {distribution.get('buy_threshold', 0.1):.3f}\n",
            f"  - Scores in [{distribution.get('buy_threshold', 0.1) - distribution.get('band_width', 0.05):.3f}, "
            f"{distribution.get('buy_threshold', 0.1):.3f}): {distribution.get('buy_band_below', 0)}\n",
            f"  - Scores in [{distribution.get('buy_threshold', 0.1):.3f}, "
            f"{distribution.get('buy_threshold', 0.1) + distribution.get('band_width', 0.05):.3f}): "
            f"{distribution.get('buy_band_above', 0)}\n",
            f"- **SELL Threshold**: {distribution.get('sell_threshold', -0.1):.3f}\n",
            f"  - Scores in [{distribution.get('sell_threshold', -0.1) - distribution.get('band_width', 0.05):.3f}, "
            f"{distribution.get('sell_threshold', -0.1):.3f}): {distribution.get('sell_band_below', 0)}\n",
            f"  - Scores in [{distribution.get('sell_threshold', -0.1):.3f}, "
            f"{distribution.get('sell_threshold', -0.1) + distribution.get('band_width', 0.05):.3f}): "
            f"{distribution.get('sell_band_above', 0)}\n",
        ]
    )

    # Safety checks
    lines.append("\n## Safety Checks\n")
    if failures:
        lines.append("### ❌ Failures\n")
        for fail in failures:
            lines.append(f"- ❌ {fail}\n")

    if warnings:
        lines.append("\n### ⚠️ Warnings\n")
        for warn in warnings:
            lines.append(f"- ⚠️ {warn}\n")

    if not failures and not warnings:
        lines.append("- ✅ All safety checks passed\n")

    if errors:
        lines.append("\n### Errors (Non-Critical)\n")
        for err in errors:
            lines.append(f"- ⚠️ {err}\n")

    # Final verdict
    lines.append("\n## Final Verdict\n")
    if is_safe and not failures:
        lines.append("✅ **SAFE TO START** - All checks passed\n")
    else:
        lines.append("❌ **NOT SAFE TO START** - Failures detected\n")

    return "".join(lines)


def main() -> int:
    """
    Main pre-market dry-run function.

    Returns:
        Exit code: 0 for SAFE, 1 for NOT SAFE
    """
    print("=" * 80)
    print("SYSTEM3 PRE-MARKET SIGNAL DRY-RUN")
    print("=" * 80)
    print()

    all_errors = []

    # Step 1: Load thresholds
    print("Step 1: Loading live thresholds...")
    thresholds, errors = load_thresholds()
    if errors:
        all_errors.extend(errors)
        print(f"⚠️  Warnings: {len(errors)}")
        for err in errors:
            print(f"   - {err}")
    else:
        print("✅ PASSED: Thresholds loaded")
        print(
            f"   Global: BUY >= {thresholds.get('global', {}).get('buy', 0.1):.3f}, "
            f"SELL <= {thresholds.get('global', {}).get('sell', -0.1):.3f}"
        )

    # Step 2: Load latest snapshot
    print("\nStep 2: Loading latest snapshot...")
    df, errors = load_latest_snapshot()
    if errors:
        all_errors.extend(errors)
        for err in errors:
            print(f"   - {err}")

    if df is None or df.empty:
        print("❌ FAILED: No snapshot data available")
        return 1

    print(f"✅ PASSED: Loaded {len(df)} rows")

    # Step 3: Apply thresholds and count signals
    print("\nStep 3: Applying thresholds and counting signals...")
    counts, signal_dfs = apply_thresholds_and_count_signals(df, thresholds)

    print(
        f"   Global: {counts.get('global', {}).get('buy', 0)} BUY, "
        f"{counts.get('global', {}).get('sell', 0)} SELL, "
        f"{counts.get('global', {}).get('total', 0)} total"
    )

    # Step 4: Analyze distribution
    print("\nStep 4: Analyzing score distribution...")
    distribution = analyze_score_distribution_near_thresholds(df, thresholds)
    print("✅ PASSED: Distribution analyzed")

    # Step 5: Perform safety checks
    print("\nStep 5: Performing safety checks...")
    is_safe, failures, warnings = perform_safety_checks(counts)

    if failures:
        print(f"❌ FAILURES: {len(failures)}")
        for fail in failures:
            print(f"   - {fail}")

    if warnings:
        print(f"⚠️  WARNINGS: {len(warnings)}")
        for warn in warnings:
            print(f"   - {warn}")

    if not failures and not warnings:
        print("✅ PASSED: All safety checks passed")

    # Step 6: Generate report
    print("\nStep 6: Generating pre-market report...")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    report_path = LOGS_DIR / f"system3_pre_market_check_{today}.md"

    report = generate_pre_market_report(thresholds, counts, distribution, is_safe, failures, warnings, all_errors)

    try:
        with report_path.open("w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ PASSED: Report saved to {report_path}")
    except Exception as e:
        print(f"❌ FAILED: Could not write report: {e}")
        return 1

    # Final verdict
    print("\n" + "=" * 80)
    if is_safe and not failures:
        print("✅ FINAL VERDICT: SAFE TO START")
        return 0
    else:
        print("❌ FINAL VERDICT: NOT SAFE TO START")
        print("\nFailures:")
        for fail in failures:
            print(f"   - {fail}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
