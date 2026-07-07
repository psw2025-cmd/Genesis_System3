#!/usr/bin/env python3
"""
Advanced Prediction Model Enhancer
Enhances prediction models with continuous learning and multi-model ensemble
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

IST = pytz.timezone("Asia/Kolkata")


class AdvancedPredictionEnhancer:
    """Enhances prediction models with advanced features"""

    def __init__(self):
        self.models_dir = ROOT_DIR / "core" / "models"
        self.training_data_dir = ROOT_DIR / "storage" / "datasets"
        self.paper_trades_file = ROOT_DIR / "src" / "outputs" / "paper_trades_live.csv"

    def load_paper_trade_features(self) -> pd.DataFrame:
        """Extract features from paper trades for model training"""
        if not self.paper_trades_file.exists():
            return pd.DataFrame()

        try:
            df = pd.read_csv(self.paper_trades_file, on_bad_lines="skip", engine="python")

            # Extract features
            features = []
            for _, trade in df.iterrows():
                feature = {
                    "underlying": trade.get("underlying", ""),
                    "strike": trade.get("strike", 0),
                    "option_type": trade.get("option_type", ""),
                    "entry_price": trade.get("entry_price", 0),
                    "exit_price": trade.get("exit_price", 0),
                    "strategy": trade.get("strategy", ""),
                    "timestamp": trade.get("timestamp", ""),
                    "pnl": trade.get("realized_pnl", 0),
                    "pnl_pct": trade.get("realized_pnl_pct", 0),
                    "profitable": (
                        float(trade.get("realized_pnl", 0)) > 0 if pd.notna(trade.get("realized_pnl", 0)) else False
                    ),
                }
                features.append(feature)

            return pd.DataFrame(features)
        except Exception as e:
            print(f"Error loading paper trades: {e}")
            return pd.DataFrame()

    def calculate_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate advanced features for prediction"""
        if df.empty:
            return df

        # Add moneyness
        if "strike" in df.columns and "underlying" in df.columns:
            # Estimate spot price (would need real data)
            spot_estimates = {
                "NIFTY": 24000,
                "BANKNIFTY": 52000,
                "FINNIFTY": 22000,
                "MIDCPNIFTY": 12000,
                "SENSEX": 75000,
            }

            def calc_moneyness(row):
                underlying = str(row.get("underlying", "")).upper()
                strike = float(row.get("strike", 0))
                spot = spot_estimates.get(underlying, 24000)
                return strike / spot if spot > 0 else 1.0

            df["moneyness"] = df.apply(calc_moneyness, axis=1)

        # Add time-based features
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df["hour"] = df["timestamp"].dt.hour
            df["day_of_week"] = df["timestamp"].dt.dayofweek

        # Add PnL-based features
        if "pnl_pct" in df.columns:
            df["abs_pnl_pct"] = df["pnl_pct"].abs()
            df["pnl_category"] = pd.cut(
                df["pnl_pct"],
                bins=[-np.inf, -10, -5, 0, 5, 10, np.inf],
                labels=["Large Loss", "Medium Loss", "Small Loss", "Small Profit", "Medium Profit", "Large Profit"],
            )

        return df

    def generate_model_insights(self, df: pd.DataFrame) -> Dict:
        """Generate insights for model improvement"""
        if df.empty:
            return {}

        insights = {
            "total_trades": len(df),
            "profitable_trades": len(df[df.get("profitable", False) == True]) if "profitable" in df.columns else 0,
            "win_rate": 0,
            "avg_pnl": 0,
            "best_strategy": "",
            "best_underlying": "",
            "feature_importance": {},
        }

        if "profitable" in df.columns:
            insights["win_rate"] = df["profitable"].sum() / len(df) if len(df) > 0 else 0

        if "pnl" in df.columns:
            insights["avg_pnl"] = df["pnl"].mean() if len(df) > 0 else 0

        if "strategy" in df.columns and "profitable" in df.columns:
            strategy_perf = df.groupby("strategy")["profitable"].agg(["sum", "count"])
            if not strategy_perf.empty:
                strategy_win_rate = (strategy_perf["sum"] / strategy_perf["count"]).idxmax()
                insights["best_strategy"] = strategy_win_rate

        if "underlying" in df.columns and "profitable" in df.columns:
            underlying_perf = df.groupby("underlying")["profitable"].agg(["sum", "count"])
            if not underlying_perf.empty:
                underlying_win_rate = (underlying_perf["sum"] / underlying_perf["count"]).idxmax()
                insights["best_underlying"] = underlying_win_rate

        return insights

    def enhance_models(self):
        """Enhance prediction models"""
        print("[Enhancement] Enhancing prediction models...")

        # Load paper trade data
        df = self.load_paper_trade_features()

        # Save insights (even if empty structure) to prevent missing file warnings
        insights_file = ROOT_DIR / "storage" / "learning" / "model_insights.json"
        insights_file.parent.mkdir(parents=True, exist_ok=True)

        if df.empty:
            print("[Info] No paper trade data available yet - writing default insights template")
            default_insights = {
                "total_trades": 0,
                "profitable_trades": 0,
                "win_rate": 0.0,
                "avg_pnl": 0.0,
                "best_strategy": "N/A",
                "best_underlying": "N/A",
                "feature_importance": {},
                "status": "ok",
                "updated_at": datetime.now(IST).isoformat(),
            }
            with open(insights_file, "w") as f:
                json.dump(default_insights, f, indent=2)
            return default_insights

        print(f"[Info] Loaded {len(df)} paper trades")

        # Calculate advanced features
        df_enhanced = self.calculate_advanced_features(df)

        # Generate insights
        insights = self.generate_model_insights(df_enhanced)

        print(f"[Info] Win rate: {insights.get('win_rate', 0):.2%}")
        print(f"[Info] Average PnL: {insights.get('avg_pnl', 0):.2f}")
        print(f"[Info] Best strategy: {insights.get('best_strategy', 'N/A')}")
        print(f"[Info] Best underlying: {insights.get('best_underlying', 'N/A')}")

        with open(insights_file, "w") as f:
            json.dump(insights, f, indent=2, default=str)

        print("[OK] Model insights saved")

        return insights


if __name__ == "__main__":
    enhancer = AdvancedPredictionEnhancer()
    enhancer.enhance_models()
