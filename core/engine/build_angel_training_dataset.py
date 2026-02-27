import os
import sys
from datetime import datetime

import pandas as pd

# --------------- Path setup ---------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.utils.logger import logger

LIVE_CSV = os.path.join(ROOT_DIR, "storage", "live", "angel_index_options_watch.csv")


def _load_live_data() -> pd.DataFrame | None:
    if not os.path.exists(LIVE_CSV):
        print(f"[ERROR] Live CSV not found: {LIVE_CSV}")
        return None

    try:
        df = pd.read_csv(LIVE_CSV)
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {e}")
        return None

    if df.empty:
        print("[ERROR] Live CSV is empty.")
        return None

    required = ["underlying", "expiry", "strike", "side", "ltp", "spot", "symbol", "ts"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"[ERROR] Missing columns in live CSV: {missing}")
        return None

    # Parse timestamp + numeric
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
    df["ltp"] = pd.to_numeric(df["ltp"], errors="coerce")
    df["spot"] = pd.to_numeric(df["spot"], errors="coerce")

    df = df.dropna(subset=["ts", "strike", "ltp", "spot"])

    # Sort for time-series ops
    df = df.sort_values(["underlying", "expiry", "strike", "side", "ts"])
    return df


def _add_core_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Core per-row features: moneyness, distance to ATM, basic momentum & volatility,
    and spot movement.
    """
    df = df.copy()

    # --- Moneyness / distance from ATM ---
    df["moneyness"] = (df["spot"] - df["strike"]) / df["spot"].replace(0, pd.NA)
    df["atm_dist_abs"] = (df["spot"] - df["strike"]).abs()
    df["atm_dist_pct"] = df["atm_dist_abs"] / df["spot"].replace(0, pd.NA)

    # --- Per-contract time series (underlying+symbol+side) ---
    g = df.groupby(["underlying", "symbol", "side"])

    df["ltp_prev"] = g["ltp"].shift(1)
    df["ltp_chg_1"] = df["ltp"] - df["ltp_prev"]
    df["ltp_chg_1_pct"] = df["ltp_chg_1"] / df["ltp_prev"].replace(0, pd.NA)

    # rolling mean/std for option price
    df["ltp_roll_mean_3"] = g["ltp"].rolling(3, min_periods=2).mean().reset_index(level=[0, 1, 2], drop=True)
    df["ltp_roll_std_5"] = g["ltp"].rolling(5, min_periods=2).std().reset_index(level=[0, 1, 2], drop=True)

    # --- Spot movement per underlying ---
    ug = df.groupby("underlying")
    df["spot_prev"] = ug["spot"].shift(1)
    df["spot_chg_1"] = df["spot"] - df["spot_prev"]
    df["spot_chg_1_pct"] = df["spot_chg_1"] / df["spot_prev"].replace(0, pd.NA)

    df["spot_roll_std_5"] = ug["spot"].rolling(5, min_periods=2).std().reset_index(level=0, drop=True)

    return df


def _add_ce_pe_pair_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Features that require both CE and PE at same (underlying, expiry, strike, ts).
    """
    df = df.copy()

    # pivot to wide: CE and PE columns
    pivot_cols = ["underlying", "expiry", "strike", "ts", "spot"]
    wide = df.pivot_table(index=pivot_cols, columns="side", values="ltp", aggfunc="last")

    # Ensure both columns exist
    for side in ["CE", "PE"]:
        if side not in wide.columns:
            wide[side] = pd.NA

    wide = wide.reset_index()
    wide.columns.name = None

    # CE/PE pair features
    wide["ce_pe_diff"] = wide["CE"] - wide["PE"]
    wide["ce_pe_sum"] = wide["CE"] + wide["PE"]
    wide["ce_pe_ratio"] = wide["CE"] / wide["PE"].replace(0, pd.NA)

    # premium as % of spot
    wide["ce_prem_spot_pct"] = wide["CE"] / wide["spot"].replace(0, pd.NA)
    wide["pe_prem_spot_pct"] = wide["PE"] / wide["spot"].replace(0, pd.NA)

    # rename columns to avoid clashes
    add_cols = [
        "ce_pe_diff",
        "ce_pe_sum",
        "ce_pe_ratio",
        "ce_prem_spot_pct",
        "pe_prem_spot_pct",
    ]

    # merge back on key
    df = df.merge(
        wide[pivot_cols + add_cols],
        on=pivot_cols,
        how="left",
    )

    return df


