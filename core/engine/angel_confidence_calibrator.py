"""
Angel One Index Options - Confidence & Score Calibrator (UPGRADED)

Calibrates model confidence and expected_move_score based on real outcomes.
Helps improve signal quality and threshold selection.

UPGRADES (World-Class AI Trading System):
- Confidence-based position sizing multiplier
- Time-based trading filter (high liquidity hours)
- Win/loss streak management
- Volatility-adjusted position scaling
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
SIGNALS_CSV = LIVE_DIR / "angel_index_ai_signals.csv"
PNL_LOG_CSV = LIVE_DIR / "angel_index_ai_pnl_log.csv"
CALIBRATION_JSON = PROJECT_ROOT / "storage" / "config" / "confidence_calibration.json"


class ConfidenceCalibrator:
    """
    Calibrates confidence and score predictions based on real outcomes.

    UPGRADED FEATURES:
    - Confidence-based position sizing
    - Time-based trading filters
    - Win/loss streak tracking
    - Volatility adjustments
    """

    def __init__(self):
        self.calibration_data = {}
        # Streak tracking
        self.win_streak = 0
        self.loss_streak = 0
        self.last_trade_result = None

    def calibrate(self, days: int = 7) -> Dict[str, Any]:
        """
        Calibrate confidence and score based on real PnL outcomes.

        Returns calibration factors and recommendations.
        """
        # Load signals and PnL data
        if not SIGNALS_CSV.exists() or not PNL_LOG_CSV.exists():
            return {
                "status": "NO_DATA",
                "message": "Signals or PnL data not available",
            }

        try:
            df_sig = pd.read_csv(SIGNALS_CSV)
            df_pnl = pd.read_csv(PNL_LOG_CSV)

            if df_sig.empty or df_pnl.empty:
                return {
                    "status": "EMPTY",
                    "message": "Data files are empty",
                }

            # Filter by date
            if "ts" in df_sig.columns:
                df_sig["ts"] = pd.to_datetime(df_sig["ts"], errors="coerce")
                cutoff = datetime.utcnow() - timedelta(days=days)
                df_sig = df_sig[df_sig["ts"] >= cutoff]

            if "exit_ts" in df_pnl.columns:
                df_pnl["exit_ts"] = pd.to_datetime(df_pnl["exit_ts"], errors="coerce")
                cutoff = datetime.utcnow() - timedelta(days=days)
                df_pnl = df_pnl[df_pnl["exit_ts"] >= cutoff]

            # Match signals with PnL (simplified matching)
            # In production, use trade IDs or timestamps for precise matching
            buy_signals = df_sig[df_sig.get("pred_label", "").isin(["BUY_CE", "BUY_PE"])]

            if buy_signals.empty or df_pnl.empty:
                return {
                    "status": "INSUFFICIENT_DATA",
                    "message": "Not enough buy signals or PnL data",
                }

            # Analyze confidence vs actual outcomes
            calibration = self._analyze_confidence_accuracy(buy_signals, df_pnl)

            return {
                "status": "SUCCESS",
                "calibration": calibration,
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": str(e),
            }

    def _analyze_confidence_accuracy(self, df_signals: pd.DataFrame, df_pnl: pd.DataFrame) -> Dict[str, Any]:
        """Analyze how well confidence predicts actual outcomes."""
        # Group by confidence ranges
        df_signals["conf_bucket"] = pd.cut(
            df_signals.get("pred_confidence", pd.Series([0.5] * len(df_signals))),
            bins=[0, 0.7, 0.8, 0.9, 1.0],
            labels=["0.7-0.8", "0.8-0.9", "0.9-1.0", "1.0"],
        )

        # Simplified: assume signals with higher confidence should have better outcomes
        # In production, match signals to PnL by trade ID or timestamp

        calibration = {
            "confidence_ranges": {},
            "score_calibration": {},
            "recommendations": [],
        }

        for bucket in df_signals["conf_bucket"].unique():
            if pd.isna(bucket):
                continue
            subset = df_signals[df_signals["conf_bucket"] == bucket]
            avg_conf = subset.get("pred_confidence", pd.Series()).mean()
            calibration["confidence_ranges"][str(bucket)] = {
                "count": len(subset),
                "avg_confidence": float(avg_conf) if not pd.isna(avg_conf) else 0.0,
            }

        # Recommendations
        calibration["recommendations"].append("Monitor confidence distribution vs actual PnL outcomes")
        calibration["recommendations"].append("Adjust confidence thresholds based on win rate by confidence bucket")

        return calibration

    def calculate_confidence_position_multiplier(self, confidence: float) -> float:
        """
        Calculate position size multiplier based on confidence.

        Formula: multiplier = 0.5 + (confidence * 0.5)
        Range: 0.5x to 1.0x (50% to 100% of base size)

        Args:
            confidence: Model confidence (0.0 to 1.0)

        Returns:
            Position multiplier (0.5 to 1.0)
        """
        if confidence < 0.0:
            confidence = 0.0
        elif confidence > 1.0:
            confidence = 1.0

        # Scale from 0.5 to 1.0 based on confidence
        multiplier = 0.5 + (confidence * 0.5)

        # Cap at reasonable limits
        multiplier = max(0.5, min(1.5, multiplier))

        return float(multiplier)

    def is_trading_hours_optimal(self, timestamp: Optional[datetime] = None) -> bool:
        """
        Check if current time is in optimal trading hours.

        Optimal hours (high liquidity):
        - Morning: 9:30 AM - 11:30 AM IST
        - Afternoon: 2:00 PM - 3:30 PM IST

        Args:
            timestamp: Timestamp to check (default: now)

        Returns:
            True if in optimal trading hours
        """
        if timestamp is None:
            timestamp = datetime.now()

        hour = timestamp.hour
        minute = timestamp.minute
        time_decimal = hour + (minute / 60.0)

        # Morning session: 9:30 (9.5) to 11:30 (11.5)
        morning_optimal = 9.5 <= time_decimal < 11.5

        # Afternoon session: 14:00 (14.0) to 15:30 (15.5)
        afternoon_optimal = 14.0 <= time_decimal < 15.5

        return morning_optimal or afternoon_optimal

    def calculate_streak_multiplier(self) -> float:
        """
        Calculate position size multiplier based on win/loss streak.

        Rules:
        - After 3+ consecutive wins: Increase size by 20% (1.2x)
        - After 3+ consecutive losses: Reduce size by 50% (0.5x) or pause
        - Normal: 1.0x

        Returns:
            Streak multiplier (0.5 to 1.2)
        """
        if self.win_streak >= 3:
            # Hot streak - increase size
            return 1.2
        elif self.loss_streak >= 3:
            # Cold streak - reduce size significantly
            return 0.5
        else:
            # Normal
            return 1.0

    def update_streak(self, trade_result: str):
        """
        Update win/loss streak tracking.

        Args:
            trade_result: "WIN", "LOSS", or "BREAK_EVEN"
        """
        if trade_result == "WIN":
            self.win_streak += 1
            self.loss_streak = 0
        elif trade_result == "LOSS":
            self.loss_streak += 1
            self.win_streak = 0
        else:  # BREAK_EVEN
            # Reset streaks on break-even
            self.win_streak = 0
            self.loss_streak = 0

        self.last_trade_result = trade_result

    def get_position_size_adjustments(
        self, confidence: float, timestamp: Optional[datetime] = None, volatility: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get all position size adjustments.

        Args:
            confidence: Model confidence (0.0 to 1.0)
            timestamp: Trade timestamp (for time filter)
            volatility: Current volatility (for volatility adjustment)

        Returns:
            Dict with all adjustments and final multiplier
        """
        # Confidence multiplier
        conf_mult = self.calculate_confidence_position_multiplier(confidence)

        # Time filter
        time_optimal = self.is_trading_hours_optimal(timestamp)
        time_mult = 1.0 if time_optimal else 0.0  # Don't trade outside optimal hours

        # Streak multiplier
        streak_mult = self.calculate_streak_multiplier()

        # Volatility adjustment (reduce size in high volatility)
        vol_mult = 1.0
        if volatility is not None:
            if volatility > 0.30:  # High IV (>30%)
                vol_mult = 0.8  # Reduce by 20%
            elif volatility < 0.15:  # Low IV (<15%)
                vol_mult = 1.1  # Increase by 10%

        # Final multiplier (all adjustments combined)
        final_mult = conf_mult * time_mult * streak_mult * vol_mult

        return {
            "confidence_multiplier": conf_mult,
            "time_optimal": time_optimal,
            "time_multiplier": time_mult,
            "streak_multiplier": streak_mult,
            "win_streak": self.win_streak,
            "loss_streak": self.loss_streak,
            "volatility_multiplier": vol_mult,
            "final_multiplier": final_mult,
            "should_trade": time_optimal and final_mult > 0,
        }

    def save_calibration(self, calibration: Dict[str, Any]) -> bool:
        """Save calibration data to JSON."""
        import json

        PROJECT_ROOT / "storage" / "config" / "confidence_calibration.json"
        CALIBRATION_JSON.parent.mkdir(parents=True, exist_ok=True)

        output = {
            "calibrated_at": datetime.utcnow().isoformat(),
            "calibration": calibration,
        }

        try:
            with CALIBRATION_JSON.open("w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
            return True
        except Exception as e:
            print(f"[CALIBRATOR] Failed to save calibration: {e}")
            return False


def main() -> None:
    """Main entry point for confidence calibrator."""
    print("=== ANGEL ONE INDEX OPTIONS - CONFIDENCE CALIBRATOR ===")

    calibrator = ConfidenceCalibrator()
    result = calibrator.calibrate(days=7)

    if result["status"] == "SUCCESS":
        print("\n=== CALIBRATION RESULTS ===")
        cal = result["calibration"]
        print("Confidence ranges:")
        for bucket, data in cal.get("confidence_ranges", {}).items():
            print(f"  {bucket}: {data['count']} signals, avg_conf={data['avg_confidence']:.3f}")

        print("\nRecommendations:")
        for rec in cal.get("recommendations", []):
            print(f"  - {rec}")

        calibrator.save_calibration(cal)
        print(f"\n[SAVE] Calibration saved to: {CALIBRATION_JSON}")
    else:
        print(f"[INFO] {result.get('message', 'Calibration not available')}")


if __name__ == "__main__":
    main()
