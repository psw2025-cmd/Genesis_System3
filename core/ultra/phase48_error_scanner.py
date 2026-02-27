"""
System3 Ultra - Phase 48: Real Market Error Scanner

Scan for discrepancies between predictions and actual market behavior.
Identify systematic errors and classify error types.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 110
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
OUTPUT_DIR = PROJECT_ROOT / "storage" / "ultra" / "ph46_ph55"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_predictions_and_outcomes() -> Optional[pd.DataFrame]:
    """Load predictions and actual outcomes."""
    # Try to load from various sources
    sources = [
        (ULTRA_DIR / "phase31_ultra_fused_decisions.csv", "final_action"),
        (LIVE_DIR / "angel_index_ai_signals.csv", "pred_label"),
        (LIVE_DIR / "angel_index_ai_trades_plan.csv", "action"),
    ]

    predictions = []

    for source_path, action_col in sources:
        if source_path.exists():
            try:
                df = pd.read_csv(source_path)
                if action_col in df.columns:
                    predictions.append(
                        {
                            "source": source_path.stem,
                            "action": df[action_col].iloc[-1] if len(df) > 0 else "HOLD",
                            "confidence": (
                                df.get("pred_confidence", df.get("confidence", [0.0])).iloc[-1] if len(df) > 0 else 0.0
                            ),
                        }
                    )
            except Exception:
                continue

    # Try to load outcomes
    outcomes_path = LEARNING_DIR / "real_outcomes.csv"
    outcomes = None
    if outcomes_path.exists():
        try:
            outcomes = pd.read_csv(outcomes_path)
        except Exception:
            pass

    if not predictions:
        return None

    # Combine
    df_pred = pd.DataFrame(predictions)
    if outcomes is not None and not outcomes.empty:
        # Merge if possible
        if "outcome" in outcomes.columns:
            df_pred["actual_outcome"] = outcomes["outcome"].iloc[0] if len(outcomes) > 0 else "UNKNOWN"
    else:
        df_pred["actual_outcome"] = "UNKNOWN"

    return df_pred


def classify_error(prediction: str, outcome: str, confidence: float) -> Dict[str, Any]:
    """
    Classify error type.

    Args:
        prediction: Predicted action
        outcome: Actual outcome
        confidence: Prediction confidence

    Returns:
        Error classification dict
    """
    if outcome == "UNKNOWN":
        return {
            "error_type": "NO_OUTCOME_DATA",
            "severity": "LOW",
            "description": "No outcome data available",
        }

    # Map actions to directions
    action_map = {
        "BUY_CE": "UP",
        "BUY_PE": "DOWN",
        "HOLD": "NEUTRAL",
    }

    pred_dir = action_map.get(prediction, "UNKNOWN")
    outcome_dir = action_map.get(outcome, "UNKNOWN")

    if pred_dir == outcome_dir:
        return {
            "error_type": "NONE",
            "severity": "NONE",
            "description": "Prediction matches outcome",
        }

    if pred_dir == "UNKNOWN" or outcome_dir == "UNKNOWN":
        return {
            "error_type": "UNKNOWN_DIRECTION",
            "severity": "MEDIUM",
            "description": "Cannot determine direction",
        }

    # Direction mismatch
    if pred_dir != outcome_dir:
        if confidence > 0.8:
            return {
                "error_type": "HIGH_CONFIDENCE_MISMATCH",
                "severity": "HIGH",
                "description": f"High confidence ({confidence:.2f}) but wrong direction",
            }
        else:
            return {
                "error_type": "DIRECTION_MISMATCH",
                "severity": "MEDIUM",
                "description": f"Wrong direction predicted",
            }

    return {
        "error_type": "UNKNOWN",
        "severity": "LOW",
        "description": "Unknown error type",
    }


def scan_errors(df: pd.DataFrame) -> pd.DataFrame:
    """Scan for errors in predictions."""
    errors = []

    for _, row in df.iterrows():
        error = classify_error(
            row.get("action", "HOLD"), row.get("actual_outcome", "UNKNOWN"), row.get("confidence", 0.0)
        )

        errors.append(
            {
                "timestamp": datetime.now().isoformat(),
                "source": row.get("source", "UNKNOWN"),
                "prediction": row.get("action", "HOLD"),
                "outcome": row.get("actual_outcome", "UNKNOWN"),
                "confidence": row.get("confidence", 0.0),
                **error,
            }
        )

    return pd.DataFrame(errors)


def run_phase48_error_scanner() -> None:
    """Run Phase 48: Real Market Error Scanner."""
    print("=== SYSTEM3 ULTRA - PHASE 48: REAL MARKET ERROR SCANNER ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load predictions and outcomes
    df_data = load_predictions_and_outcomes()

    if df_data is None or df_data.empty:
        print("[WARN] No prediction/outcome data found. Using synthetic data for demo.")
        # Create synthetic data
        np.random.seed(42)
        df_data = pd.DataFrame(
            {
                "source": ["phase31", "signals", "trades"],
                "action": np.random.choice(["BUY_CE", "BUY_PE", "HOLD"], 3),
                "confidence": np.random.uniform(0.6, 0.9, 3),
                "actual_outcome": np.random.choice(["BUY_CE", "BUY_PE", "HOLD"], 3),
            }
        )

    print(f"[LOAD] Loaded {len(df_data)} prediction/outcome pairs")

    # Scan for errors
    df_errors = scan_errors(df_data)

    # Error patterns
    error_patterns = {
        "total_errors": len(df_errors[df_errors["error_type"] != "NONE"]),
        "high_severity": len(df_errors[df_errors["severity"] == "HIGH"]),
        "medium_severity": len(df_errors[df_errors["severity"] == "MEDIUM"]),
        "low_severity": len(df_errors[df_errors["severity"] == "LOW"]),
        "error_types": df_errors["error_type"].value_counts().to_dict(),
    }

    # Save results
    output_csv = OUTPUT_DIR / "phase48_error_scan_report.csv"
    df_errors.to_csv(output_csv, index=False)
    print(f"[SAVE] Error scan report saved to: {output_csv}")

    patterns_json = OUTPUT_DIR / "phase48_error_patterns.json"
    with patterns_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "patterns": error_patterns,
                "scan_date": datetime.now().isoformat(),
                "total_scanned": len(df_errors),
            },
            f,
            indent=2,
            default=str,
        )
    print(f"[SAVE] Error patterns saved to: {patterns_json}")

    # Summary
    print(f"\n=== ERROR SCAN SUMMARY ===")
    print(f"Total scanned: {len(df_errors)}")
    print(f"Errors found: {error_patterns['total_errors']}")
    print(f"High severity: {error_patterns['high_severity']}")
    print(f"Medium severity: {error_patterns['medium_severity']}")
    print(f"Low severity: {error_patterns['low_severity']}")
    print(f"\nError types:")
    for error_type, count in error_patterns["error_types"].items():
        print(f"  {error_type}: {count}")

    print("\n[OK] Phase 48 Real Market Error Scanner completed")


def main() -> None:
    """Main entry point."""
    run_phase48_error_scanner()


if __name__ == "__main__":
    main()
