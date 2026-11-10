#!/usr/bin/env python3
"""
Real 5/6-day (bhavcopy-based) ranking validation -- DuckDB-vectorized.

Computes a GENUINE Spearman rho between the production ranker's predicted
gain-score (using the live FACTOR_WEIGHTS from src/ranking/gain_rank_engine.py,
computed from real NSE F&O bhavcopy data on day D) and the REAL observed
next-trading-day % move in each underlying's spot price (day D -> day D+1).

This intentionally does NOT fabricate a passing result. If the real
correlation is below the SYS3-BLK-005 threshold (0.70), the validation file
still records the true rho -- a low/negative rho is itself real evidence
about current model quality and must not be papered over.

Performance: all cached bhavcopy CSVs are loaded ONCE into an in-memory
DuckDB table and every per-symbol/per-day factor (OI, volume, PCR, ATM
straddle, and a REAL 5-day rolling price/OI momentum) is computed with
set-based SQL, instead of re-reading a CSV per symbol per day.

Universe per day: all index + equity underlyings with F&O options that day.

Output: state/market_validations/market_validation_<date>.json per validated
day (schema matches what scripts/system3_gate_evaluator.py already reads).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict

import duckdb
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.ranking.gain_rank_engine import FACTOR_WEIGHTS  # noqa: E402

BHAVCOPY_GLOB = str(ROOT / "storage" / "bhavcopy" / "*.csv")
OUT_DIR = ROOT / "state" / "market_validations"
MIN_UNIVERSE = 10
MOMENTUM_LOOKBACK_DAYS = 5

# 6-factor weights (bhavcopy has no live ML-confidence signal), redistributed
# proportionally exactly like GainRankEngine.rank_all does when ml_confidence
# is unavailable -- this mirrors PRODUCTION behavior, it does not invent one.
_BASE = 1.0 - FACTOR_WEIGHTS["ml_confidence"]
PRODUCTION_WEIGHTS_NO_ML = {
    "oi_change_pct": FACTOR_WEIGHTS["oi_change_pct"] / _BASE,
    "iv_percentile": FACTOR_WEIGHTS["iv_percentile"] / _BASE,
    "volume_surge": FACTOR_WEIGHTS["volume_surge"] / _BASE,
    "pcr_divergence": FACTOR_WEIGHTS["pcr_divergence"] / _BASE,
    "atm_premium_ratio": FACTOR_WEIGHTS["atm_premium_ratio"] / _BASE,
    "momentum_score": FACTOR_WEIGHTS["momentum_score"] / _BASE,
}


def build_lakehouse() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
    con.execute(
        f"""
        CREATE TABLE bhav AS
        SELECT
            TckrSymb AS symbol, OptnTp AS opt_type, FinInstrmTp AS instr_type,
            TradDt AS trade_date, StrkPric AS strike, UndrlygPric AS spot,
            OpnIntrst AS oi, ChngInOpnIntrst AS oi_change, TtlTradgVol AS volume,
            ClsPric AS close_price, XpryDt AS expiry
        FROM read_csv_auto('{BHAVCOPY_GLOB}', union_by_name=True)
        WHERE OptnTp IN ('CE','PE') AND UndrlygPric > 0
        """
    )
    return con


def compute_daily_factors(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """One row per (trade_date, symbol): spot, oi, volume, pcr, atm straddle,
    and a REAL 5-day rolling momentum of spot price + OI, all set-based."""
    con.execute(
        """
        CREATE TABLE base_agg AS
        SELECT
            trade_date, symbol,
            ANY_VALUE(spot) AS spot,
            SUM(oi) AS oi_total,
            SUM(ABS(oi_change)) AS oi_change_total,
            SUM(volume) AS volume,
            SUM(oi) FILTER (WHERE opt_type='CE') AS ce_oi,
            SUM(oi) FILTER (WHERE opt_type='PE') AS pe_oi,
            MIN(expiry) FILTER (WHERE expiry > trade_date) AS nearest_expiry
        FROM bhav
        GROUP BY trade_date, symbol
        """
    )
    con.execute(
        """
        CREATE TABLE atm AS
        WITH near AS (
            SELECT b.*, a.spot AS day_spot, a.nearest_expiry,
                   ABS(b.strike - a.spot) AS dist
            FROM bhav b
            JOIN base_agg a USING (trade_date, symbol)
            WHERE b.expiry = a.nearest_expiry
        ),
        ranked AS (
            SELECT *,
                ROW_NUMBER() OVER (PARTITION BY trade_date, symbol, opt_type ORDER BY dist) AS rn
            FROM near
        )
        SELECT trade_date, symbol,
            MAX(close_price) FILTER (WHERE opt_type='CE' AND rn=1) AS atm_ce,
            MAX(close_price) FILTER (WHERE opt_type='PE' AND rn=1) AS atm_pe,
            MIN(CAST(nearest_expiry - trade_date AS BIGINT)) AS days_to_exp
        FROM ranked
        GROUP BY trade_date, symbol
        """
    )
    # REAL momentum: 5-day rolling % change in spot AND OI, per symbol,
    # using only prior days (no lookahead) via window functions.
    con.execute(
        f"""
        CREATE TABLE momentum AS
        SELECT
            trade_date, symbol,
            spot / NULLIF(LAG(spot, {MOMENTUM_LOOKBACK_DAYS}) OVER w, 0) - 1.0 AS spot_roll_chg_5d,
            oi_total / NULLIF(LAG(oi_total, {MOMENTUM_LOOKBACK_DAYS}) OVER w, 0) - 1.0 AS oi_roll_chg_5d
        FROM base_agg
        WINDOW w AS (PARTITION BY symbol ORDER BY trade_date)
        """
    )

    df = con.execute(
        """
        SELECT b.trade_date, b.symbol, b.spot, b.oi_total, b.oi_change_total, b.volume,
               b.ce_oi, b.pe_oi, a.atm_ce, a.atm_pe, a.days_to_exp,
               m.spot_roll_chg_5d, m.oi_roll_chg_5d
        FROM base_agg b
        LEFT JOIN atm a USING (trade_date, symbol)
        LEFT JOIN momentum m USING (trade_date, symbol)
        ORDER BY b.trade_date, b.symbol
        """
    ).fetchdf()

    df["pcr"] = df["pe_oi"] / df["ce_oi"].replace(0, np.nan)
    df["pcr"] = df["pcr"].fillna(1.0)
    # ATM IV proxy: skip expiry-day straddle (intrinsic only, distorted).
    valid_atm = df["days_to_exp"].fillna(0) > 0
    df["atm_premium"] = np.where(
        valid_atm, (df["atm_ce"].fillna(0) + df["atm_pe"].fillna(0)) / 2 / df["spot"], np.nan
    )
    return df


def _norm_minmax(values: pd.Series) -> pd.Series:
    v = values.astype(float)
    lo, hi = v.min(), v.max()
    if pd.isna(lo) or pd.isna(hi) or hi <= lo:
        return pd.Series(50.0, index=v.index)
    return (v - lo) / (hi - lo) * 100.0


def _pcr_score(pcr: float) -> float:
    if pcr < 0.6 or pcr > 1.8:
        return 90.0
    if pcr < 0.8 or pcr > 1.4:
        return 70.0
    if pcr < 1.0 or pcr > 1.2:
        return 55.0
    return 45.0


def score_day(day_df: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectional normalize one day's factor rows into 0-100 scores."""
    df = day_df.copy()
    df["oi_chg_pct_raw"] = df["oi_change_total"] / df["oi_total"].replace(0, np.nan) * 100.0
    df["oi_score"] = _norm_minmax(df["oi_chg_pct_raw"].fillna(0))
    df["vol_score"] = _norm_minmax(df["volume"])
    df["atm_score"] = _norm_minmax(df["atm_premium"].fillna(df["atm_premium"].median()))
    df["pcr_score"] = df["pcr"].apply(_pcr_score)
    # IV percentile proxy: cross-sectional rank of atm_premium as a stand-in
    # (bhavcopy has no per-symbol multi-day IV history built cheaply here).
    df["iv_score"] = df["atm_score"]
    # REAL momentum score: blend of 5-day spot %% change and OI %% change,
    # cross-sectionally normalized -- replaces the old hardcoded 50.0.
    spot_mom = df["spot_roll_chg_5d"].fillna(0.0)
    oi_mom = df["oi_roll_chg_5d"].fillna(0.0)
    df["momentum_score"] = _norm_minmax(0.5 * _norm_minmax(spot_mom) + 0.5 * _norm_minmax(oi_mom))
    return df


