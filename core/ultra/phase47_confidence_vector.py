"""
System3 Ultra - Phase 47: 7D Confidence Vector Engine

Track confidence trends over 7-day rolling window.
Detect confidence patterns and generate trajectory predictions.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 109
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
OUTPUT_DIR = PROJECT_ROOT / "storage" / "ultra" / "ph46_ph55"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_confidence_history(days: int = 7) -> Optional[pd.DataFrame]:
    """Load confidence history for last N days."""
    # Try multiple sources
    sources = [
        ULTRA_DIR / "dhan_ultra_live_shadow_signals.csv",
        LIVE_DIR / "dhan_index_ai_signals.csv",
    ]

    for source in sources:
        if source.exists():
            try:
                df = pd.read_csv(source)
                if "pred_confidence" in df.columns or "confidence" in df.columns or "ultra_conf" in df.columns:
                    conf_col = (
                        "pred_confidence"
                        if "pred_confidence" in df.columns
                        else ("confidence" if "confidence" in df.columns else "ultra_conf")
                    )
                    df["confidence"] = df[conf_col]

                    # Parse timestamp
                    if "timestamp" in df.columns:
                        df["timestamp"] = pd.to_datetime(df["timestamp"])
                    elif "created_at" in df.columns:
                        df["timestamp"] = pd.to_datetime(df["created_at"])
                    else:
                        df["timestamp"] = pd.Timestamp.now()

                    # Filter last N days
                    cutoff = pd.Timestamp.now() - timedelta(days=days)
                    df = df[df["timestamp"] >= cutoff]

                    if not df.empty:
                        return df[["timestamp", "confidence", "underlying"]].copy()
            except Exception as e:
                print(f"[WARN] Failed to load from {source}: {e}")
                continue

    return None


def compute_confidence_vector(confidence_series: pd.Series, window: int = 7) -> Dict[str, Any]:
    """
    Compute 7-day confidence vector.

    Args:
        confidence_series: Series of confidence values
        window: Rolling window size (days)

    Returns:
        Dict with vector statistics and trends
    """
    if len(confidence_series) < 2:
        return {
            "vector_mean": 0.0,
            "vector_std": 0.0,
            "trend": "INSUFFICIENT_DATA",
            "trend_strength": 0.0,
            "trajectory": "STABLE",
            "current_confidence": float(confidence_series.iloc[-1]) if len(confidence_series) > 0 else 0.0,
            "rolling_mean": 0.0,
            "rolling_std": 0.0,
            "sample_size": len(confidence_series),
        }

    conf_clean = confidence_series.dropna()
    if len(conf_clean) < 2:
        return {
            "vector_mean": float(conf_clean.mean()) if not conf_clean.empty else 0.0,
            "vector_std": 0.0,
            "trend": "INSUFFICIENT_DATA",
            "trend_strength": 0.0,
            "trajectory": "STABLE",
            "current_confidence": float(conf_clean.iloc[-1]) if len(conf_clean) > 0 else 0.0,
            "rolling_mean": 0.0,
            "rolling_std": 0.0,
            "sample_size": len(conf_clean),
        }

    # Compute rolling statistics
    rolling_mean = conf_clean.rolling(window=min(window, len(conf_clean)), min_periods=1).mean()
    rolling_std = conf_clean.rolling(window=min(window, len(conf_clean)), min_periods=1).std()

    # Trend detection
    if len(conf_clean) >= 2:
        first_half = conf_clean.iloc[: len(conf_clean) // 2].mean()
        second_half = conf_clean.iloc[len(conf_clean) // 2 :].mean()
        trend_diff = second_half - first_half
        trend_strength = abs(trend_diff) / (conf_clean.std() + 1e-10)

        if trend_strength < 0.1:
            trend = "STABLE"
        elif trend_diff > 0:
            trend = "INCREASING"
        else:
            trend = "DECREASING"
    else:
        trend = "STABLE"
        trend_strength = 0.0

    # Trajectory prediction (simple linear extrapolation)
    if len(conf_clean) >= 3:
        recent = conf_clean.iloc[-3:].values
        trajectory_slope = (recent[-1] - recent[0]) / 2
        if abs(trajectory_slope) < 0.01:
            trajectory = "STABLE"
        elif trajectory_slope > 0:
            trajectory = "RISING"
        else:
            trajectory = "FALLING"
    else:
        trajectory = "STABLE"

    current_conf = float(conf_clean.iloc[-1]) if len(conf_clean) > 0 else 0.0
    rolling_mean_val = float(rolling_mean.iloc[-1]) if not rolling_mean.empty else 0.0
    rolling_std_val = float(rolling_std.iloc[-1]) if not rolling_std.empty and len(rolling_std) > 0 else 0.0

    return {
        "vector_mean": float(conf_clean.mean()),
        "vector_std": float(conf_clean.std()),
        "trend": trend,
        "trend_strength": float(trend_strength),
        "trajectory": trajectory,
        "current_confidence": current_conf,
        "rolling_mean": rolling_mean_val,
        "rolling_std": rolling_std_val,
        "sample_size": len(conf_clean),
    }


def run_phase47_confidence_vector() -> None:
    """Run Phase 47: 7D Confidence Vector Engine."""
    print("=== SYSTEM3 ULTRA - PHASE 47: 7D CONFIDENCE VECTOR ENGINE ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load confidence history
    df_conf = load_confidence_history(days=7)

    if df_conf is None or df_conf.empty:
        print("[WARN] No confidence history found. Using synthetic data for demo.")
        # Create synthetic data
        np.random.seed(42)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=168, freq="1H")  # 7 days hourly
        df_conf = pd.DataFrame(
            {
                "timestamp": dates,
                "confidence": np.random.uniform(0.5, 0.9, len(dates)) + np.linspace(0, 0.1, len(dates)),
                "underlying": np.random.choice(["NIFTY", "BANKNIFTY"], len(dates)),
            }
        )

    print(f"[LOAD] Loaded {len(df_conf)} confidence values")

    # Compute vectors per underlying
    vector_results = []
    trend_results = []

    for underlying in df_conf["underlying"].unique():
        df_underlying = df_conf[df_conf["underlying"] == underlying].sort_values("timestamp")

        vector = compute_confidence_vector(df_underlying["confidence"], window=7)
        vector["underlying"] = underlying
        vector["analysis_date"] = datetime.now().isoformat()

        vector_results.append(vector)

        # Trend over time
        trend_results.append(
            {
                "underlying": underlying,
                "timestamp": datetime.now().isoformat(),
                **vector,
            }
        )

    df_vectors = pd.DataFrame(vector_results)

    # Save results
    output_csv = OUTPUT_DIR / "phase47_confidence_vector_7d.csv"
    df_vectors.to_csv(output_csv, index=False)
    print(f"[SAVE] Confidence vectors saved to: {output_csv}")

    trends_json = OUTPUT_DIR / "phase47_confidence_trends.json"
    with trends_json.open("w", encoding="utf-8") as f:
        json.dump(trend_results, f, indent=2, default=str)
    print(f"[SAVE] Confidence trends saved to: {trends_json}")

    # Summary
    print("\n=== CONFIDENCE VECTOR SUMMARY ===")
    for _, row in df_vectors.iterrows():
        print(f"\n{row['underlying']}:")
        print(f"  Mean: {row['vector_mean']:.3f}")
        print(f"  Trend: {row['trend']} (strength: {row['trend_strength']:.3f})")
        print(f"  Trajectory: {row['trajectory']}")
        print(f"  Current: {row['current_confidence']:.3f}")

    print("\n[OK] Phase 47 7D Confidence Vector Engine completed")


def main() -> None:
    """Main entry point."""
    run_phase47_confidence_vector()


if __name__ == "__main__":
    main()
