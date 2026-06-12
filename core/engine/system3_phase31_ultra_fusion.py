"""
System3 Ultra - Phase 31: Ultra Decision Fusion Layer

Combine all Ultra outputs (SL/TP, risk, position size, regime, confidence, score)
into a single fused per-leg decision.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 94
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

ULTRA_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def _load_live_signals() -> Optional[pd.DataFrame]:
    """Load latest live signals CSV."""
    signals_csv = LIVE_DIR / "dhan_index_ai_signals.csv"
    if not signals_csv.exists():
        return None

    try:
        df = pd.read_csv(signals_csv)
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"[PHASE 31][ERROR] Failed to load signals: {e}")
        return None


def _load_ultra_artifacts() -> Dict[str, Any]:
    """Load Ultra artifacts from phases 21-30."""
    artifacts = {}

    # Phase 21: Risk evaluations
    risk_csv = REPORTS_ULTRA_DIR / "phase21_risk_evaluations.csv"
    if risk_csv.exists():
        try:
            artifacts["risk_evaluations"] = pd.read_csv(risk_csv)
        except Exception:
            pass

    # Phase 24: Confidence drift
    drift_json = REPORTS_ULTRA_DIR / "phase24_confidence_drift_report.json"
    if drift_json.exists():
        try:
            with drift_json.open("r", encoding="utf-8") as f:
                artifacts["confidence_drift"] = json.load(f)
        except Exception:
            pass

    # Phase 29: Sensitivity summary
    sensitivity_json = REPORTS_ULTRA_DIR / "phase29_sensitivity_summary.json"
    if sensitivity_json.exists():
        try:
            with sensitivity_json.open("r", encoding="utf-8") as f:
                artifacts["sensitivity"] = json.load(f)
        except Exception:
            pass

    # Phase 30: Calibration results
    calibration_csv = REPORTS_ULTRA_DIR / "phase30_calibration_results.csv"
    if calibration_csv.exists():
        try:
            artifacts["calibration"] = pd.read_csv(calibration_csv)
        except Exception:
            pass

    return artifacts


def _compute_risk_components(
    row: pd.Series,
    artifacts: Dict[str, Any],
) -> Dict[str, Any]:
    """Compute risk components from Ultra artifacts."""
    # Default values
    risk_score = 0.5
    risk_flag = "MEDIUM"
    regime = "UNKNOWN"

    # Try to get from calibration results (Phase 30)
    if "calibration" in artifacts:
        calib_df = artifacts["calibration"]
        # Match by underlying if possible
        underlying = row.get("underlying")
        if underlying and not calib_df.empty:
            calib_match = calib_df[calib_df.get("underlying", "") == underlying]
            if not calib_match.empty:
                risk_level = calib_match.iloc[0].get("updated_risk_level", "MEDIUM")
                if risk_level == "LOW":
                    risk_flag = "SAFE"
                    risk_score = 0.2
                elif risk_level == "HIGH":
                    risk_flag = "RISKY"
                    risk_score = 0.8
                else:
                    risk_flag = "MEDIUM"
                    risk_score = 0.5

    # Try to get from risk evaluations (Phase 21)
    if "risk_evaluations" in artifacts:
        risk_df = artifacts["risk_evaluations"]
        underlying = row.get("underlying")
        if underlying and not risk_df.empty:
            risk_match = risk_df[risk_df.get("underlying", "") == underlying]
            if not risk_match.empty:
                risk_score = risk_match.iloc[0].get("risk_score", risk_score)
                risk_level = risk_match.iloc[0].get("risk_level", "MEDIUM")
                if risk_level == "LOW":
                    risk_flag = "SAFE"
                elif risk_level == "HIGH":
                    risk_flag = "RISKY"

    return {
        "risk_score": float(risk_score),
        "risk_flag": risk_flag,
        "regime": regime,
    }


def _compute_sl_tp(
    row: pd.Series,
    artifacts: Dict[str, Any],
) -> Dict[str, float]:
    """Compute SL/TP from calibration or defaults."""
    sl_pct = 0.10  # Default 10%
    tp_pct = 0.20  # Default 20%

    # Try to get from calibration results
    if "calibration" in artifacts:
        calib_df = artifacts["calibration"]
        underlying = row.get("underlying")
        if underlying and not calib_df.empty:
            calib_match = calib_df[calib_df.get("underlying", "") == underlying]
            if not calib_match.empty:
                sl_pct = calib_match.iloc[0].get("updated_sl", sl_pct)
                tp_pct = calib_match.iloc[0].get("updated_tp", tp_pct)

    return {
        "sl_pct": float(sl_pct),
        "tp_pct": float(tp_pct),
    }


def _compute_final_action(
    model_signal: str,
    confidence: float,
    score: float,
    risk_flag: str,
) -> str:
    """
    Compute final action based on fusion logic.

    Fusion logic:
    - If risk_flag == 'BLOCKED' → AVOID
    - Else:
      - If BUY_CE and score > 0 and confidence >= 0.85 → STRONG_BUY_CE
      - If BUY_PE and score < 0 and confidence >= 0.85 → STRONG_BUY_PE
      - If BUY_CE with confidence >= 0.70 → BUY_CE
      - If BUY_PE with confidence >= 0.70 → BUY_PE
      - Else → HOLD
    """
    if risk_flag == "BLOCKED":
        return "AVOID"

    if pd.isna(model_signal) or model_signal not in ["BUY_CE", "BUY_PE", "HOLD"]:
        return "HOLD"

    conf = float(confidence) if not pd.isna(confidence) else 0.0
    scr = float(score) if not pd.isna(score) else 0.0

    if model_signal == "BUY_CE":
        if conf >= 0.85 and scr > 0:
            return "STRONG_BUY_CE"
        elif conf >= 0.70:
            return "BUY_CE"

    if model_signal == "BUY_PE":
        if conf >= 0.85 and scr < 0:
            return "STRONG_BUY_PE"
        elif conf >= 0.70:
            return "BUY_PE"

    return "HOLD"


def _compute_final_size(
    ultra_weight: float,
    risk_flag: str,
) -> float:
    """
    Compute final normalized position size (0-1).

    Size logic:
    - Base size = ultra_weight (0-1) * position_size_factor
    - Clamp between 0 and 1
    - If risk_flag != 'SAFE' → reduce size by 50-100% accordingly
    """
    base_size = ultra_weight

    # Adjust based on risk
    if risk_flag == "BLOCKED":
        return 0.0
    elif risk_flag == "RISKY":
        base_size *= 0.5  # Reduce by 50%
    elif risk_flag == "MEDIUM":
        base_size *= 0.75  # Reduce by 25%
    # SAFE: use full size

    return max(0.0, min(1.0, base_size))


def _compute_final_risk_flag(risk_flag: str, final_action: str) -> str:
    """Compute final risk flag."""
    if risk_flag == "BLOCKED" or final_action == "AVOID":
        return "BLOCKED"
    elif risk_flag == "RISKY":
        return "RISKY"
    elif risk_flag == "SAFE":
        return "SAFE"
    else:
        return "RISKY"  # Default to RISKY if unknown


def run_phase31_fusion(max_rows: int = 1000) -> str:
    """
    Run Phase 31: Ultra Decision Fusion.

    Args:
        max_rows: Maximum number of rows to process

    Returns:
        Path to output CSV file
    """
    print("=== SYSTEM3 ULTRA - PHASE 31: ULTRA DECISION FUSION LAYER ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load live signals
    df_signals = _load_live_signals()
    if df_signals is None or df_signals.empty:
        print("[PHASE 31][ERROR] No live signals found")
        error_path = ULTRA_DIR / "phase31_error_no_signals.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write("# Phase 31 Error\n\nNo live signals found in `storage/live/dhan_index_ai_signals.csv`\n")
        return str(error_path)

    print(f"[LOAD] Loaded {len(df_signals)} signals")

    # Limit rows
    if len(df_signals) > max_rows:
        df_signals = df_signals.tail(max_rows).copy()
        print(f"[INFO] Limited to last {max_rows} rows")

    # Load Ultra artifacts
    artifacts = _load_ultra_artifacts()
    print(f"[LOAD] Loaded {len(artifacts)} Ultra artifact sources")

    # Prepare output DataFrame
    fused_rows = []

    for _, row in df_signals.iterrows():
        # Extract base fields
        timestamp = row.get("timestamp", datetime.utcnow().isoformat())
        underlying = row.get("underlying", "")
        strike = row.get("strike", np.nan)
        side = row.get("side", "")
        ltp = row.get("ltp", np.nan)
        spot = row.get("spot", np.nan)

        # Extract model outputs
        model_signal = row.get("pred_label", row.get("signal", "HOLD"))
        confidence = row.get("pred_confidence", row.get("confidence", 0.0))
        score = row.get("expected_move_score", row.get("score", 0.0))

        # Compute risk components
        risk_comp = _compute_risk_components(row, artifacts)
        risk_score = risk_comp["risk_score"]
        risk_flag = risk_comp["risk_flag"]
        regime = risk_comp["regime"]

        # Compute SL/TP
        sl_tp = _compute_sl_tp(row, artifacts)
        sl_pct = sl_tp["sl_pct"]
        tp_pct = sl_tp["tp_pct"]

        # Compute ultra_weight (based on confidence and score)
        conf_norm = float(confidence) if not pd.isna(confidence) else 0.0
        score_abs = abs(float(score)) if not pd.isna(score) else 0.0
        ultra_weight = conf_norm * 0.6 + score_abs * 0.4  # Weighted combination

        # Compute final action
        final_action = _compute_final_action(model_signal, confidence, score, risk_flag)

        # Compute final size
        final_size = _compute_final_size(ultra_weight, risk_flag)

        # Compute final risk flag
        final_risk_flag = _compute_final_risk_flag(risk_flag, final_action)

        fused_row = {
            "timestamp": timestamp,
            "underlying": underlying,
            "strike": strike,
            "side": side,
            "ltp": ltp,
            "spot": spot,
            "model_signal": model_signal,
            "confidence": confidence,
            "score": score,
            "regime": regime,
            "risk_score": risk_score,
            "risk_flag": risk_flag,
            "sl_pct": sl_pct,
            "tp_pct": tp_pct,
            "ultra_weight": ultra_weight,
            "final_action": final_action,
            "final_size": final_size,
            "final_risk_flag": final_risk_flag,
        }
        fused_rows.append(fused_row)

    # Create DataFrame
    df_fused = pd.DataFrame(fused_rows)

    # Save CSV
    output_csv = ULTRA_DIR / "phase31_ultra_fused_decisions.csv"
    df_fused.to_csv(output_csv, index=False)
    print(f"[SAVE] Fused decisions saved to: {output_csv}")

    # Generate summary
    action_counts = df_fused["final_action"].value_counts()
    risk_counts = df_fused["final_risk_flag"].value_counts()

    print(f"\n=== FUSION SUMMARY ===")
    print(f"Total decisions: {len(df_fused)}")
    print(f"\nFinal Action Distribution:")
    for action, count in action_counts.items():
        print(f"  {action}: {count}")
    print(f"\nRisk Flag Distribution:")
    for risk, count in risk_counts.items():
        print(f"  {risk}: {count}")

    # Save JSON summary
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_decisions": len(df_fused),
        "action_distribution": action_counts.to_dict(),
        "risk_distribution": risk_counts.to_dict(),
        "output_file": str(output_csv),
    }

    summary_json = ULTRA_DIR / "phase31_ultra_fused_decisions_summary.json"
    with summary_json.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[SAVE] Summary saved to: {summary_json}")

    print("\n[OK] Phase 31 Ultra Decision Fusion completed")
    return str(output_csv)


def main() -> None:
    """Main entry point for CLI use."""
    try:
        path = run_phase31_fusion()
        print(f"\n[PHASE 31] Output written to: {path}")
    except Exception as e:
        print(f"[PHASE 31][ERROR] {e}")
        error_path = ULTRA_DIR / "phase31_error.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write(f"# Phase 31 Error\n\n{str(e)}\n")
        print(f"[PHASE 31] Error details saved to: {error_path}")


if __name__ == "__main__":
    main()
