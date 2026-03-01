"""
Order Flow Imbalance (OFI) Engine
Calculates bid-ask pressure and buying/selling imbalance for option chains.
Standard institutional 'Edge' for HFT and advanced AI trading.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any

class OrderFlowEngine:
    def __init__(self):
        self.last_state = {} # Stores previous tick data for delta calculation

    def calculate_ofi_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the Order Flow Imbalance Score for each contract.
        Score > 0: Buying Pressure
        Score < 0: Selling Pressure
        """
        if df.empty or "bid" not in df.columns or "ask" not in df.columns:
            df["ofi_score"] = 0.0
            return df

        # Ensure numeric types
        df["bid"] = pd.to_numeric(df["bid"], errors='coerce').fillna(0)
        df["ask"] = pd.to_numeric(df["ask"], errors='coerce').fillna(0)
        df["bid_qty"] = pd.to_numeric(df.get("bid_qty", 0), errors='coerce').fillna(0)
        df["ask_qty"] = pd.to_numeric(df.get("ask_qty", 0), errors='coerce').fillna(0)
        df["volume"] = pd.to_numeric(df.get("volume", 0), errors='coerce').fillna(0)

        # 1. Static Imbalance (Snap-shot)
        # Higher bid qty vs ask qty indicates support/buying pressure
        df["static_imbalance"] = (df["bid_qty"] - df["ask_qty"]) / (df["bid_qty"] + df["ask_qty"] + 1)

        # 2. Spread Quality
        # Narrower spread = higher confidence in the current price
        df["spread"] = df["ask"] - df["bid"]
        df["spread_pct"] = df["spread"] / (df["bid"] + 1e-9)

        # 3. Final OFI Score Calculation
        # We combine static imbalance with a volume multiplier
        # High volume + high imbalance = Strong Institutional Signal
        df["ofi_score"] = df["static_imbalance"] * np.log1p(df["volume"])
        
        # Normalize to [-1, 1]
        max_ofi = df["ofi_score"].abs().max()
        if max_ofi > 0:
            df["ofi_score"] = df["ofi_score"] / max_ofi

        return df

    def get_aggregate_market_pressure(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculates the overall buying/selling pressure for an underlying"""
        if df.empty or "ofi_score" not in df.columns:
            return {"total_pressure": 0.0, "ce_pressure": 0.0, "pe_pressure": 0.0}

        ce_mask = df["side"].str.upper() == "CE"
        pe_mask = df["side"].str.upper() == "PE"

        ce_pressure = df[ce_mask]["ofi_score"].mean() if ce_mask.any() else 0.0
        pe_pressure = df[pe_mask]["ofi_score"].mean() if pe_mask.any() else 0.0

        return {
            "total_pressure": float(df["ofi_score"].mean()),
            "ce_pressure": float(ce_pressure),
            "pe_pressure": float(pe_pressure),
            "imbalance_ratio": float(ce_pressure / (pe_pressure + 1e-9) if pe_pressure != 0 else 1.0)
        }

# Global instance
_ofi_engine = OrderFlowEngine()

def get_ofi_engine() -> OrderFlowEngine:
    return _ofi_engine