def _add_forward_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add future returns over multiple horizons (1,2,4,6 steps).
    One step ~ your sampling interval (e.g. 30 seconds).
    """
    df = df.copy()
    g = df.groupby(["underlying", "symbol", "side"])

    for h in [1, 2, 4, 6]:
        fwd_ltp = g["ltp"].shift(-h)
        col = f"fwd_ret_{h}"
        df[col] = (fwd_ltp - df["ltp"]) / df["ltp"].replace(0, pd.NA)

    return df


def _add_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create:
      - label_5class: STRONG_BUY / BUY / HOLD / SELL / STRONG_SELL
      - label_3class: BUY / SELL / HOLD  (for training compatibility)
    Based on mid-horizon forward return fwd_ret_2.
    """
    df = df.copy()

    horizon_col = "fwd_ret_2"
    if horizon_col not in df.columns:
        print("[ERROR] Missing forward return column for labels.")
        return df

    # Slightly tighter thresholds (0.3% / 0.7%) for richer classes
    thr_buy_weak = 0.003  # +0.3%
    thr_buy_strong = 0.007  # +0.7%
    thr_sell_weak = -0.003  # -0.3%
    thr_sell_strong = -0.007  # -0.7%

    def _label5(x):
        if pd.isna(x):
            return None
        if x >= thr_buy_strong:
            return "STRONG_BUY"
        if x >= thr_buy_weak:
            return "BUY"
        if x <= thr_sell_strong:
            return "STRONG_SELL"
        if x <= thr_sell_weak:
            return "SELL"
        return "HOLD"

    df["label_5class"] = df[horizon_col].apply(_label5)

    # Map into 3 major classes
    def _label3(c):
        if c in ("STRONG_BUY", "BUY"):
            return "BUY"
        if c in ("STRONG_SELL", "SELL"):
            return "SELL"
        if c == "HOLD":
            return "HOLD"
        return None

    df["label_3class"] = df["label_5class"].apply(_label3)

    # Drop rows where we cannot compute forward return / label
    df = df.dropna(subset=[horizon_col, "label_3class"])

    return df


def main():
    logger.info("=== Build Angel One index options training dataset (v2) ===")
    print(f"Reading live data from: {LIVE_CSV}")

    df = _load_live_data()
    if df is None:
        logger.error("Live data load failed; aborting.")
        return

    print(f"Total raw rows loaded: {len(df)}")

    # -------- FEATURES --------
    df_feat = _add_core_features(df)
    df_feat = _add_ce_pe_pair_features(df_feat)
    df_feat = _add_forward_returns(df_feat)
    df_feat = _add_labels(df_feat)

    if df_feat.empty:
        print("[WARN] After label derivation, no rows left (likely not enough history or all HOLD).")
        print("       Let the live loop (option 7) run longer during market hours, then rerun this.")
        return

    # Columns to keep for training
    feature_cols = [
        "underlying",
        "symbol",
        "side",
        "expiry",
        "ts",
        "spot",
        "strike",
        "ltp",
        "moneyness",
        "atm_dist_abs",
        "atm_dist_pct",
        "ltp_chg_1",
        "ltp_chg_1_pct",
        "ltp_roll_mean_3",
        "ltp_roll_std_5",
        "spot_chg_1",
        "spot_chg_1_pct",
        "spot_roll_std_5",
        "ce_pe_diff",
        "ce_pe_sum",
        "ce_pe_ratio",
        "ce_prem_spot_pct",
        "pe_prem_spot_pct",
        "fwd_ret_1",
        "fwd_ret_2",
        "fwd_ret_4",
        "fwd_ret_6",
        "label_5class",
        "label_3class",
    ]

    feature_cols = [c for c in feature_cols if c in df_feat.columns]

    train_df = df_feat[feature_cols].dropna(subset=["label_3class"])

    if train_df.empty:
        print("[WARN] Training dataframe is empty after filtering; need more live data.")
        return

    # -------- SAVE --------
    out_dir = os.path.join(ROOT_DIR, "storage", "training")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "angel_index_options_training.csv")

    write_header = not os.path.exists(out_path)
    train_df.to_csv(out_path, mode="a", header=write_header, index=False)

    print(f"\nTraining dataset rows appended: {len(train_df)}")
    print(f"Output file: {out_path}")
    logger.info(f"Training dataset (v2) built and saved to: {out_path}")


if __name__ == "__main__":
    main()
