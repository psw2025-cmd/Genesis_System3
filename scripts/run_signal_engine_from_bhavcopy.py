"""
Signal Engine Bhavcopy Runner

Daily scheduled at 18:45 IST (15 min after bhavcopy download).
Transforms today's NSE FO bhavcopy into the option chain snapshot
format expected by run_signal_engine(), then writes per-option
signals to storage/live/dhan_index_ai_signals.csv.

This activates the dead 15% ml_confidence weight in GainRankEngine
without requiring a live Dhan Data API subscription.

Output CSV columns include: ts, underlying, expiry, strike, side,
ltp, spot, final_score, signal, expected_move_score, prob_BUY_CE
"""

import glob
import logging
import os
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger

BHAVCOPY_DIR = ROOT_DIR / "storage" / "bhavcopy"
LIVE_DIR = ROOT_DIR / "storage" / "live"
SIGNALS_CSV = LIVE_DIR / "dhan_index_ai_signals.csv"

# Only these underlyings flow into GainRankEngine ranking
INDEX_SYMBOLS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"}

# Max strikes per expiry per underlying to keep df manageable (ATM ± N)
ATM_BAND = 10  # include 10 strikes above and below ATM


def _latest_bhavcopy() -> Path | None:
    files = sorted(glob.glob(str(BHAVCOPY_DIR / "*_fo_bhavcopy.csv")))
    return Path(files[-1]) if files else None


def _load_bhavcopy(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    # Keep only index futures + options
    df = df[df["TckrSymb"].isin(INDEX_SYMBOLS)].copy()
    # Keep only options (OptnTp is CE or PE; futures have NaN/blank)
    df = df[df["OptnTp"].isin(["CE", "PE"])].copy()
    # Drop zero-LTP rows (untradeable strikes)
    df = df[df["ClsPric"].notna() & (df["ClsPric"] > 0)].copy()
    return df


def _nearest_expiry(group: pd.DataFrame) -> str:
    """Return the nearest expiry date string from the group."""
    today = date.today()
    expiries = pd.to_datetime(group["XpryDt"], errors="coerce").dropna()
    future_expiries = expiries[expiries.dt.date >= today]
    if future_expiries.empty:
        return str(expiries.max().date())
    return str(future_expiries.min().date())


def _atm_filter(group: pd.DataFrame, spot: float) -> pd.DataFrame:
    """Return ATM ± ATM_BAND strikes for the nearest expiry only."""
    nearest = _nearest_expiry(group)
    exp_group = group[pd.to_datetime(group["XpryDt"], errors="coerce").dt.date.astype(str) == nearest]
    if exp_group.empty:
        return exp_group
    strikes = exp_group["StrkPric"].dropna().unique()
    if len(strikes) == 0:
        return exp_group
    atm = float(min(strikes, key=lambda s: abs(s - spot)))
    sorted_strikes = sorted(set(strikes))
    atm_idx = sorted_strikes.index(atm)
    low = max(0, atm_idx - ATM_BAND)
    high = min(len(sorted_strikes) - 1, atm_idx + ATM_BAND)
    valid_strikes = set(sorted_strikes[low : high + 1])
    return exp_group[exp_group["StrkPric"].isin(valid_strikes)]


def bhavcopy_to_snapshot(bhavcopy_path: Path) -> pd.DataFrame:
    """
    Transform bhavcopy rows → df_snap format for run_signal_engine().

    Output columns: ts, underlying, expiry, strike, side, ltp, spot
    """
    raw = _load_bhavcopy(bhavcopy_path)
    if raw.empty:
        logger.warning("No index option rows in bhavcopy: %s", bhavcopy_path.name)
        return pd.DataFrame()

    ts_now = datetime.now().isoformat(timespec="seconds")
    rows = []

    for symbol, grp in raw.groupby("TckrSymb"):
        spot_vals = grp["UndrlygPric"].dropna()
        if spot_vals.empty:
            logger.warning("%s: no spot price in bhavcopy, skipping", symbol)
            continue
        spot = float(spot_vals.median())
        filtered = _atm_filter(grp, spot)
        if filtered.empty:
            continue

        for _, row in filtered.iterrows():
            expiry_raw = str(row.get("XpryDt", "")).strip()
            strike = float(row["StrkPric"])
            side = str(row["OptnTp"]).strip()
            ltp = float(row["ClsPric"])
            rows.append(
                {
                    "ts": ts_now,
                    "underlying": str(symbol),
                    "expiry": expiry_raw,
                    "strike": strike,
                    "side": side,
                    "ltp": ltp,
                    "spot": spot,
                }
            )

    if not rows:
        logger.warning("No valid option rows built from bhavcopy")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    logger.info(
        "Bhavcopy → snapshot: %d rows for %s",
        len(df),
        ", ".join(df["underlying"].unique()),
    )
    return df


def run(bhavcopy_path: Path | None = None) -> bool:
    """
    Main entry point. Returns True on success.
    """
    if bhavcopy_path is None:
        bhavcopy_path = _latest_bhavcopy()
    if bhavcopy_path is None:
        logger.error("No bhavcopy file found in %s", BHAVCOPY_DIR)
        return False

    logger.info("Using bhavcopy: %s", bhavcopy_path.name)

    df_snap = bhavcopy_to_snapshot(bhavcopy_path)
    if df_snap.empty:
        logger.error("Empty snapshot — signal engine not run")
        return False

    try:
        from core.engine.system3_signal_engine import run_signal_engine

        df_signals = run_signal_engine(df_snap, enable_safety_checks=False)
    except Exception as exc:
        logger.error("Signal engine failed: %s", exc, exc_info=True)
        return False

    if df_signals.empty:
        logger.warning("Signal engine returned empty DataFrame")
        return False

    counts = df_signals["signal"].value_counts().to_dict() if "signal" in df_signals.columns else {}
    prob_cols = [c for c in df_signals.columns if c.startswith("prob_")]
    logger.info(
        "Signals written to %s | rows=%d signals=%s prob_cols=%s",
        SIGNALS_CSV,
        len(df_signals),
        counts,
        prob_cols,
    )
    return True


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Run signal engine using latest bhavcopy")
    ap.add_argument("--bhavcopy", type=Path, default=None, help="Path to specific bhavcopy CSV")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    success = run(bhavcopy_path=args.bhavcopy)
    sys.exit(0 if success else 1)
