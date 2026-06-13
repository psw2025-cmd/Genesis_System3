"""
System3 Phase 79 - Adaptive Threshold Engine

Use volatility/regime features to generate adaptive thresholds per regime
instead of single fixed values.
"""

import sys
import pandas as pd
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from itertools import product

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"

# Input files
SIGNALS_CSV = STORAGE_LIVE / "dhan_index_ai_signals.csv"
PNL_LOG_CSV = STORAGE_LIVE / "dhan_index_ai_pnl_log.csv"

# Output files
OUTPUT_JSON = STORAGE_ULTRA / "phase79_adaptive_thresholds.json"
OUTPUT_MD = STORAGE_ULTRA / "phase79_adaptive_thresholds.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

# Regimes (simplified - would normally come from regime classifier)
REGIMES = ["LOW_VOL", "MID_VOL", "HIGH_VOL", "TREND_UP", "TREND_DOWN", "CHOPPY"]
MIN_TRADES = 5  # Minimum trades per regime to consider


def load_data() -> Dict[str, pd.DataFrame]:
    """Load signals and PnL data."""
    data = {}

    if SIGNALS_CSV.exists():
        try:
            data["signals"] = pd.read_csv(SIGNALS_CSV)
        except Exception as e:
            print(f"[PH79] Error loading signals: {e}")
            data["signals"] = pd.DataFrame()
    else:
        data["signals"] = pd.DataFrame()

    if PNL_LOG_CSV.exists():
        try:
            data["pnl"] = pd.read_csv(PNL_LOG_CSV)
        except Exception as e:
            print(f"[PH79] Error loading PnL: {e}")
            data["pnl"] = pd.DataFrame()
    else:
        data["pnl"] = pd.DataFrame()

    return data


def classify_regime(row: pd.Series) -> str:
    """Classify regime for a signal (simplified heuristic)."""
    # TODO: Use actual regime classifier from Phase 14/46/49 if available
    # For now, use simple heuristic based on volatility
    vol = abs(row.get("spot_roll_std_5", 0.0))
    if vol < 0.01:
        return "LOW_VOL"
    elif vol > 0.05:
        return "HIGH_VOL"
    else:
        return "MID_VOL"


def evaluate_threshold_combo(
    signals_df: pd.DataFrame, pnl_df: pd.DataFrame, regime: str, min_conf: float, min_score: float
) -> Dict[str, Any]:
    """Evaluate a threshold combination for a regime."""
    # Filter signals by regime and thresholds
    regime_signals = signals_df[signals_df["regime"] == regime].copy()
    filtered = regime_signals[
        (regime_signals["pred_confidence"] >= min_conf) & (abs(regime_signals["expected_move_score"]) >= min_score)
    ]

    if len(filtered) < MIN_TRADES:
        return {
            "win_rate": 0.0,
            "avg_pnl": 0.0,
            "trades_used": len(filtered),
            "valid": False,
        }

    # Match with PnL
    trades_with_pnl = []
    for _, signal_row in filtered.iterrows():
        ts = signal_row.get("ts", "")
        underlying = signal_row.get("underlying", "")
        strike = signal_row.get("strike", 0)
        side = signal_row.get("side", "")

        if not pnl_df.empty:
            pnl_match = pnl_df[
                (pnl_df["ts"] == ts)
                & (pnl_df["underlying"] == underlying)
                & (pnl_df["strike"] == strike)
                & (pnl_df["side"] == side)
            ]
            if not pnl_match.empty:
                pnl_pct = pnl_match.iloc[0].get("pnl_pct", 0.0)
                trades_with_pnl.append(pnl_pct)

    if len(trades_with_pnl) < MIN_TRADES:
        return {
            "win_rate": 0.0,
            "avg_pnl": 0.0,
            "trades_used": len(trades_with_pnl),
            "valid": False,
        }

    wins = sum(1 for pnl in trades_with_pnl if pnl > 0)
    win_rate = wins / len(trades_with_pnl) if trades_with_pnl else 0.0
    avg_pnl = np.mean(trades_with_pnl) if trades_with_pnl else 0.0

    return {
        "win_rate": float(win_rate),
        "avg_pnl": float(avg_pnl),
        "trades_used": len(trades_with_pnl),
        "valid": True,
    }


def grid_search_regime(signals_df: pd.DataFrame, pnl_df: pd.DataFrame, regime: str) -> Dict[str, Any]:
    """Grid search best thresholds for a regime."""
    conf_range = np.arange(0.60, 0.96, 0.05)
    score_range = np.arange(0.10, 0.61, 0.05)

    best_combo = None
    best_avg_pnl = -999.0

    for min_conf, min_score in product(conf_range, score_range):
        result = evaluate_threshold_combo(signals_df, pnl_df, regime, min_conf, min_score)
        if result["valid"] and result["avg_pnl"] > best_avg_pnl:
            best_avg_pnl = result["avg_pnl"]
            best_combo = {
                "min_conf": float(min_conf),
                "min_score": float(min_score),
                "win_rate": result["win_rate"],
                "avg_pnl": result["avg_pnl"],
                "trades_used": result["trades_used"],
            }

    return best_combo or {
        "min_conf": 0.80,
        "min_score": 0.30,
        "win_rate": 0.0,
        "avg_pnl": 0.0,
        "trades_used": 0,
    }


def generate_adaptive_thresholds() -> Dict[str, Any]:
    """Generate adaptive thresholds per regime."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 79 - ADAPTIVE THRESHOLD ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load data
    data = load_data()
    signals_df = data["signals"]
    pnl_df = data["pnl"]

    if signals_df.empty:
        print("[PH79] No signals found. Creating default thresholds.")
        regimes_result = {
            regime: {
                "min_conf": 0.80,
                "min_score": 0.30,
                "win_rate": 0.0,
                "avg_pnl": 0.0,
                "trades_used": 0,
            }
            for regime in REGIMES
        }
    else:
        # Classify regimes
        signals_df["regime"] = signals_df.apply(classify_regime, axis=1)

        # Grid search per regime
        regimes_result = {}
        for regime in REGIMES:
            print(f"[PH79] Evaluating threshold grid for {regime}...")
            best = grid_search_regime(signals_df, pnl_df, regime)
            regimes_result[regime] = best

    report = {
        "timestamp": datetime.now().isoformat(),
        "regimes": regimes_result,
    }

    # Save JSON
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[PH79] Saved best per-regime thresholds to {OUTPUT_JSON}")

    # Generate MD
    generate_markdown(report)
    print(f"[PH79] Markdown report written to {OUTPUT_MD}")

    return report


def generate_markdown(report: Dict[str, Any]) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 79 - Adaptive Thresholds Report\n\n")
        f.write(f"**Date**: {report['timestamp']}\n\n")

        f.write("## Per-Regime Thresholds\n\n")
        f.write("| Regime | min_conf | min_score | win_rate | avg_pnl | trades_used |\n")
        f.write("|--------|----------|-----------|----------|---------|-------------|\n")

        for regime, params in report["regimes"].items():
            f.write(
                f"| {regime} | {params['min_conf']:.2f} | {params['min_score']:.2f} | "
                f"{params['win_rate']:.2f} | {params['avg_pnl']:.2f} | {params['trades_used']} |\n"
            )


def main():
    """Main entry point."""
    try:
        report = generate_adaptive_thresholds()
        print("\n[PH79] Adaptive threshold generation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH79] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
