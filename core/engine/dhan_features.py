from __future__ import annotations

import numpy as np
import pandas as pd


def add_advanced_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a set of advanced-but-lightweight engineered features.

    These are designed to be:
    - cheap to compute on synthetic + live data
    - robust to missing base columns (fallback to 0.0)
    - easily extendable later
    """
    out = df.copy()

    # Safely fetch base columns
    spot = out.get("spot")
    ltp = out.get("ltp")
    moneyness = out.get("moneyness")
    atm_abs = out.get("atm_dist_abs")
    atm_pct = out.get("atm_dist_pct")
    ltp_chg = out.get("ltp_chg_1_pct")
    spot_chg = out.get("spot_chg_1_pct")
    ltp_std = out.get("ltp_roll_std_5")
    spot_std = out.get("spot_roll_std_5")
    ce_pe_ratio = out.get("ce_pe_ratio")

    spot_safe = spot.astype(float) if spot is not None else None
    ltp_safe = ltp.astype(float) if ltp is not None else None

    # moneyness% (relative to spot)
    if moneyness is not None and spot_safe is not None:
        out["moneyness_pct"] = (moneyness.astype(float) / spot_safe.replace(0, np.nan) * 100.0).fillna(0.0)
    else:
        out["moneyness_pct"] = 0.0

    # distance_from_atm (pct)
    if atm_abs is not None and spot_safe is not None:
        out["dist_atm_pct"] = (atm_abs.astype(float) / spot_safe.replace(0, np.nan) * 100.0).fillna(0.0)
    elif atm_pct is not None:
        out["dist_atm_pct"] = atm_pct.astype(float) * 100.0
    else:
        out["dist_atm_pct"] = 0.0

    # decay-speed: opposite of short-term premium change
    if ltp_chg is not None:
        out["premium_decay_speed"] = -ltp_chg.astype(float)
    else:
        out["premium_decay_speed"] = 0.0

    # synthetic IV proxy: atm distance * volatility
    if atm_pct is not None and ltp_std is not None:
        out["synthetic_iv_proxy"] = atm_pct.astype(float) * ltp_std.astype(float)
    else:
        out["synthetic_iv_proxy"] = 0.0

    # spot-leading-premium / premium-leading-spot
    if ltp_chg is not None and spot_chg is not None:
        lc = ltp_chg.astype(float)
        sc = spot_chg.astype(float)
        out["spot_leads_premium"] = sc - lc
        out["premium_leads_spot"] = lc - sc
    else:
        out["spot_leads_premium"] = 0.0
        out["premium_leads_spot"] = 0.0

    # volatility shock detector
    if spot_std is not None:
        out["vol_shock_flag"] = (spot_std.astype(float) > 1.0).astype(int)
    else:
        out["vol_shock_flag"] = 0

    # synthetic VWAP proxy (we don't have volume, so mirror LTP)
    if ltp_safe is not None:
        out["synthetic_vwap"] = ltp_safe
    else:
        out["synthetic_vwap"] = 0.0

    # simple slopes (3-step, 5-step) on premium if sequential data exists
    if "ts" in out.columns and ltp_safe is not None:
        sort_cols = [c for c in ["underlying", "side", "ts"] if c in out.columns]
        if sort_cols:
            out = out.sort_values(sort_cols)
        grouped = out.groupby(["underlying", "side"], group_keys=False)

        out["slope_3"] = grouped["ltp"].apply(lambda s: s.astype(float).diff(3) / 3.0).fillna(0.0)
        out["slope_5"] = grouped["ltp"].apply(lambda s: s.astype(float).diff(5) / 5.0).fillna(0.0)
    else:
        out["slope_3"] = 0.0
        out["slope_5"] = 0.0

    # RSI-like oscillator on premium (very crude)
    if "ts" in out.columns and ltp_safe is not None:
        grouped = out.groupby(["underlying", "side"], group_keys=False)

        def _rsi_like(series: pd.Series, window: int = 5) -> pd.Series:
            delta = series.diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window).mean()
            avg_loss = loss.rolling(window).mean()
            rs = avg_gain / avg_loss.replace(0, np.nan)
            rsi = 100.0 - (100.0 / (1.0 + rs))
            return rsi.fillna(50.0)

        out["rsi_like_5"] = grouped["ltp"].apply(lambda s: _rsi_like(s.astype(float), window=5))
    else:
        out["rsi_like_5"] = 50.0

    # CE/PE order-flow proxy (from ce_pe_diff if available)
    if "ce_pe_diff" in out.columns:
        diff = out["ce_pe_diff"].astype(float)
        out["orderflow_proxy"] = np.tanh(diff / 50.0)
    else:
        out["orderflow_proxy"] = 0.0

    # Divergence signal: premium vs spot move disagreement
    if ltp_chg is not None and spot_chg is not None:
        lc = ltp_chg.astype(float)
        sc = spot_chg.astype(float)
        out["divergence_signal"] = np.sign(lc) * np.sign(-sc)
    else:
        out["divergence_signal"] = 0.0

    return out
