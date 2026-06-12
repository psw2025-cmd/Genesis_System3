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

Final rank score = weighted sum. Top-N returned sorted descending.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
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

# Weights for the six scoring factors (must sum to 1.0)
FACTOR_WEIGHTS = {
    "oi_change_pct":      0.30,   # Strongest signal — institutional conviction
    "iv_percentile":      0.20,   # IV regime matters for premium/directional trades
    "volume_surge":       0.20,   # Volume confirms the move
    "pcr_divergence":     0.15,   # Sentiment extremes with reversal = edge
    "atm_premium_ratio":  0.10,   # Expected move magnitude (how much gain is possible)
    "momentum_score":     0.05,   # Trend confirmation
}

# Minimum score to be included in recommended trades
MIN_GAIN_SCORE = 40.0

# History file for tracking daily predictions
RANK_HISTORY_FILE = os.path.join(ROOT_DIR, "state", "gain_rank_history.json")


class GainRankEngine:
    """
    Ranks all option underlyings by predicted % gain potential.
    Designed to find symbols where the MOST gain is expected — not just direction.
    """

    def __init__(self, top_n: int = 5):
        self.top_n = top_n
        self._rank_history: List[Dict] = self._load_history()

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def rank_all(
        self,
        all_chain_data: Dict[str, pd.DataFrame],
        spots: Dict[str, float],
        oi_history: Optional[Dict[str, Dict]] = None,
        vol_history: Optional[Dict[str, float]] = None,
    ) -> pd.DataFrame:
        """
        Rank all underlyings by predicted gain potential.

        Args:
            all_chain_data: {underlying: options_chain_df}
            spots: {underlying: spot_price}
            oi_history: {underlying: {"prev_oi": float, "curr_oi": float}}
            vol_history: {underlying: avg_5day_volume}

        Returns:
            DataFrame sorted by gain_score descending with columns:
            [rank, underlying, gain_score, oi_change_score, iv_score,
             volume_score, pcr_score, momentum_score, atm_premium_score,
             expected_move_pct, recommendation, timestamp]
        """
        rows = []
        for underlying, chain_df in all_chain_data.items():
            if chain_df is None or chain_df.empty:
                continue
            spot = spots.get(underlying, 0.0)
            if spot <= 0:
                continue

            row = self._score_underlying(
                underlying=underlying,
                chain_df=chain_df,
                spot=spot,
                oi_hist=oi_history.get(underlying) if oi_history else None,
                avg_vol=vol_history.get(underlying) if vol_history else None,
            )
            rows.append(row)

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df = df.sort_values("gain_score", ascending=False).reset_index(drop=True)
        df.insert(0, "rank", range(1, len(df) + 1))
        df["timestamp"] = datetime.now().isoformat()

        # Save snapshot for daily validation
        self._save_snapshot(df)
        return df

    def get_top_n(
        self,
        all_chain_data: Dict[str, pd.DataFrame],
        spots: Dict[str, float],
        oi_history: Optional[Dict[str, Dict]] = None,
        vol_history: Optional[Dict[str, float]] = None,
    ) -> List[Dict]:
        """
        Convenience method: returns top-N symbols as list of dicts.
        Only includes symbols that meet MIN_GAIN_SCORE threshold.
        """
        ranked = self.rank_all(all_chain_data, spots, oi_history, vol_history)
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
    ) -> Dict:
        oi_score = self._oi_change_score(chain_df, oi_hist)
        iv_score = self._iv_percentile_score(chain_df)
        vol_score = self._volume_surge_score(chain_df, avg_vol)
        pcr_score = self._pcr_divergence_score(chain_df, spot)
        premium_score, expected_move_pct = self._atm_premium_score(chain_df, spot)
        momentum_score = self._momentum_score(chain_df, spot)

        gain_score = (
            oi_score      * FACTOR_WEIGHTS["oi_change_pct"]
            + iv_score    * FACTOR_WEIGHTS["iv_percentile"]
            + vol_score   * FACTOR_WEIGHTS["volume_surge"]
            + pcr_score   * FACTOR_WEIGHTS["pcr_divergence"]
            + premium_score * FACTOR_WEIGHTS["atm_premium_ratio"]
            + momentum_score * FACTOR_WEIGHTS["momentum_score"]
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

    def _iv_percentile_score(self, df: pd.DataFrame) -> float:
        """Score based on IV percentile — high IV rank = large premium / big moves expected."""
        iv_col = next((c for c in df.columns if c.lower() in ("iv", "implied_volatility", "iv_pct")), None)
        if iv_col is None:
            return 50.0
        iv_vals = df[iv_col].replace(0, np.nan).dropna()
        if iv_vals.empty:
            return 50.0
        median_iv = iv_vals.median()
        # IV 10-15% = normal. >30% = very high = strong score
        return min(100.0, (median_iv / 0.30) * 100)

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
    #  Persistence                                                         #
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
