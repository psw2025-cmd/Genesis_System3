# core/engine/generate_synthetic_dhan_training.py

import os
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from core.engine.dhan_features import add_advanced_features


UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _training_csv_path(root: Path) -> Path:
    return root / "storage" / "training" / "dhan_index_options_training.csv"


def _base_spot(underlying: str) -> float:
    """Approximate base spot levels for indices."""
    base_map = {
        "NIFTY": 22000.0,
        "BANKNIFTY": 48000.0,
        "FINNIFTY": 19500.0,
        "MIDCPNIFTY": 13500.0,
        "SENSEX": 73000.0,
    }
    return base_map.get(underlying, 20000.0)


def _round_to_step(x: float, step: float = 50.0) -> float:
    return round(x / step) * step


def _simulate_for_underlying(
    underlying: str,
    n_rows: int = 600,
    seed: int | None = None,
) -> pd.DataFrame:
    """
    Build synthetic index options rows for a single underlying.

    Columns produced (minimum required for training):
      ts, underlying, expiry, strike, side, ltp, spot, label
    """
    if seed is not None:
        np.random.seed(seed)

    base = _base_spot(underlying)

    # Generate a simple intraday time axis (1-minute steps)
    start_ts = datetime(2025, 1, 1, 9, 15, 0)
    ts_list = [start_ts + timedelta(minutes=i) for i in range(n_rows)]

    # Simulate spot as noisy random walk around base
    spot = np.zeros(n_rows)
    spot[0] = base
    for i in range(1, n_rows):
        # small random walk noise ~ +/- 0.5%
        shock = np.random.normal(loc=0.0, scale=0.002)  # 0.2% sigma
        spot[i] = spot[i - 1] * (1.0 + shock)

    # Side: CE / PE roughly 50-50
    side = np.random.choice(["CE", "PE"], size=n_rows)

    # Strikes around spot, rounded to 50 or 25 depending on index
    step = 50.0
    if underlying in ("NIFTY", "FINNIFTY", "MIDCPNIFTY"):
        step = 50.0
    elif underlying in ("BANKNIFTY", "SENSEX"):
        step = 100.0

    strikes = []
    for s in spot:
        # pick offset in -3..+3 steps
        offset_steps = np.random.randint(-3, 4)
        strikes.append(_round_to_step(s + offset_steps * step, step))

    strikes = np.array(strikes, dtype=float)

    # ltp: depends on moneyness + noise
    ltps = []
    for i in range(n_rows):
        s = spot[i]
        k = strikes[i]
        sd = side[i]
        # intrinsic
        if sd == "CE":
            intrinsic = max(s - k, 0.0)
        else:
            intrinsic = max(k - s, 0.0)
        time_value = max(0.1 * step, 0.03 * s * np.random.rand())
        l = intrinsic + time_value
        l *= np.random.uniform(0.7, 1.3)
        ltps.append(max(l, 1.0))

    ltps = np.array(ltps)

    # expiry just a synthetic date string, not used by model heavily
    # e.g. nearest Friday for weekly for NIFTY, but keep it simple:
    expiry_base = datetime(2025, 1, 30)
    expiries = np.array(
        [(expiry_base + timedelta(days=int(i // (n_rows / 3)) * 7)).strftime("%d%b%Y").upper() for i in range(n_rows)]
    )

    # Labels:
    #  - HOLD most of time
    #  - BUY_CE when CE is clearly ITM (spot > strike + threshold)
    #  - BUY_PE when PE is clearly ITM (spot < strike - threshold)
    labels = []
    for i in range(n_rows):
        s = spot[i]
        k = strikes[i]
        sd = side[i]
        threshold = 0.004 * s  # ~0.4%

        if sd == "CE":
            if s > k + threshold:
                labels.append("BUY_CE")
            else:
                labels.append("HOLD")
        else:  # PE
            if s < k - threshold:
                labels.append("BUY_PE")
            else:
                labels.append("HOLD")

    df = pd.DataFrame(
        {
            "ts": ts_list,
            "underlying": underlying,
            "expiry": expiries,
            "strike": strikes,
            "side": side,
            "ltp": ltps,
            "spot": spot,
            "label": labels,
        }
    )

    # Optional extra features that training code may expect; if missing,
    # train_dhan_models._ensure_feature_columns will fill defaults.
    # Still, we add some realistic ones.
    df["moneyness"] = np.where(
        df["side"] == "CE",
        df["spot"] - df["strike"],
        df["strike"] - df["spot"],
    )
    df["atm_dist_abs"] = (df["spot"] - df["strike"]).abs()
    df["atm_dist_pct"] = df["atm_dist_abs"] / df["spot"].clip(lower=1.0)

    # For synthetic data we don't have history; just set small random noise
    df["ltp_chg_1_pct"] = np.random.normal(0.0, 0.01, size=n_rows)
    df["spot_chg_1_pct"] = np.random.normal(0.0, 0.005, size=n_rows)
    df["ltp_roll_std_5"] = np.random.uniform(0.5, 2.5, size=n_rows)
    df["spot_roll_std_5"] = np.random.uniform(0.2, 1.5, size=n_rows)
    df["ce_pe_diff"] = np.random.uniform(-50.0, 50.0, size=n_rows)

    # Add ce_pe_ratio: calculate from paired CE/PE rows where possible
    # For synthetic data, we'll create a realistic ratio based on moneyness
    df["ce_pe_ratio"] = np.nan

    # Try to pair CE/PE rows with same strike, expiry, and ts
    for (exp, k, ts), group in df.groupby(["expiry", "strike", "ts"]):
        ce_rows = group[group["side"] == "CE"]
        pe_rows = group[group["side"] == "PE"]

        if len(ce_rows) > 0 and len(pe_rows) > 0:
            # Real pair exists - calculate actual ratio
            ce_ltp = ce_rows["ltp"].iloc[0]
            pe_ltp = pe_rows["ltp"].iloc[0]
            if pe_ltp > 0:
                ratio = ce_ltp / pe_ltp
                df.loc[ce_rows.index, "ce_pe_ratio"] = ratio
                df.loc[pe_rows.index, "ce_pe_ratio"] = ratio

    # Fill remaining NaN values with synthetic ratio based on moneyness
    ce_mask = df["side"] == "CE"
    pe_mask = df["side"] == "PE"
    nan_mask = df["ce_pe_ratio"].isna()

    # For CE rows without pairs: ratio tends to be higher when ITM
    ce_nan_mask = ce_mask & nan_mask
    if ce_nan_mask.any():
        moneyness_factor = (df.loc[ce_nan_mask, "spot"] - df.loc[ce_nan_mask, "strike"]) / df.loc[
            ce_nan_mask, "spot"
        ].clip(lower=1.0)
        df.loc[ce_nan_mask, "ce_pe_ratio"] = 1.0 + moneyness_factor * 2.0

    # For PE rows without pairs: ratio tends to be lower when ITM (inverse relationship)
    pe_nan_mask = pe_mask & nan_mask
    if pe_nan_mask.any():
        moneyness_factor = (df.loc[pe_nan_mask, "strike"] - df.loc[pe_nan_mask, "spot"]) / df.loc[
            pe_nan_mask, "spot"
        ].clip(lower=1.0)
        df.loc[pe_nan_mask, "ce_pe_ratio"] = 1.0 / (1.0 + moneyness_factor * 2.0)

    # Clip to reasonable range (0.1 to 10.0)
    df["ce_pe_ratio"] = df["ce_pe_ratio"].clip(lower=0.1, upper=10.0)

    return df


def main():
    root = _project_root()
    out_path = _training_csv_path(root)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("=== ANGEL ONE INDEX OPTIONS - SYNTHETIC TRAINING DATA ===")
    print(f"Project root: {root}")
    print(f"Output CSV  : {out_path}")

    all_dfs = []
    global_labels = []

    for u in UNDERLYINGS:
        df_u = _simulate_for_underlying(u, n_rows=600)
        all_dfs.append(df_u)
        global_labels.extend(df_u["label"].tolist())
        counts = df_u["label"].value_counts()
        print(f"[Synthetic] {u} -> rows {len(df_u)}, label counts:")
        print(counts)

    df_all = pd.concat(all_dfs, ignore_index=True)

    # Add advanced engineered features (non-breaking; adds extra columns)
    df_all = add_advanced_features(df_all)

    print("\n[Synthetic] Final label distribution:")
    print(df_all["label"].value_counts())

    # Ensure consistent column order
    cols_order = [
        "ts",
        "underlying",
        "expiry",
        "strike",
        "side",
        "ltp",
        "spot",
        "moneyness",
        "atm_dist_abs",
        "atm_dist_pct",
        "ltp_chg_1_pct",
        "spot_chg_1_pct",
        "ltp_roll_std_5",
        "spot_roll_std_5",
        "ce_pe_diff",
        "ce_pe_ratio",
        "label",
    ]
    # Keep only those that actually exist, in that order
    cols_order = [c for c in cols_order if c in df_all.columns]
    df_all = df_all[cols_order]

    df_all.to_csv(out_path, index=False)
    print("\n[Synthetic] Training CSV written successfully.")


if __name__ == "__main__":
    main()
