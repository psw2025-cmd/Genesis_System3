"""
Dhan Index Options - Safety Layer V3

Overfit Guard + Noise Suppressor for model predictions.
SAFE MODE ONLY - Read-only validation.
"""

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
SIGNALS_CSV = LIVE_DIR / "dhan_index_ai_signals.csv"


class OverfitGuard:
    """Guards against overfitting in model predictions."""

    @staticmethod
    def detect_overfitting(df_signals: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect potential overfitting in signals.

        Returns:
            Dict with overfitting detection results
        """
        if df_signals.empty:
            return {
                "overfitting_detected": False,
                "confidence": 0.0,
                "reasons": [],
            }

        reasons = []
        confidence = 0.0

        # Check 1: Too many perfect predictions
        if "pred_confidence" in df_signals.columns:
            perfect_conf = (df_signals["pred_confidence"] == 1.0).sum()
            total = len(df_signals)
            if total > 0 and perfect_conf / total > 0.5:
                reasons.append(f"High percentage of perfect confidence ({perfect_conf/total*100:.1f}%)")
                confidence += 0.3

        # Check 2: Very low variance in predictions
        if "pred_label" in df_signals.columns:
            label_counts = df_signals["pred_label"].value_counts()
            if len(label_counts) == 1:
                reasons.append("All predictions are identical (no diversity)")
                confidence += 0.5

        # Check 3: Extreme confidence values only
        if "pred_confidence" in df_signals.columns:
            conf_std = df_signals["pred_confidence"].std()
            if conf_std < 0.05:
                reasons.append("Very low confidence variance (suspiciously uniform)")
                confidence += 0.2

        overfitting_detected = confidence > 0.5

        return {
            "overfitting_detected": overfitting_detected,
            "confidence": min(1.0, confidence),
            "reasons": reasons,
        }


class NoiseSuppressor:
    """Suppresses noise in model predictions."""

    @staticmethod
    def suppress_noise(df_signals: pd.DataFrame, min_confidence: float = 0.7) -> pd.DataFrame:
        """
        Suppress noisy/low-confidence signals.

        Args:
            df_signals: DataFrame with signals
            min_confidence: Minimum confidence threshold

        Returns:
            Filtered DataFrame
        """
        if df_signals.empty:
            return df_signals

        df = df_signals.copy()

        # Filter by confidence
        if "pred_confidence" in df.columns:
            df = df[df["pred_confidence"] >= min_confidence]

        # Filter by score magnitude
        if "expected_move_score" in df.columns:
            df = df[df["expected_move_score"].abs() >= 0.2]

        return df


def run_safety_checks_v3() -> Dict[str, Any]:
    """
    Run Safety Layer V3 checks.

    Returns:
        Dict with safety check results
    """
    print("=== ANGEL ONE INDEX OPTIONS - SAFETY LAYER V3 ===")
    print("[INFO] SAFE MODE - Read-only validation\n")

    if not SIGNALS_CSV.exists():
        return {
            "status": "NO_DATA",
            "message": "Signals CSV not found",
        }

    try:
        df = pd.read_csv(SIGNALS_CSV)
        if df.empty:
            return {
                "status": "EMPTY",
                "message": "No signals available",
            }

        # Get recent signals
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.sort_values("ts")
            recent = df.tail(100)
        else:
            recent = df.tail(100)

        # Overfit guard
        overfit_check = OverfitGuard.detect_overfitting(recent)

        # Noise suppressor (preview)
        filtered = NoiseSuppressor.suppress_noise(recent, min_confidence=0.7)
        noise_reduction = len(recent) - len(filtered)

        return {
            "status": "SUCCESS",
            "overfit_check": overfit_check,
            "noise_suppression": {
                "original_count": len(recent),
                "filtered_count": len(filtered),
                "noise_reduced": noise_reduction,
            },
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def main() -> None:
    """Main entry point."""
    results = run_safety_checks_v3()

    if results["status"] == "SUCCESS":
        print("=== OVERFIT GUARD RESULTS ===")
        overfit = results["overfit_check"]
        if overfit["overfitting_detected"]:
            print(f"⚠️  OVERFITTING DETECTED (confidence: {overfit['confidence']:.2f})")
            print("Reasons:")
            for reason in overfit["reasons"]:
                print(f"  • {reason}")
        else:
            print("✅ No overfitting detected")

        print("\n=== NOISE SUPPRESSION PREVIEW ===")
        noise = results["noise_suppression"]
        print(f"Original signals: {noise['original_count']}")
        print(f"After noise suppression: {noise['filtered_count']}")
        print(f"Noise reduced: {noise['noise_reduced']} signals")
    else:
        print(f"[INFO] {results.get('message', 'Safety checks not available')}")


if __name__ == "__main__":
    main()
