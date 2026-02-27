"""
Angel One Index Options - Market Intelligence Dashboard

Combines all market intelligence modules into unified dashboard.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

from core.engine.angel_volatility_detector import detect_volatility_regime, classify_volatility_state
from core.engine.angel_microtrend_recognizer import detect_microtrend, classify_trend_direction
from core.engine.angel_breakout_predictor import predict_breakout, detect_breakout_signal
from core.engine.angel_iv_estimator import refine_iv_estimate
from core.engine.angel_risk_event_scanner import scan_risk_events, classify_risk_level

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
SIGNALS_CSV = LIVE_DIR / "angel_index_ai_signals.csv"


def run_market_intelligence_dashboard() -> None:
    """Run complete market intelligence dashboard."""
    print("=== ANGEL ONE INDEX OPTIONS - MARKET INTELLIGENCE DASHBOARD ===\n")

    # Load latest signals
    if not SIGNALS_CSV.exists():
        print("[ERROR] Signals CSV not found. Run menu 11 first.")
        return

    try:
        df = pd.read_csv(SIGNALS_CSV)
        if df.empty:
            print("[INFO] No signals available.")
            return

        # Get latest snapshot
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.sort_values("ts")
            latest = df.tail(100)  # Last 100 rows
        else:
            latest = df.tail(100)

        print("=== VOLATILITY ANALYSIS ===")
        df_vol = detect_volatility_regime(latest, window=5)
        vol_state = classify_volatility_state(df_vol)
        print(f"Volatility State: {vol_state}")

        print("\n=== TREND ANALYSIS ===")
        df_trend = detect_microtrend(latest, lookback=3)
        trend_dir = classify_trend_direction(df_trend)
        print(f"Trend Direction: {trend_dir}")

        print("\n=== BREAKOUT ANALYSIS ===")
        if "spot" in latest.columns:
            recent_spot = latest["spot"].tail(20)
            resistance = recent_spot.max()
            support = recent_spot.min()
            breakout = predict_breakout(latest, resistance, support)
            print(f"Breakout Signal: {breakout['breakout_signal']}")
            print(f"Breakout Probability: {breakout['breakout_probability']:.2f}")

        print("\n=== IV ANALYSIS ===")
        df_iv = refine_iv_estimate(latest)
        if "synthetic_iv" in df_iv.columns:
            avg_iv = df_iv["synthetic_iv"].mean()
            print(f"Average Synthetic IV: {avg_iv:.2%}")

        print("\n=== RISK ANALYSIS ===")
        df_risk = scan_risk_events(latest, threshold_pct=1.0)
        risk_level = classify_risk_level(df_risk)
        print(f"Risk Level: {risk_level}")

        print("\n=== SUMMARY ===")
        print(f"Volatility: {vol_state}")
        print(f"Trend: {trend_dir}")
        print(f"Risk: {risk_level}")

    except Exception as e:
        print(f"[ERROR] Dashboard failed: {e}")


def main() -> None:
    """Main entry point."""
    run_market_intelligence_dashboard()


if __name__ == "__main__":
    main()
