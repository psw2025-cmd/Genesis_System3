"""
Utility functions for calculating additional option chain columns.
"""

from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd


def add_calculated_columns(df: pd.DataFrame, fetch_timestamp: Optional[str] = None) -> pd.DataFrame:
    """
    Add calculated columns to option chain DataFrame.

    Args:
        df: DataFrame with option chain data
        fetch_timestamp: Optional fetch timestamp string (for days_to_expiry calculation)

    Returns:
        DataFrame with additional calculated columns
    """
    df = df.copy()

    # Ensure required columns exist
    required_cols = ["strike", "spot_price", "option_type", "ltp"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # 1. Intrinsic value
    def calc_intrinsic(row):
        try:
            spot = float(row["spot_price"]) if pd.notna(row["spot_price"]) else None
            strike = float(row["strike"]) if pd.notna(row["strike"]) else None
            opt_type = str(row["option_type"]).upper()

            if spot is None or strike is None:
                return None

            if opt_type == "CE":
                return max(0.0, spot - strike)
            else:  # PE
                return max(0.0, strike - spot)
        except (ValueError, TypeError):
            return None

    df["intrinsic_value"] = df.apply(calc_intrinsic, axis=1)

    # 2. Extrinsic value
    df["extrinsic_value"] = None
    mask = df["ltp"].notna() & df["intrinsic_value"].notna()
    df.loc[mask, "extrinsic_value"] = df.loc[mask, "ltp"] - df.loc[mask, "intrinsic_value"]
    # Note: Extrinsic value should be non-negative in theory, but can be negative if:
    # - LTP < intrinsic (market inefficiency or data timing issue)
    # - Spot price changed between intrinsic calc and LTP fetch
    # We keep the calculated value to maintain: intrinsic + extrinsic = ltp
    # Negative extrinsic indicates potential data quality issue but is mathematically correct

    # 3. Intrinsic percentage
    df["intrinsic_pct"] = None
    mask = df["ltp"].notna() & (df["ltp"] > 0) & df["intrinsic_value"].notna()
    df.loc[mask, "intrinsic_pct"] = (df.loc[mask, "intrinsic_value"] / df.loc[mask, "ltp"]) * 100.0

    # 4. ATM distance (absolute)
    df["atm_distance"] = None
    mask = df["strike"].notna() & df["spot_price"].notna()
    df.loc[mask, "atm_distance"] = abs(df.loc[mask, "strike"] - df.loc[mask, "spot_price"])

    # 5. ATM distance percentage
    df["atm_distance_pct"] = None
    mask = df["atm_distance"].notna() & df["spot_price"].notna() & (df["spot_price"] > 0)
    df.loc[mask, "atm_distance_pct"] = (df.loc[mask, "atm_distance"] / df.loc[mask, "spot_price"]) * 100.0

    # 6. Bid-ask spread
    df["bid_ask_spread"] = None
    if "bidPrice" in df.columns and "offerPrice" in df.columns:
        mask = df["bidPrice"].notna() & df["offerPrice"].notna()
        df.loc[mask, "bid_ask_spread"] = df.loc[mask, "offerPrice"] - df.loc[mask, "bidPrice"]

    # 7. Mid price
    df["mid_price"] = None
    if "bidPrice" in df.columns and "offerPrice" in df.columns:
        mask = df["bidPrice"].notna() & df["offerPrice"].notna()
        df.loc[mask, "mid_price"] = (df.loc[mask, "bidPrice"] + df.loc[mask, "offerPrice"]) / 2.0

    # 8. Bid-ask spread percentage
    df["bid_ask_spread_pct"] = None
    if "bid_ask_spread" in df.columns and "mid_price" in df.columns:
        mask = df["bid_ask_spread"].notna() & df["mid_price"].notna() & (df["mid_price"] > 0)
        df.loc[mask, "bid_ask_spread_pct"] = (df.loc[mask, "bid_ask_spread"] / df.loc[mask, "mid_price"]) * 100.0

    # 9. Volume/OI ratio
    df["volume_oi_ratio"] = None
    if "volume" in df.columns and "oi" in df.columns:
        mask = df["volume"].notna() & df["oi"].notna() & (df["oi"] > 0)
        df.loc[mask, "volume_oi_ratio"] = df.loc[mask, "volume"] / df.loc[mask, "oi"]

    # 10. Premium as % of strike
    df["premium_pct_of_strike"] = None
    mask = df["ltp"].notna() & df["strike"].notna() & (df["strike"] > 0)
    df.loc[mask, "premium_pct_of_strike"] = (df.loc[mask, "ltp"] / df.loc[mask, "strike"]) * 100.0

    # 11. Premium as % of spot
    df["premium_pct_of_spot"] = None
    mask = df["ltp"].notna() & df["spot_price"].notna() & (df["spot_price"] > 0)
    df.loc[mask, "premium_pct_of_spot"] = (df.loc[mask, "ltp"] / df.loc[mask, "spot_price"]) * 100.0

    # 12. Delta/Gamma ratio
    df["delta_gamma_ratio"] = None
    if "delta" in df.columns and "gamma" in df.columns:
        mask = df["delta"].notna() & df["gamma"].notna() & (df["gamma"] != 0)
        df.loc[mask, "delta_gamma_ratio"] = df.loc[mask, "delta"] / df.loc[mask, "gamma"]

    # 13. Days to expiry and time to expiry
    df["days_to_expiry"] = None
    df["time_to_expiry"] = None

    if "expiry_date" in df.columns:
        try:
            # Convert expiry_date to datetime
            df["expiry_date_dt"] = pd.to_datetime(df["expiry_date"], errors="coerce")

            # Use fetch_timestamp if provided, otherwise use current date
            if fetch_timestamp:
                try:
                    # Remove timezone suffix if present (e.g., "IST")
                    fetch_str = str(fetch_timestamp).replace(" IST", "").replace(" UTC", "").strip()
                    fetch_dt = pd.to_datetime(fetch_str)
                except:
                    fetch_dt = pd.Timestamp.now()
            else:
                # Try to get from fetch_date column if available
                if "fetch_date" in df.columns:
                    fetch_dt = pd.to_datetime(df["fetch_date"], errors="coerce")
                else:
                    fetch_dt = pd.Timestamp.now()

            # Calculate days to expiry
            mask = df["expiry_date_dt"].notna()
            if isinstance(fetch_dt, pd.Timestamp):
                df.loc[mask, "days_to_expiry"] = (df.loc[mask, "expiry_date_dt"] - fetch_dt).dt.days
            else:
                # If fetch_dt is a Series
                df.loc[mask, "days_to_expiry"] = (df.loc[mask, "expiry_date_dt"] - fetch_dt.loc[mask]).dt.days

            # Calculate time to expiry (in years)
            mask = df["days_to_expiry"].notna()
            df.loc[mask, "time_to_expiry"] = df.loc[mask, "days_to_expiry"] / 365.0

            # Clean up temporary column
            df = df.drop(columns=["expiry_date_dt"], errors="ignore")

        except Exception as e:
            # If calculation fails, leave as None
            pass

    # 14. Theta per day (normalized)
    df["theta_per_day"] = None
    if "theta" in df.columns and "days_to_expiry" in df.columns:
        mask = df["theta"].notna() & df["days_to_expiry"].notna() & (df["days_to_expiry"] > 0)
        df.loc[mask, "theta_per_day"] = df.loc[mask, "theta"] / df.loc[mask, "days_to_expiry"]

    # 15. Put-call spread (requires matching CE/PE pairs)
    # This is complex and requires grouping by strike, so we'll skip it for now
    # Can be added later as a post-processing step if needed

    return df
