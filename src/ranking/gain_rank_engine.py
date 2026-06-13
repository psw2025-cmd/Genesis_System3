"""
Gain Rank Engine
================
Ranks ALL option underlyings by predicted % gain potential using multi-factor scoring.
Returns top-N symbols ordered by expected gain — not just direction (BUY/SELL).

Scoring factors (each normalized 0-100):
  1. OI Change %        — buildup momentum (institutional positioning)
  2. IV Percentile      — high IV = premium selling opportunity / low IV = breakout setup
  3. Volume Surge       — unusual volume vs 5-day average signals conviction
  4. PCR Divergence     — extreme PCR with reversal signal = directional edge
  5. ATM Premium Ratio  — option premium as % of spot (expected move magnitude)
  6. Momentum Score     — recent spot price momentum (dLTP / 5-period EMA)
  7. ML Confidence      — system3_signal_engine aggregate directional conviction per underlying

Final rank score = weighted sum. Top-N returned sorted descending.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
import json
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from core.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger("gain_rank_engine")

# Weights for the seven scoring factors (must sum to 1.0)
# Updated conservatively based on 1-day grid search: PCR was massively under-weighted.
# Grid search optimal (1 day): PCR=0.50, OI=0.15 → ρ 0.40→0.80
# Applied at 50% of optimal move to guard against 1-day overfitting.
# Auto-updated by scripts/calibrate_factor_weights.py once 5+ validation days accumulate.
FACTOR_WEIGHTS = {
    "oi_change_pct":      0.20,   # Reduced 0.25→0.20; grid found OI less discriminating than PCR
    "iv_percentile":      0.15,   # Now real signal via ATM straddle proxy (was dead 50.0)
    "volume_surge":       0.15,   # Unchanged — volume confirms conviction
    "pcr_divergence":     0.22,   # Raised 0.12→0.22; grid search found PCR most discriminating
    "atm_premium_ratio":  0.08,   # Unchanged — expected move magnitude
    "momentum_score":     0.05,   # Unchanged — no bhavcopy intraday data available
    "ml_confidence":      0.15,   # Reduced 0.20→0.15; signal CSV not yet generated, redistributed
}

# Minimum score to be included in recommended trades
MIN_GAIN_SCORE = 40.0

# History files
RANK_HISTORY_FILE = os.path.join(ROOT_DIR, "state", "gain_rank_history.json")
IV_HISTORY_FILE   = os.path.join(ROOT_DIR, "state", "iv_history.json")


class GainRankEngine:
    """
    Ranks all option underlyings by predicted % gain potential.
    Designed to find symbols where the MOST gain is expected — not just direction.
    """

    def __init__(self, top_n: int = 5):
        self.top_n = top_n
        self._rank_history: List[Dict] = self._load_history()
        # {symbol: [iv_proxy_float, ...]} from last 5 days — used by _iv_percentile_score
        self._iv_history: Dict[str, List[float]] = self._load_iv_history()

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def rank_all(
        self,
        all_chain_data: Dict[str, pd.DataFrame],
        spots: Dict[str, float],
        oi_history: Optional[Dict[str, Dict]] = None,
        vol_history: Optional[Dict[str, float]] = None,
        ml_confidence: Optional[Dict[str, float]] = None,
    ) -> pd.DataFrame:
        """
        Rank all underlyings by predicted gain potential.

        Args:
            all_chain_data: {underlying: options_chain_df}
            spots: {underlying: spot_price}
            oi_history: {underlying: {"prev_oi": float, "curr_oi": float}}
            vol_history: {underlying: avg_5day_volume}
            ml_confidence: {underlying: 0-100 score from ml_signal_aggregator}

        Returns:
            DataFrame sorted by gain_score descending with columns:
            [rank, underlying, gain_score, oi_change_score, iv_score,
             volume_score, pcr_score, momentum_score, atm_premium_score,
             ml_confidence_score, expected_move_pct, recommendation, timestamp]
        """
        rows = []
        iv_proxies_today: Dict[str, Optional[float]] = {}

        for underlying, chain_df in all_chain_data.items():
            if chain_df is None or chain_df.empty:
                continue
            spot = spots.get(underlying, 0.0)
            if spot <= 0:
                continue

            # Compute IV proxy once here so it can be stored for tomorrow's history
            iv_proxy = self._compute_iv_proxy(chain_df)
            if iv_proxy is not None:
                iv_proxies_today[underlying] = iv_proxy

            row = self._score_underlying(
                underlying=underlying,
                chain_df=chain_df,
                spot=spot,
                oi_hist=oi_history.get(underlying) if oi_history else None,
                avg_vol=vol_history.get(underlying) if vol_history else None,
                ml_conf=ml_confidence.get(underlying, 0.0) if ml_confidence else 0.0,
                iv_proxy=iv_proxy,
            )
            rows.append(row)

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df = df.sort_values("gain_score", ascending=False).reset_index(drop=True)
        df.insert(0, "rank", range(1, len(df) + 1))
        df["timestamp"] = datetime.now().isoformat()

        # Persist IV proxies so tomorrow has rolling history for percentile scoring
        if iv_proxies_today:
            self._save_iv_history(iv_proxies_today)

        # Save snapshot for daily validation
        self._save_snapshot(df)
        return df

    def get_top_n(
        self,
        all_chain_data: Dict[str, pd.DataFrame],
        spots: Dict[str, float],
        oi_history: Optional[Dict[str, Dict]] = None,
        vol_history: Optional[Dict[str, float]] = None,
        ml_confidence: Optional[Dict[str, float]] = None,
    ) -> List[Dict]:
        """
        Convenience method: returns top-N symbols as list of dicts.
        Only includes symbols that meet MIN_GAIN_SCORE threshold.
        """
        ranked = self.rank_all(all_chain_data, spots, oi_history, vol_history, ml_confidence)
        if ranked.empty:
            return []

        top = ranked[ranked["gain_score"] >= MIN_GAIN_SCORE].head(self.top_n)
        return top.to_dict(orient="records")

    # ------------------------------------------------------------------ #
    #  Scoring factors                                                     #
    # ------------------------------------------------------------------ #

    def _score_underlying(
        self,
        underlying: str,
        chain_df: pd.DataFrame,
        spot: float,
        oi_hist: Optional[Dict],
        avg_vol: Optional[float],
        ml_conf: float = 0.0,
        iv_proxy: Optional[float] = None,
    ) -> Dict:
        oi_score = self._oi_change_score(chain_df, oi_hist)
        iv_score = self._iv_percentile_score(chain_df, underlying, iv_proxy)
        vol_score = self._volume_surge_score(chain_df, avg_vol)
        pcr_score = self._pcr_divergence_score(chain_df, spot)
        premium_score, expected_move_pct = self._atm_premium_score(chain_df, spot)
        momentum_score = self._momentum_score(chain_df, spot)

        # When ml_confidence=0 (signal engine hasn't run), redistribute its 20%
        # weight proportionally to the other factors so scoring remains valid.
        if ml_conf > 0:
            gain_score = (
                oi_score        * FACTOR_WEIGHTS["oi_change_pct"]
                + iv_score      * FACTOR_WEIGHTS["iv_percentile"]
                + vol_score     * FACTOR_WEIGHTS["volume_surge"]
                + pcr_score     * FACTOR_WEIGHTS["pcr_divergence"]
                + premium_score * FACTOR_WEIGHTS["atm_premium_ratio"]
                + momentum_score * FACTOR_WEIGHTS["momentum_score"]
                + ml_conf       * FACTOR_WEIGHTS["ml_confidence"]
            )
        else:
            # No ML signal — redistribute ml_confidence weight proportionally
            base_weight = 1.0 - FACTOR_WEIGHTS["ml_confidence"]
            gain_score = (
                oi_score        * FACTOR_WEIGHTS["oi_change_pct"] / base_weight
                + iv_score      * FACTOR_WEIGHTS["iv_percentile"] / base_weight
                + vol_score     * FACTOR_WEIGHTS["volume_surge"] / base_weight
                + pcr_score     * FACTOR_WEIGHTS["pcr_divergence"] / base_weight
                + premium_score * FACTOR_WEIGHTS["atm_premium_ratio"] / base_weight
                + momentum_score * FACTOR_WEIGHTS["momentum_score"] / base_weight
            )

        gain_score = round(min(100.0, max(0.0, gain_score)), 2)

        return {
            "underlying": underlying,
            "gain_score": gain_score,
            "oi_change_score": round(oi_score, 2),
            "iv_score": round(iv_score, 2),
            "volume_score": round(vol_score, 2),
            "pcr_score": round(pcr_score, 2),
            "momentum_score": round(momentum_score, 2),
            "atm_premium_score": round(premium_score, 2),
            "ml_confidence_score": round(ml_conf, 2),
            "expected_move_pct": round(expected_move_pct, 3),
            "recommendation": "TRADE" if gain_score >= MIN_GAIN_SCORE else "SKIP",
        }

    def _oi_change_score(self, df: pd.DataFrame, oi_hist: Optional[Dict]) -> float:
        """Score based on % change in total OI vs previous session."""
        if oi_hist and "prev_oi" in oi_hist and oi_hist["prev_oi"] > 0:
            curr_oi = oi_hist.get("curr_oi", 0)
            change_pct = abs((curr_oi - oi_hist["prev_oi"]) / oi_hist["prev_oi"]) * 100
            # >5% OI change = strong; >15% = very strong
            return min(100.0, change_pct * 6.0)

        # Fallback: use intra-chain OI concentration
        oi_col = next((c for c in df.columns if "oi" in c.lower() and "change" not in c.lower()), None)
        if oi_col is None:
            return 50.0
        total_oi = df[oi_col].sum()
        if total_oi <= 0:
            return 50.0
        # Score by how concentrated OI is near ATM (concentration = conviction)
        return min(100.0, (total_oi / 1_000_000) * 10)

    def _iv_percentile_score(
        self,
        df: pd.DataFrame,
        underlying: str = "",
        iv_proxy: Optional[float] = None,
    ) -> float:
        """
        Score based on IV percentile.
        Priority:
          1. Real IV column from live option chain (Dhan Data API — future)
          2. ATM straddle proxy vs 5-day rolling history (from bhavcopy)
          3. Fallback: 50.0 (neutral, no signal)
        """
        # Path 1: real IV column
        iv_col = next((c for c in df.columns if c.lower() in ("iv", "implied_volatility", "iv_pct")), None)
        if iv_col is not None:
            iv_vals = df[iv_col].replace(0, np.nan).dropna()
            if not iv_vals.empty:
                median_iv = iv_vals.median()
                return min(100.0, (median_iv / 0.30) * 100)

        # Path 2: proxy from bhavcopy ATM straddle (passed from rank_all)
        if iv_proxy is None:
            iv_proxy = self._compute_iv_proxy(df)

        if iv_proxy is None:
            return 50.0

        history = self._iv_history.get(underlying, [])
        if len(history) < 2:
            # Not enough history — use absolute scaling: proxy ~0.15 → 75 score
            return min(100.0, iv_proxy * 500)

        n_below = sum(1 for v in history if v < iv_proxy)
        return round(n_below / len(history) * 100, 1)

    def _compute_iv_proxy(self, df: pd.DataFrame) -> Optional[float]:
        """
        Compute annualised ATM straddle IV proxy.
        Handles both raw bhavcopy UDiFF columns and parsed chain_df columns
        (which have expiry_date + spot_price preserved from _parse_bhavcopy).
        Formula: (ATM_CE_ltp + ATM_PE_ltp) / spot / sqrt(T)
        """
        # Detect column style: parsed (has expiry_date) vs raw UDiFF (has XpryDt)
        if "expiry_date" in df.columns and "spot_price" in df.columns:
            expiry_col, strike_col, type_col, ltp_col, spot_col = (
                "expiry_date", "strike", "option_type", "ltp", "spot_price"
            )
        elif "XpryDt" in df.columns and "UndrlygPric" in df.columns:
            expiry_col, strike_col, ltp_col, spot_col = "XpryDt", "StrkPric", "ClsPric", "UndrlygPric"
            type_col = next((c for c in df.columns if c.lower() in ("optntp",)), None)
            if type_col is None:
                return None
        else:
            return None

        spot_series = pd.to_numeric(df[spot_col], errors="coerce").dropna()
        if spot_series.empty or spot_series.iloc[0] <= 0:
            return None
        spot_val = float(spot_series.iloc[0])

        df2 = df.copy()
        df2["_expiry_dt"] = pd.to_datetime(df2[expiry_col], errors="coerce")
        df2 = df2.dropna(subset=["_expiry_dt"])
        if df2.empty:
            return None

        today = date.today()
        df2["_days"] = (df2["_expiry_dt"].dt.date - today).apply(lambda d: d.days)
        df2 = df2[df2["_days"] > 0]  # skip 0-DTE (intrinsic only, not real IV)
        if df2.empty:
            return None

        nearest_exp = df2["_expiry_dt"].min()
        near = df2[df2["_expiry_dt"] == nearest_exp].copy()
        T = float(near["_days"].iloc[0]) / 365

        near["_dist"] = pd.to_numeric(near[strike_col], errors="coerce").sub(spot_val).abs()
        atm_strike = near.loc[near["_dist"].idxmin(), strike_col]

        atm = near[near[strike_col] == atm_strike]
        ce = atm[atm[type_col].str.upper() == "CE"]
        pe = atm[atm[type_col].str.upper() == "PE"]

        ce_ltp = float(ce[ltp_col].values[0]) if len(ce) > 0 else 0.0
        pe_ltp = float(pe[ltp_col].values[0]) if len(pe) > 0 else 0.0
        straddle = ce_ltp + pe_ltp

        if straddle <= 0 or spot_val <= 0:
            return None

        return round(straddle / spot_val / (T ** 0.5), 6)

    def _volume_surge_score(self, df: pd.DataFrame, avg_vol: Optional[float]) -> float:
        """Score based on volume surge vs 5-day average."""
        vol_col = next((c for c in df.columns if "volume" in c.lower() or c.lower() == "vol"), None)
        if vol_col is None:
            return 50.0
        curr_vol = df[vol_col].sum()
        if curr_vol <= 0:
            return 50.0
        if avg_vol and avg_vol > 0:
            surge_ratio = curr_vol / avg_vol
            return min(100.0, (surge_ratio - 1.0) * 50 + 50)   # 1x=50, 2x=100
        # Fallback: absolute volume score
        return min(100.0, (curr_vol / 1_000_000) * 10)

    def _pcr_divergence_score(self, df: pd.DataFrame, spot: float) -> float:
        """
        Score based on PCR at extreme with reversal signal.
        PCR < 0.7 (over-bearish) or PCR > 1.5 (over-bullish) near reversal = high score.
        """
        oi_col = next((c for c in df.columns if "oi" in c.lower() and "change" not in c.lower()), None)
        type_col = next((c for c in df.columns if c.lower() in ("option_type", "type", "ce_pe")), None)
        if oi_col is None or type_col is None:
            return 50.0

        ce_oi = df[df[type_col].str.upper().isin(["CE", "CALL"])][oi_col].sum()
        pe_oi = df[df[type_col].str.upper().isin(["PE", "PUT"])][oi_col].sum()
        if ce_oi <= 0:
            return 50.0

        pcr = pe_oi / ce_oi
        # Extremes signal potential for sharp moves (PCR extremes = contrarian opportunity)
        if pcr < 0.6 or pcr > 1.8:
            return 90.0
        elif pcr < 0.8 or pcr > 1.4:
            return 70.0
        elif pcr < 1.0 or pcr > 1.2:
            return 55.0
        return 45.0  # PCR near 1 = balanced, less directional edge

    def _atm_premium_score(self, df: pd.DataFrame, spot: float) -> Tuple[float, float]:
        """
        Score based on ATM option premium as % of spot.
        Higher premium % = bigger expected move = higher gain potential.
        Returns (score, expected_move_pct).
        """
        ltp_col = next((c for c in df.columns if c.lower() in ("ltp", "last_price", "close")), None)
        strike_col = next((c for c in df.columns if "strike" in c.lower()), None)
        if ltp_col is None or strike_col is None or spot <= 0:
            return 50.0, 0.02

        atm_strike = df[strike_col].sub(spot).abs().idxmin()
        atm_row = df.loc[atm_strike]
        atm_ltp = atm_row[ltp_col] if isinstance(atm_row[ltp_col], (int, float)) else df[ltp_col].median()

        expected_move_pct = (atm_ltp * 2) / spot  # Straddle approximation
        score = min(100.0, expected_move_pct * 1000)  # 2% move = 20 score, 10% = 100
        return score, round(expected_move_pct, 4)

    def _momentum_score(self, df: pd.DataFrame, spot: float) -> float:
        """Score based on recent spot momentum (change_pct column or derived)."""
        chg_col = next(
            (c for c in df.columns if c.lower() in ("change_pct", "pct_change", "spot_change", "change%")),
            None
        )
        if chg_col is not None:
            momentum = df[chg_col].mean()
            return min(100.0, max(0.0, 50 + momentum * 10))

        # Fallback: check if spot vs ATM CE LTP suggests direction
        return 50.0

    # ------------------------------------------------------------------ #
    #  IV History persistence                                             #
    # ------------------------------------------------------------------ #

    def _load_iv_history(self) -> Dict[str, List[float]]:
        """Load {symbol: [last-5-days iv_proxy values]} from iv_history.json."""
        if not os.path.exists(IV_HISTORY_FILE):
            return {}
        try:
            with open(IV_HISTORY_FILE) as f:
                raw: Dict[str, Dict[str, float]] = json.load(f)
        except Exception:
            return {}
        # raw = {date_str: {symbol: iv_proxy}}
        # Sort by date, take last 5 days, flatten to {symbol: [values]}
        sorted_dates = sorted(raw.keys())[-5:]
        out: Dict[str, List[float]] = {}
        for d in sorted_dates:
            for sym, val in raw[d].items():
                out.setdefault(sym, []).append(val)
        return out

    def _save_iv_history(self, today_values: Dict[str, Optional[float]]) -> None:
        """Append today's IV proxies to iv_history.json, keep last 30 days."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(os.path.dirname(IV_HISTORY_FILE), exist_ok=True)

        raw: Dict[str, Dict[str, float]] = {}
        if os.path.exists(IV_HISTORY_FILE):
            try:
                with open(IV_HISTORY_FILE) as f:
                    raw = json.load(f)
            except Exception:
                raw = {}

        entry = {sym: val for sym, val in today_values.items() if val is not None}
        if entry:
            raw[today_str] = entry

        # Prune to last 30 days
        pruned = {d: v for d, v in raw.items() if d in sorted(raw.keys())[-30:]}
        try:
            with open(IV_HISTORY_FILE, "w") as f:
                json.dump(pruned, f, indent=2)
        except Exception as e:
            logger.warning(f"GainRankEngine: could not save IV history: {e}")

    # ------------------------------------------------------------------ #
    #  Rank history persistence                                            #
    # ------------------------------------------------------------------ #

    def _save_snapshot(self, ranked_df: pd.DataFrame) -> None:
        """Save today's ranking snapshot for later market result validation."""
        os.makedirs(os.path.dirname(RANK_HISTORY_FILE), exist_ok=True)
        snapshot = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "predictions": ranked_df[["rank", "underlying", "gain_score", "expected_move_pct", "recommendation"]]
                           .head(10).to_dict(orient="records"),
        }
        self._rank_history.append(snapshot)
        # Keep last 90 days
        self._rank_history = self._rank_history[-90:]
        try:
            with open(RANK_HISTORY_FILE, "w") as f:
                json.dump(self._rank_history, f, indent=2)
        except Exception as e:
            logger.warning(f"GainRankEngine: could not save history: {e}")

    def _load_history(self) -> List[Dict]:
        if not os.path.exists(RANK_HISTORY_FILE):
            return []
        try:
            with open(RANK_HISTORY_FILE) as f:
                return json.load(f)
        except Exception:
            return []

    def get_history(self) -> List[Dict]:
        return self._rank_history
