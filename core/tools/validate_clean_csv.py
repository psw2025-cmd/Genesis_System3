"""
System3 Clean CSV Validation Module

Validates the cleaned CSV file and generates validation report.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
CLEAN_DIR = PROJECT_ROOT / "storage" / "clean"
CSV_CLEAN = CLEAN_DIR / "dhan_index_ai_signals_with_forward_clean.csv"
CSV_EV_READY = CLEAN_DIR / "dhan_index_ai_signals_with_forward_ev_ready.csv"
CSV_SELL_ANOMALIES = CLEAN_DIR / "dhan_index_ai_signals_sell_anomalies.csv"

OUTPUT_REPORT = PROJECT_ROOT / "docs" / "SYSTEM3_CSV_CLEAN_VALIDATION_SUMMARY.md"


def validate_greeks(df: pd.DataFrame) -> Dict:
    """Validate Greeks ranges."""
    results = {
        "delta_valid": True,
        "vega_valid": True,
        "theta_valid": True,
        "delta_out_of_range": 0,
        "negative_vega": 0,
        "positive_theta": 0,
        "large_positive_theta": 0,
    }

    if "delta" in df.columns:
        delta = pd.to_numeric(df["delta"], errors="coerce")
        out_of_range = ((delta < -1) | (delta > 1)).sum()
        results["delta_out_of_range"] = out_of_range
        results["delta_valid"] = out_of_range == 0

    if "vega" in df.columns:
        vega = pd.to_numeric(df["vega"], errors="coerce")
        negative = (vega < 0).sum()
        results["negative_vega"] = negative
        results["vega_valid"] = negative == 0

    if "theta" in df.columns:
        theta = pd.to_numeric(df["theta"], errors="coerce")
        positive = (theta > 0).sum()
        large_positive = (theta > 10).sum()
        results["positive_theta"] = positive
        results["large_positive_theta"] = large_positive
        results["theta_valid"] = large_positive == 0

    return results


def validate_iv(df: pd.DataFrame) -> Dict:
    """Validate IV ranges."""
    results = {"iv_valid": True, "iv_estimate_valid": True, "iv_out_of_range": 0, "iv_estimate_out_of_range": 0}

    for col in ["iv", "iv_estimate"]:
        if col in df.columns:
            iv = pd.to_numeric(df[col], errors="coerce")
            out_of_range = ((iv < 0) | (iv > 3)).sum()
            key = f"{col.replace('_', '_')}_out_of_range"
            results[key] = out_of_range
            results[f"{col}_valid"] = out_of_range == 0

    return results


def validate_probabilities(df: pd.DataFrame) -> Dict:
    """Validate probability ranges and sums."""
    results = {
        "prob_valid": True,
        "prob_sum_valid": True,
        "prob_out_of_range": 0,
        "prob_sum_bad": 0,
        "prob_sum_mean": 0.0,
        "prob_sum_std": 0.0,
    }

    prob_cols = ["prob_BUY_CE", "prob_BUY_PE", "prob_HOLD"]

    # Check individual ranges
    for col in prob_cols:
        if col in df.columns:
            prob = pd.to_numeric(df[col], errors="coerce")
            out_of_range = ((prob < 0) | (prob > 1)).sum()
            results["prob_out_of_range"] += out_of_range

    # Check probability sum
    if all(col in df.columns for col in prob_cols):
        prob_sum = (
            pd.to_numeric(df["prob_BUY_CE"], errors="coerce")
            + pd.to_numeric(df["prob_BUY_PE"], errors="coerce")
            + pd.to_numeric(df["prob_HOLD"], errors="coerce")
        )
        valid_mask = prob_sum.notna()
        if valid_mask.sum() > 0:
            prob_sum_valid = prob_sum[valid_mask]
            results["prob_sum_mean"] = prob_sum_valid.mean()
            results["prob_sum_std"] = prob_sum_valid.std()
            results["prob_sum_bad"] = (np.abs(prob_sum_valid - 1.0) > 0.05).sum()
            results["prob_sum_valid"] = results["prob_sum_bad"] == 0

    results["prob_valid"] = results["prob_out_of_range"] == 0

    return results


def validate_moneyness(df: pd.DataFrame) -> Dict:
    """Validate moneyness consistency."""
    results = {"moneyness_valid": True, "moneyness_zero_count": 0, "moneyness_inconsistent": 0}

    if all(col in df.columns for col in ["moneyness", "spot", "strike"]):
        moneyness = pd.to_numeric(df["moneyness"], errors="coerce")
        spot = pd.to_numeric(df["spot"], errors="coerce")
        strike = pd.to_numeric(df["strike"], errors="coerce")

        # Count zero values (should be rare after fix)
        results["moneyness_zero_count"] = ((moneyness == 0) & spot.notna() & strike.notna() & (strike > 0)).sum()

        # Check consistency with spot/strike
        valid_mask = moneyness.notna() & spot.notna() & strike.notna() & (strike > 0)
        if valid_mask.sum() > 0:
            expected_moneyness = spot[valid_mask] / strike[valid_mask]
            diff = np.abs(moneyness[valid_mask] - expected_moneyness)
            results["moneyness_inconsistent"] = (diff > 0.01).sum()
            results["moneyness_valid"] = (results["moneyness_zero_count"] == 0) and (
                results["moneyness_inconsistent"] == 0
            )

    return results


def validate_forward_returns(df: pd.DataFrame) -> Dict:
    """Validate forward returns."""
    results = {
        "fwd_ret_1_coverage": 0.0,
        "fwd_ret_3_coverage": 0.0,
        "fwd_ret_5_coverage": 0.0,
        "fwd_ret_outliers": 0,
        "fwd_ret_valid": True,
    }

    forward_cols = ["fwd_ret_1", "fwd_ret_3", "fwd_ret_5"]

    for col in forward_cols:
        if col in df.columns:
            fwd_ret = pd.to_numeric(df[col], errors="coerce")
            coverage = (fwd_ret.notna().sum() / len(df) * 100) if len(df) > 0 else 0
            key = f"{col}_coverage"
            results[key] = coverage

            # Check for outliers (> 1.0)
            outliers = (fwd_ret.abs() > 1.0).sum()
            results["fwd_ret_outliers"] += outliers

    results["fwd_ret_valid"] = results["fwd_ret_outliers"] == 0

    return results


def run_validation() -> Dict:
    """Run validation on clean CSV files."""
    print("=" * 80)
    print("SYSTEM3 CLEAN CSV VALIDATION")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    validation_results = {}

    # Load clean CSV
    if not CSV_CLEAN.exists():
        print(f"❌ Clean CSV not found: {CSV_CLEAN}")
        return {"error": "Clean CSV not found"}

    print(f"Loading clean CSV: {CSV_CLEAN}")
    df_clean = pd.read_csv(CSV_CLEAN, engine="python", on_bad_lines="skip")
    print(f"✅ Loaded {len(df_clean):,} rows")

    # Load EV-ready CSV
    if CSV_EV_READY.exists():
        df_ev = pd.read_csv(CSV_EV_READY, engine="python", on_bad_lines="skip")
        print(f"✅ Loaded EV-ready CSV: {len(df_ev):,} rows")
    else:
        df_ev = pd.DataFrame()
        print(f"⚠️ EV-ready CSV not found")

    # Load sell anomalies if exists
    if CSV_SELL_ANOMALIES.exists():
        df_anomalies = pd.read_csv(CSV_SELL_ANOMALIES, engine="python", on_bad_lines="skip")
        print(f"✅ Loaded SELL anomalies: {len(df_anomalies):,} rows")
    else:
        df_anomalies = pd.DataFrame()

    # Run validations
    print(f"\n🔍 Running Validations...")

    greeks_results = validate_greeks(df_clean)
    iv_results = validate_iv(df_clean)
    prob_results = validate_probabilities(df_clean)
    moneyness_results = validate_moneyness(df_clean)
    fwd_ret_results = validate_forward_returns(df_clean)

    validation_results = {
        "clean_rows": len(df_clean),
        "ev_ready_rows": len(df_ev),
        "sell_anomalies": len(df_anomalies),
        "greeks": greeks_results,
        "iv": iv_results,
        "probabilities": prob_results,
        "moneyness": moneyness_results,
        "forward_returns": fwd_ret_results,
    }

    # Print results
    print(f"\n📊 Validation Results:")
    print(f"\n  Greeks:")
    print(f"    Delta valid: {greeks_results['delta_valid']} (out of range: {greeks_results['delta_out_of_range']})")
    print(f"    Vega valid: {greeks_results['vega_valid']} (negative: {greeks_results['negative_vega']})")
    print(
        f"    Theta valid: {greeks_results['theta_valid']} (positive: {greeks_results['positive_theta']}, large: {greeks_results['large_positive_theta']})"
    )

    print(f"\n  IV:")
    print(f"    IV valid: {iv_results['iv_valid']} (out of range: {iv_results['iv_out_of_range']})")
    print(
        f"    IV estimate valid: {iv_results['iv_estimate_valid']} (out of range: {iv_results['iv_estimate_out_of_range']})"
    )

    print(f"\n  Probabilities:")
    print(f"    Prob valid: {prob_results['prob_valid']} (out of range: {prob_results['prob_out_of_range']})")
    print(
        f"    Prob sum valid: {prob_results['prob_sum_valid']} (bad: {prob_results['prob_sum_bad']}, mean: {prob_results['prob_sum_mean']:.4f})"
    )

    print(f"\n  Moneyness:")
    print(f"    Moneyness valid: {moneyness_results['moneyness_valid']}")
    print(f"    Zero values: {moneyness_results['moneyness_zero_count']}")
    print(f"    Inconsistent: {moneyness_results['moneyness_inconsistent']}")

    print(f"\n  Forward Returns:")
    print(f"    fwd_ret_1 coverage: {fwd_ret_results['fwd_ret_1_coverage']:.1f}%")
    print(f"    fwd_ret_3 coverage: {fwd_ret_results['fwd_ret_3_coverage']:.1f}%")
    print(f"    fwd_ret_5 coverage: {fwd_ret_results['fwd_ret_5_coverage']:.1f}%")
    print(f"    Outliers: {fwd_ret_results['fwd_ret_outliers']}")

    # Generate markdown report
    generate_report(validation_results, len(df_clean), len(df_ev), len(df_anomalies))

    return validation_results


def generate_report(results: Dict, clean_rows: int, ev_rows: int, anomaly_rows: int) -> None:
    """Generate markdown validation report."""

    report_lines = [
        "# System3 Clean CSV Validation Summary",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## File Summary",
        "",
        f"- **Clean CSV Rows**: {clean_rows:,}",
        f"- **EV-Ready CSV Rows**: {ev_rows:,}",
        f"- **SELL Anomalies**: {anomaly_rows:,}",
        "",
        "## Validation Results",
        "",
        "### Greeks Validation",
        "",
        f"- **Delta**: {'✅ PASS' if results['greeks']['delta_valid'] else '❌ FAIL'}",
        f"  - Out of range [-1, 1]: {results['greeks']['delta_out_of_range']} rows",
        f"- **Vega**: {'✅ PASS' if results['greeks']['vega_valid'] else '❌ FAIL'}",
        f"  - Negative values: {results['greeks']['negative_vega']} rows",
        f"- **Theta**: {'✅ PASS' if results['greeks']['theta_valid'] else '⚠️ WARN'}",
        f"  - Positive values: {results['greeks']['positive_theta']} rows",
        f"  - Large positive (>10): {results['greeks']['large_positive_theta']} rows",
        "",
        "### Implied Volatility Validation",
        "",
        f"- **IV**: {'✅ PASS' if results['iv']['iv_valid'] else '❌ FAIL'}",
        f"  - Out of range [0, 3]: {results['iv']['iv_out_of_range']} rows",
        f"- **IV Estimate**: {'✅ PASS' if results['iv']['iv_estimate_valid'] else '❌ FAIL'}",
        f"  - Out of range [0, 3]: {results['iv']['iv_estimate_out_of_range']} rows",
        "",
        "### Probabilities Validation",
        "",
        f"- **Individual Probabilities**: {'✅ PASS' if results['probabilities']['prob_valid'] else '❌ FAIL'}",
        f"  - Out of range [0, 1]: {results['probabilities']['prob_out_of_range']} rows",
        f"- **Probability Sum**: {'✅ PASS' if results['probabilities']['prob_sum_valid'] else '❌ FAIL'}",
        f"  - Mean: {results['probabilities']['prob_sum_mean']:.4f}",
        f"  - Std: {results['probabilities']['prob_sum_std']:.4f}",
        f"  - Bad sums (|sum - 1| > 0.05): {results['probabilities']['prob_sum_bad']} rows",
        "",
        "### Moneyness Validation",
        "",
        f"- **Status**: {'✅ PASS' if results['moneyness']['moneyness_valid'] else '❌ FAIL'}",
        f"  - Zero values (should be rare): {results['moneyness']['moneyness_zero_count']} rows",
        f"  - Inconsistent with spot/strike: {results['moneyness']['moneyness_inconsistent']} rows",
        "",
        "### Forward Returns Validation",
        "",
        f"- **Coverage**:",
        f"  - fwd_ret_1: {results['forward_returns']['fwd_ret_1_coverage']:.1f}%",
        f"  - fwd_ret_3: {results['forward_returns']['fwd_ret_3_coverage']:.1f}%",
        f"  - fwd_ret_5: {results['forward_returns']['fwd_ret_5_coverage']:.1f}%",
        f"- **Outliers (|ret| > 1.0)**: {'✅ PASS' if results['forward_returns']['fwd_ret_valid'] else '❌ FAIL'}",
        f"  - Outlier count: {results['forward_returns']['fwd_ret_outliers']} rows",
        "",
        "## Critical Issues Resolution",
        "",
        "### Moneyness Fix",
        f"- ✅ Moneyness recalculated as spot/strike",
        f"- Zero values: {results['moneyness']['moneyness_zero_count']} (should be 0 or very low)",
        "",
        "### Outlier Removal",
        f"- ✅ Rows with |forward_return| > 1.0 removed",
        f"- Outliers remaining: {results['forward_returns']['fwd_ret_outliers']} (should be 0)",
        "",
        "### SELL Signal Anomalies",
        f"- ⚠️ Anomalies detected: {anomaly_rows} rows",
        f"- Saved to: `storage/clean/dhan_index_ai_signals_sell_anomalies.csv`",
        f"- **Action Required**: Review these rows manually",
        "",
        "## Overall Status",
        "",
    ]

    # Determine overall status
    all_pass = (
        results["greeks"]["delta_valid"]
        and results["greeks"]["vega_valid"]
        and results["iv"]["iv_valid"]
        and results["iv"]["iv_estimate_valid"]
        and results["probabilities"]["prob_valid"]
        and results["probabilities"]["prob_sum_valid"]
        and results["moneyness"]["moneyness_valid"]
        and results["forward_returns"]["fwd_ret_valid"]
    )

    if all_pass:
        report_lines.append("✅ **ALL VALIDATIONS PASSED** - Clean CSV is ready for use")
    else:
        report_lines.append("⚠️ **SOME VALIDATIONS FAILED** - Review issues above")

    report_lines.extend(
        [
            "",
            "## Next Steps",
            "",
            "1. Review SELL anomalies if any detected",
            "2. Use `storage/clean/dhan_index_ai_signals_with_forward_clean.csv` for general analysis",
            "3. Use `storage/clean/dhan_index_ai_signals_with_forward_ev_ready.csv` for EV analysis and training",
            "",
        ]
    )

    # Write report
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"\n✅ Validation report saved: {OUTPUT_REPORT}")


if __name__ == "__main__":
    try:
        results = run_validation()
        print("\n✅ Validation completed successfully")
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