def _weighted_score(row: pd.Series, w: Dict[str, float]) -> float:
    return (
        row["oi_score"] * w["oi_change_pct"]
        + row["iv_score"] * w["iv_percentile"]
        + row["vol_score"] * w["volume_surge"]
        + row["pcr_score"] * w["pcr_divergence"]
        + row["atm_score"] * w["atm_premium_ratio"]
        + row["momentum_score"] * w["momentum_score"]
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = build_lakehouse()
    factors = compute_daily_factors(con)
    dates = sorted(factors["trade_date"].unique())
    if len(dates) < 2:
        print("Need at least 2 cached bhavcopy days.")
        return 1

    written = []
    for i in range(len(dates) - 1):
        d0, d1 = dates[i], dates[i + 1]
        day0 = factors[factors["trade_date"] == d0]
        day1 = factors[factors["trade_date"] == d1].set_index("symbol")

        common = [s for s in day0["symbol"] if s in day1.index]
        if len(common) < MIN_UNIVERSE:
            print(f"{d0}: only {len(common)} symbols in common with next day, skipping")
            continue

        scored = score_day(day0[day0["symbol"].isin(common)]).set_index("symbol")
        scored["gain_score"] = scored.apply(lambda r: _weighted_score(r, PRODUCTION_WEIGHTS_NO_ML), axis=1)
        predicted_order = scored.sort_values("gain_score", ascending=False).index.tolist()

        actual_pct = {
            s: (day1.loc[s, "spot"] - scored.loc[s, "spot"]) / scored.loc[s, "spot"] * 100.0 for s in common
        }
        actual_order = sorted(actual_pct, key=lambda s: actual_pct[s], reverse=True)

        pred_ranks = {s: r + 1 for r, s in enumerate(predicted_order)}
        act_ranks = {s: r + 1 for r, s in enumerate(actual_order)}
        p = [pred_ranks[s] for s in common]
        a = [act_ranks[s] for s in common]
        rho, _ = spearmanr(a, p)
        rho = 0.0 if np.isnan(rho) else float(rho)

        top10_pred, top10_act = set(predicted_order[:10]), set(actual_order[:10])
        hit_rate = len(top10_pred & top10_act) / 10.0

        day_str = pd.Timestamp(d0).strftime("%Y-%m-%d")
        next_day_str = pd.Timestamp(d1).strftime("%Y-%m-%d")
        record = {
            "date": day_str,
            "generated_by": "scripts/real_bhavcopy_5day_validation.py",
            "methodology": (
                "Cross-sectional rank of production FACTOR_WEIGHTS (ml_confidence "
                "redistributed; momentum_score is a REAL 5-day rolling spot+OI delta "
                "from bhavcopy, not a placeholder) computed from day D real NSE F&O "
                "bhavcopy vs REAL next-trading-day spot % change (day D -> day D+1), "
                "all symbols with F&O options that day."
            ),
            "is_fixture": False,
            "is_synthetic": False,
            "universe_size": len(common),
            "next_trading_day": next_day_str,
            "rank_correlation_spearman": round(rho, 4),
            "hit_rate_top10": round(hit_rate, 4),
            "predicted_top10": predicted_order[:10],
            "actual_top10": actual_order[:10],
            "status": "PASS" if rho >= 0.70 else "BELOW_THRESHOLD",
        }
        (OUT_DIR / f"market_validation_{day_str}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        written.append((day_str, rho, len(common)))
        print(f"{day_str} -> next {d1}: rho={rho:.4f}  hit_rate_top10={hit_rate:.2f}  universe={len(common)}")

    print()
    print(f"Wrote {len(written)} real validation day(s) to {OUT_DIR}")
    if written:
        mean_rho = sum(r for _, r, _ in written) / len(written)
        print(f"Mean rho across {len(written)} real days: {mean_rho:.4f} (threshold: 0.70)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
