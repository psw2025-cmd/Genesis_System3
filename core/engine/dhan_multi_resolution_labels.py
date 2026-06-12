from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd


def _label_from_return(ret_pct: float) -> str:
    """
    Map a forward return percentage to a 5-class label.
    Thresholds are conservative and can be tuned later.
    """
    if ret_pct >= 1.5:
        return "STRONG_BUY"
    if ret_pct >= 0.5:
        return "BUY"
    if ret_pct <= -1.5:
        return "STRONG_SELL"
    if ret_pct <= -0.5:
        return "SELL"
    return "HOLD"


def generate_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add multi-resolution forward labels based on option premium (ltp).

    Labels:
      - label_1: 1-step ahead
      - label_2: 2-step ahead
      - label_3: 3-step ahead
      - label_5: 5-step ahead

    The original training label columns (e.g. 'label', 'label_3class') are untouched.
    """
    if "ltp" not in df.columns:
        # Nothing to do
        return df

    work = df.copy()

    # Ensure we have a time ordering; prefer 'ts' if present
    time_col = "ts" if "ts" in work.columns else None

    # Compute forward returns grouped by underlying (and side if present)
    group_keys: List[str] = ["underlying"]
    if "side" in work.columns:
        group_keys.append("side")

    for k, col_name in [(1, "label_1"), (2, "label_2"), (3, "label_3"), (5, "label_5")]:
        fwd_ret = []

        for _, g in work.groupby(group_keys, group_keys=False):
            if time_col:
                g = g.sort_values(time_col)

            ltp = g["ltp"].astype(float)
            fwd = ltp.shift(-k)
            ret_pct = (fwd - ltp) / ltp.replace(0, np.nan) * 100.0
            fwd_ret.append(ret_pct)

        work[f"fwd_ret_{k}"] = pd.concat(fwd_ret).sort_index()
        work[col_name] = work[f"fwd_ret_{k}"].fillna(0.0).apply(_label_from_return)

    # Drop helper columns
    drop_cols = [c for c in work.columns if c.startswith("fwd_ret_")]
    work = work.drop(columns=drop_cols)

    return work
