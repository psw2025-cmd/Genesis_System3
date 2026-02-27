"""
Angel One Index Options - Auto Threshold Adjuster

Automatically adjusts thresholds based on real market performance.
Currently DISABLED - requires manual review and approval.
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

from core.engine.angel_trade_config import DEFAULT_THRESHOLDS, TradeThresholds
from core.engine.angel_automation_config import AUTOMATION_CONFIG

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
THRESHOLDS_AUTO_JSON = CONFIG_DIR / "thresholds_auto.json"
THRESHOLDS_RECOMMENDED_JSON = CONFIG_DIR / "thresholds_recommended.json"
PNL_LOG_CSV = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_pnl_log.csv"
SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals.csv"


class AutoThresholdAdjuster:
    """
    Automatically adjusts thresholds based on real performance.

    Currently DISABLED - generates recommendations only.
    """

    def __init__(self):
        self.auto_adjust_enabled = False  # Safety: disabled by default
        self.min_trades_for_adjustment = 10  # Need at least 10 trades to adjust
        self.min_days_data = 3  # Need at least 3 days of data

    def analyze_performance(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze recent performance to generate threshold recommendations.

        Returns recommendations without applying them.
        """
        # Load PnL data
        if not PNL_LOG_CSV.exists():
            return {
                "status": "NO_DATA",
                "message": "No PnL data available for analysis",
            }

        try:
            df_pnl = pd.read_csv(PNL_LOG_CSV)
            if df_pnl.empty:
                return {
                    "status": "EMPTY",
                    "message": "PnL log is empty",
                }

            # Filter by date
            if "exit_ts" in df_pnl.columns:
                df_pnl["exit_ts"] = pd.to_datetime(df_pnl["exit_ts"], errors="coerce")
                cutoff = datetime.utcnow() - timedelta(days=days)
                df_pnl = df_pnl[df_pnl["exit_ts"] >= cutoff]

            if df_pnl.empty:
                return {
                    "status": "NO_RECENT_DATA",
                    "message": f"No PnL data in last {days} days",
                }

            pnl_col = "pnl_pct" if "pnl_pct" in df_pnl.columns else "pct_pnl"
            if pnl_col not in df_pnl.columns:
                return {
                    "status": "NO_PNL_COLUMN",
                    "message": "PnL column not found",
                }

            # Analyze performance
            total_trades = len(df_pnl)
            win_rate = (df_pnl[pnl_col] > 0).sum() / total_trades * 100 if total_trades > 0 else 0
            avg_pnl = df_pnl[pnl_col].mean()
            total_pnl = df_pnl[pnl_col].sum()

            # Load signals to analyze confidence/score distribution
            signals_analysis = self._analyze_signals_distribution(days)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                total_trades, win_rate, avg_pnl, total_pnl, signals_analysis
            )

            return {
                "status": "SUCCESS",
                "analysis": {
                    "total_trades": total_trades,
                    "win_rate": win_rate,
                    "avg_pnl": avg_pnl,
                    "total_pnl": total_pnl,
                },
                "recommendations": recommendations,
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": str(e),
            }

    def _analyze_signals_distribution(self, days: int) -> Dict[str, Any]:
        """Analyze signal distribution for threshold recommendations."""
        if not SIGNALS_CSV.exists():
            return {}

        try:
            df_sig = pd.read_csv(SIGNALS_CSV)
            if df_sig.empty:
                return {}

            # Filter by date
            if "ts" in df_sig.columns:
                df_sig["ts"] = pd.to_datetime(df_sig["ts"], errors="coerce")
                cutoff = datetime.utcnow() - timedelta(days=days)
                df_sig = df_sig[df_sig["ts"] >= cutoff]

            buy_signals = df_sig[df_sig.get("pred_label", "").isin(["BUY_CE", "BUY_PE"])]

            if buy_signals.empty:
                return {}

            return {
                "total_buy_signals": len(buy_signals),
                "avg_confidence": buy_signals.get("pred_confidence", pd.Series()).mean(),
                "avg_score": buy_signals.get("expected_move_score", pd.Series()).abs().mean(),
                "confidence_distribution": {
                    "min": buy_signals.get("pred_confidence", pd.Series()).min(),
                    "max": buy_signals.get("pred_confidence", pd.Series()).max(),
                    "median": buy_signals.get("pred_confidence", pd.Series()).median(),
                },
            }
        except Exception:
            return {}

    def _generate_recommendations(
        self,
        total_trades: int,
        win_rate: float,
        avg_pnl: float,
        total_pnl: float,
        signals_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate threshold adjustment recommendations."""
        recommendations = {
            "confidence_threshold": DEFAULT_THRESHOLDS.min_confidence,
            "score_threshold": DEFAULT_THRESHOLDS.min_abs_score,
            "reasoning": [],
            "confidence": "LOW",  # LOW, MEDIUM, HIGH
        }

        # Need sufficient data
        if total_trades < self.min_trades_for_adjustment:
            recommendations["reasoning"].append(
                f"Insufficient trades ({total_trades} < {self.min_trades_for_adjustment}) for reliable adjustment"
            )
            return recommendations

        # Analyze performance
        if win_rate > 60 and avg_pnl > 2.0:
            # Good performance - could slightly relax thresholds
            recommendations["confidence_threshold"] = max(0.70, DEFAULT_THRESHOLDS.min_confidence - 0.05)
            recommendations["score_threshold"] = max(0.20, DEFAULT_THRESHOLDS.min_abs_score - 0.05)
            recommendations["reasoning"].append(
                f"Good performance (win_rate={win_rate:.1f}%, avg_pnl={avg_pnl:.2f}%) - consider slight relaxation"
            )
            recommendations["confidence"] = "MEDIUM"
        elif win_rate < 40 or avg_pnl < -1.0:
            # Poor performance - tighten thresholds
            recommendations["confidence_threshold"] = min(0.90, DEFAULT_THRESHOLDS.min_confidence + 0.05)
            recommendations["score_threshold"] = min(0.40, DEFAULT_THRESHOLDS.min_abs_score + 0.05)
            recommendations["reasoning"].append(
                f"Poor performance (win_rate={win_rate:.1f}%, avg_pnl={avg_pnl:.2f}%) - tighten thresholds"
            )
            recommendations["confidence"] = "HIGH"
        else:
            # Moderate performance - keep current
            recommendations["reasoning"].append(
                f"Moderate performance (win_rate={win_rate:.1f}%, avg_pnl={avg_pnl:.2f}%) - keep current thresholds"
            )
            recommendations["confidence"] = "MEDIUM"

        # Consider signal distribution
        if signals_analysis:
            avg_conf = signals_analysis.get("avg_confidence", 0.0)
            if avg_conf > 0.85:
                recommendations["reasoning"].append(f"High average confidence ({avg_conf:.3f}) - could relax slightly")
            elif avg_conf < 0.70:
                recommendations["reasoning"].append(f"Low average confidence ({avg_conf:.3f}) - keep strict thresholds")

        return recommendations

    def save_recommendations(self, recommendations: Dict[str, Any]) -> bool:
        """Save threshold recommendations to JSON."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        output = {
            "generated_at": datetime.utcnow().isoformat(),
            "current_thresholds": {
                "min_confidence": DEFAULT_THRESHOLDS.min_confidence,
                "min_abs_score": DEFAULT_THRESHOLDS.min_abs_score,
            },
            "recommendations": recommendations,
        }

        try:
            with THRESHOLDS_RECOMMENDED_JSON.open("w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
            return True
        except Exception as e:
            print(f"[ADJUSTER] Failed to save recommendations: {e}")
            return False

    def apply_recommendations(self, recommendations: Dict[str, Any]) -> bool:
        """
        Apply threshold recommendations (only if auto-adjust is enabled).

        Currently DISABLED for safety.
        """
        if not self.auto_adjust_enabled:
            print("[ADJUSTER] Auto-adjustment is DISABLED. Recommendations saved but not applied.")
            return False

        # Apply recommendations
        DEFAULT_THRESHOLDS.min_confidence = recommendations.get(
            "confidence_threshold", DEFAULT_THRESHOLDS.min_confidence
        )
        DEFAULT_THRESHOLDS.min_abs_score = recommendations.get("score_threshold", DEFAULT_THRESHOLDS.min_abs_score)

        # Save updated thresholds
        return self.save_recommendations(recommendations)


def main() -> None:
    """Main entry point for auto threshold adjuster."""
    print("=== ANGEL ONE INDEX OPTIONS - AUTO THRESHOLD ADJUSTER ===")
    print("[INFO] Auto-adjustment is DISABLED. Generating recommendations only.\n")

    adjuster = AutoThresholdAdjuster()
    result = adjuster.analyze_performance(days=7)

    if result["status"] == "SUCCESS":
        print("=== PERFORMANCE ANALYSIS ===")
        analysis = result["analysis"]
        print(f"Total trades: {analysis['total_trades']}")
        print(f"Win rate: {analysis['win_rate']:.1f}%")
        print(f"Average PnL: {analysis['avg_pnl']:.2f}%")
        print(f"Total PnL: {analysis['total_pnl']:.2f}%")

        print("\n=== RECOMMENDATIONS ===")
        rec = result["recommendations"]
        print(
            f"Recommended confidence: {rec['confidence_threshold']:.2f} (current: {DEFAULT_THRESHOLDS.min_confidence:.2f})"
        )
        print(f"Recommended score: {rec['score_threshold']:.2f} (current: {DEFAULT_THRESHOLDS.min_abs_score:.2f})")
        print(f"Confidence level: {rec['confidence']}")
        print("\nReasoning:")
        for reason in rec["reasoning"]:
            print(f"  - {reason}")

        # Save recommendations
        adjuster.save_recommendations(rec)
        print(f"\n[SAVE] Recommendations saved to: {THRESHOLDS_RECOMMENDED_JSON}")
    else:
        print(f"[INFO] {result.get('message', 'Analysis not available')}")


if __name__ == "__main__":
    main()
