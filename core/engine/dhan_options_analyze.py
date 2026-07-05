import os
import sys
from datetime import datetime

import pandas as pd

# ---------------- Path setup ----------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.utils.logger import logger

LIVE_CSV = os.path.join(ROOT_DIR, "storage", "live", "dhan_index_options_watch.csv")


def _load_live_csv() -> pd.DataFrame | None:
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

    # Ensure expected columns
    required = ["underlying", "expiry", "strike", "side", "ltp", "spot", "ts"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"[ERROR] Missing columns in CSV: {missing}")
        return None

    # Parse timestamp
    try:
        df["ts"] = pd.to_datetime(df["ts"])
    except Exception:
        pass

    return df


def _compute_atm_pairs(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each (underlying, ts) pick ATM CE and ATM PE (nearest strike to spot).
    Returns a DataFrame with one row per underlying+ts containing:
      ts, underlying, expiry, spot,
      strike_ce, ltp_ce, strike_pe, ltp_pe,
      ce_minus_pe, ce_pe_ratio
    """
    df = df.copy()

    # distance from spot
    df["dist"] = (df["strike"] - df["spot"]).abs()

    # separate CE and PE and pick nearest strike
    ce = df[df["side"] == "CE"].copy()
    pe = df[df["side"] == "PE"].copy()

    if ce.empty or pe.empty:
        return pd.DataFrame()

    ce_atm = ce.sort_values(["underlying", "ts", "dist"]).groupby(["underlying", "ts"]).head(1)
    pe_atm = pe.sort_values(["underlying", "ts", "dist"]).groupby(["underlying", "ts"]).head(1)

    ce_atm = ce_atm.rename(
        columns={
            "expiry": "expiry_ce",
            "strike": "strike_ce",
            "ltp": "ltp_ce",
        }
    )[["underlying", "ts", "expiry_ce", "spot", "strike_ce", "ltp_ce"]]

    pe_atm = pe_atm.rename(
        columns={
            "expiry": "expiry_pe",
            "strike": "strike_pe",
            "ltp": "ltp_pe",
        }
    )[["underlying", "ts", "expiry_pe", "strike_pe", "ltp_pe"]]

    merged = pd.merge(
        ce_atm,
        pe_atm,
        on=["underlying", "ts"],
        how="inner",
        suffixes=("", "_pe"),
    )

    # Prefer a single expiry column
    merged["expiry"] = merged["expiry_ce"].fillna(merged["expiry_pe"])
    merged.drop(columns=["expiry_ce", "expiry_pe"], inplace=True)

    # Basic features
    merged["ce_minus_pe"] = merged["ltp_ce"] - merged["ltp_pe"]
    merged["ce_pe_ratio"] = merged["ltp_ce"] / merged["ltp_pe"].replace(0, pd.NA)

    # Sort
    merged = merged.sort_values(["underlying", "ts"])
    return merged


def _compute_momentum(features: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple momentum features comparing last vs previous snapshot for each underlying.
    """
    if features.empty:
        return features

    df = features.copy()
    df = df.sort_values(["underlying", "ts"])

    # group by underlying to compute deltas
    df["ltp_ce_prev"] = df.groupby("underlying")["ltp_ce"].shift(1)
    df["ltp_pe_prev"] = df.groupby("underlying")["ltp_pe"].shift(1)
    df["spot_prev"] = df.groupby("underlying")["spot"].shift(1)

    df["d_ce"] = df["ltp_ce"] - df["ltp_ce_prev"]
    df["d_pe"] = df["ltp_pe"] - df["ltp_pe_prev"]
    df["d_spot"] = df["spot"] - df["spot_prev"]

    # percentage changes
    df["d_ce_pct"] = df["d_ce"] / df["ltp_ce_prev"].replace(0, pd.NA)
    df["d_pe_pct"] = df["d_pe"] / df["ltp_pe_prev"].replace(0, pd.NA)
    df["d_spot_pct"] = df["d_spot"] / df["spot_prev"].replace(0, pd.NA)

    return df


def _derive_signal(row: pd.Series) -> str:
    """
    Very simple, non-AI signal:
      - Bullish if CE rising, PE falling, spot rising
      - Bearish if CE falling, PE rising, spot falling
      - Otherwise Neutral
    """
    d_ce = row.get("d_ce", 0) or 0
    d_pe = row.get("d_pe", 0) or 0
    d_spot = row.get("d_spot", 0) or 0

    # Tolerances to avoid noise
    eps_ce = 0.5
    eps_pe = 0.5
    eps_spot = 1.0

    if d_ce > eps_ce and d_pe < -eps_pe and d_spot > eps_spot:
        return "BULLISH"
    if d_ce < -eps_ce and d_pe > eps_pe and d_spot < -eps_spot:
        return "BEARISH"
    return "NEUTRAL"


def main():
    logger.info("=== Dhan Index Options ANALYZE (simple signals) ===")
    print(f"Reading live CSV: {LIVE_CSV}")

    df = _load_live_csv()
    if df is None:
        logger.error("Live CSV missing or invalid; aborting analysis.")
        return

    # Ensure numeric types
    for col in ["strike", "ltp", "spot"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Compute ATM CE/PE pairs
    atm = _compute_atm_pairs(df)
    if atm.empty:
        print("[ERROR] Could not derive ATM pairs (CE/PE).")
        return

    # Add momentum features
    feat = _compute_momentum(atm)

    # For each underlying, pick latest row
    latest = feat.sort_values(["underlying", "ts"]).groupby("underlying").tail(1).copy()

    if latest.empty:
        print("[ERROR] No latest rows found.")
        return

    # Derive simple signals
    latest["signal"] = latest.apply(_derive_signal, axis=1)

    # Keep key columns
    cols = [
        "ts",
        "underlying",
        "expiry",
        "spot",
        "strike_ce",
        "ltp_ce",
        "strike_pe",
        "ltp_pe",
        "ce_minus_pe",
        "ce_pe_ratio",
        "d_ce",
        "d_pe",
        "d_spot",
        "d_ce_pct",
        "d_pe_pct",
        "d_spot_pct",
        "signal",
    ]
    cols = [c for c in cols if c in latest.columns]

    latest = latest[cols].sort_values("underlying")

    print("\n=== SIMPLE INDEX OPTIONS SIGNALS (based on last two snapshots) ===")
    print(latest.to_string(index=False))

    # Optionally write features to disk for future AI use
    feat_dir = os.path.join(ROOT_DIR, "storage", "features")
    os.makedirs(feat_dir, exist_ok=True)
    feat_path = os.path.join(feat_dir, "dhan_index_options_features.csv")

    write_header = not os.path.exists(feat_path)
    feat.to_csv(feat_path, mode="a", header=write_header, index=False)

    print(f"\nFull feature history appended to: {feat_path}")
    logger.info("Dhan index options analysis completed.")


if __name__ == "__main__":
    main()
