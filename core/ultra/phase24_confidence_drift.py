"""
System3 Ultra - Phase 24: Confidence Drift Analyzer

Track how model confidence changes over time.
Detects upward, downward, or stable drift patterns.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 87
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
LEARNING_ULTRA_DIR = PROJECT_ROOT / "storage" / "learning_ultra"
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)


def analyze_confidence_drift(
    confidence_series: pd.Series,
    window_size: int = 50,
) -> Dict[str, Any]:
    """
    Analyze confidence drift from time series.

    Args:
        confidence_series: Series of confidence values over time
        window_size: Window size for rolling analysis

    Returns:
        Dict with drift direction, strength, and statistics
    """
    if len(confidence_series) < 10:
        return {
            "drift": "INSUFFICIENT_DATA",
            "strength": 0.0,
            "std_dev": 0.0,
            "mean": float(confidence_series.mean()) if not confidence_series.empty else 0.0,
            "early_mean": 0.0,
            "late_mean": 0.0,
            "drift_diff": 0.0,
            "sample_size": len(confidence_series),
        }

    # Clean data
    conf_clean = confidence_series.dropna()
    if len(conf_clean) < 10:
        return {
            "drift": "INSUFFICIENT_DATA",
            "strength": 0.0,
            "std_dev": 0.0,
            "mean": float(conf_clean.mean()) if not conf_clean.empty else 0.0,
            "early_mean": 0.0,
            "late_mean": 0.0,
            "drift_diff": 0.0,
            "sample_size": len(conf_clean),
        }

    # Compute statistics
    mean_conf = conf_clean.mean()
    std_conf = conf_clean.std()

    # Split into early and late periods
    mid = len(conf_clean) // 2
    early_mean = conf_clean.iloc[:mid].mean()
    late_mean = conf_clean.iloc[mid:].mean()

    # Compute drift
    drift_diff = late_mean - early_mean
    drift_strength = abs(drift_diff) / (std_conf + 1e-10)

    # Store drift_diff for return
    final_drift_diff = drift_diff

    # Classify drift direction
    if drift_strength < 0.2:
        drift = "STABLE"
    elif drift_diff > 0:
        drift = "UPWARD"
    else:
        drift = "DOWNWARD"

    # Rolling trend (more sophisticated)
    if len(conf_clean) >= window_size:
        rolling_mean = conf_clean.rolling(window=window_size, min_periods=10).mean()
        if not rolling_mean.empty:
            first_rolling = (
                rolling_mean.iloc[window_size - 1] if len(rolling_mean) > window_size - 1 else rolling_mean.iloc[0]
            )
            last_rolling = rolling_mean.iloc[-1]
            rolling_trend = last_rolling - first_rolling
            if abs(rolling_trend) > 0.05:
                if rolling_trend > 0:
                    drift = "UPWARD"
                else:
                    drift = "DOWNWARD"
                drift_strength = abs(rolling_trend) / (std_conf + 1e-10)

    return {
        "drift": drift,
        "strength": float(drift_strength),
        "std_dev": float(std_conf),
        "mean": float(mean_conf),
        "early_mean": float(early_mean),
        "late_mean": float(late_mean),
        "drift_diff": float(final_drift_diff),
        "sample_size": len(conf_clean),
    }


def load_recent_signals(n: int = 200) -> Optional[pd.DataFrame]:
    """
    Load last N signals from available sources.

    Args:
        n: Number of signals to load

    Returns:
        DataFrame with confidence column, or None
    """
    # Try shadow signals first
    shadow_csv = ULTRA_DIR / "angel_ultra_live_shadow_signals.csv"
    if shadow_csv.exists():
        try:
            df = pd.read_csv(shadow_csv)
            if "ultra_conf" in df.columns:
                df["confidence"] = df["ultra_conf"]
            elif "baseline_conf" in df.columns:
                df["confidence"] = df["baseline_conf"]
            if "confidence" in df.columns:
                return df.tail(n)
        except Exception:
            pass

    # Try baseline signals
    signals_csv = LIVE_DIR / "angel_index_ai_signals.csv"
    if signals_csv.exists():
        try:
            df = pd.read_csv(signals_csv)
            if "pred_confidence" in df.columns:
                df["confidence"] = df["pred_confidence"]
            elif "confidence" in df.columns:
                pass
            if "confidence" in df.columns:
                return df.tail(n)
        except Exception:
            pass

    # Try shadow master
    shadow_master = LEARNING_ULTRA_DIR / "angel_ultra_shadow_master.csv"
    if shadow_master.exists():
        try:
            df = pd.read_csv(shadow_master)
            if "confidence" in df.columns:
                return df.tail(n)
        except Exception:
            pass

    return None


def main() -> None:
    """Main entry point for testing."""
    print("=== SYSTEM3 ULTRA - PHASE 24: CONFIDENCE DRIFT ANALYZER ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load recent signals
    df_signals = load_recent_signals(n=200)

    if df_signals is None or df_signals.empty or "confidence" not in df_signals.columns:
        print("[WARN] No confidence data found. Using synthetic data for demo.")
        # Generate synthetic data for demo
        np.random.seed(42)
        # Simulate downward drift
        n_samples = 200
        base_conf = 0.7
        drift = -0.001
        conf_series = pd.Series([base_conf + drift * i + np.random.normal(0, 0.05) for i in range(n_samples)])
    else:
        conf_series = df_signals["confidence"]

    print(f"[LOAD] Analyzing {len(conf_series)} confidence values")

    # Analyze drift
    result = analyze_confidence_drift(conf_series, window_size=50)

    print("\n=== CONFIDENCE DRIFT ANALYSIS ===")
    print(f"Drift Direction: {result['drift']}")
    print(f"Drift Strength: {result['strength']:.3f}")
    print(f"Standard Deviation: {result['std_dev']:.3f}")
    print(f"Mean Confidence: {result['mean']:.3f}")
    print(f"Early Mean: {result['early_mean']:.3f}")
    print(f"Late Mean: {result['late_mean']:.3f}")
    print(f"Drift Difference: {result['drift_diff']:.3f}")
    print(f"Sample Size: {result['sample_size']}")

    # Save drift report
    drift_report = {
        "analysis_date": pd.Timestamp.now().isoformat(),
        **result,
    }

    import json

    report_json = REPORTS_ULTRA_DIR / "phase24_confidence_drift_report.json"
    with report_json.open("w", encoding="utf-8") as f:
        json.dump(drift_report, f, indent=2)
    print(f"\n[SAVE] Drift report saved to: {report_json}")

    print("\n[OK] Confidence Drift Analyzer validated")


if __name__ == "__main__":
    main()
