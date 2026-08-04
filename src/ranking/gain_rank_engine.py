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
  8. Gamma Exposure     — net dealer gamma × OI (GEX); large negative GEX → sharp moves expected

Final rank score = weighted sum. Top-N returned sorted descending.
"""

import json
import os
import sys
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from core.utils.logger import logger
except ImportError:
    import logging

    logger = logging.getLogger("gain_rank_engine")

# Weights for the eight scoring factors (must sum to 1.0)
# Updated conservatively based on 1-day grid search: PCR was massively under-weighted.
# Grid search optimal (1 day): PCR=0.50, OI=0.15 → ρ 0.40→0.80
# Applied at 50% of optimal move to guard against 1-day overfitting.
# Gamma Exposure added (0.07) taken from momentum_score reduction (0.05→0.02) and
# ml_confidence reduction (0.15→0.13) — GEX is a proven high-signal NSE factor.
# Auto-updated by scripts/calibrate_factor_weights.py once 5+ validation days accumulate.
FACTOR_WEIGHTS = {
    "oi_change_pct": 0.20,  # Reduced 0.25→0.20; grid found OI less discriminating than PCR
    "iv_percentile": 0.15,  # Now real signal via ATM straddle proxy (was dead 50.0)
    "volume_surge": 0.13,  # Slight reduction from 0.15 to fund GEX factor
    "pcr_divergence": 0.22,  # Raised 0.12→0.22; grid search found PCR most discriminating
    "atm_premium_ratio": 0.08,  # Unchanged — expected move magnitude
    "momentum_score": 0.02,  # Reduced 0.05→0.02 — usually defaults to 50.0, weak signal
    "ml_confidence": 0.13,  # Reduced 0.15→0.13; signal CSV not yet generated
    "gamma_exposure": 0.07,  # NEW — net dealer GEX from Dhan Greeks; 0 if gamma unavailable
}

# Minimum score to be included in recommended trades
MIN_GAIN_SCORE = 40.0

# History files
RANK_HISTORY_FILE = os.path.join(ROOT_DIR, "state", "gain_rank_history.json")
IV_HISTORY_FILE = os.path.join(ROOT_DIR, "state", "iv_history.json")


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
            try:
                from core.brokers.dhan.equity_fo_universe import is_tradeable_fo_symbol

                if not is_tradeable_fo_symbol(underlying):
                    logger.debug("Skipping non-F&O symbol %s", underlying)
                    continue
            except ImportError:
                pass
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
        gex_score = self._gamma_exposure_score(chain_df, spot)

        # When ml_confidence=0 (signal engine hasn't run), redistribute its weight
        # proportionally to the other factors so scoring remains valid.
        if ml_conf > 0:
            gain_score = (
                oi_score * FACTOR_WEIGHTS["oi_change_pct"]
                + iv_score * FACTOR_WEIGHTS["iv_percentile"]
                + vol_score * FACTOR_WEIGHTS["volume_surge"]
                + pcr_score * FACTOR_WEIGHTS["pcr_divergence"]
                + premium_score * FACTOR_WEIGHTS["atm_premium_ratio"]
                + momentum_score * FACTOR_WEIGHTS["momentum_score"]
                + ml_conf * FACTOR_WEIGHTS["ml_confidence"]
                + gex_score * FACTOR_WEIGHTS["gamma_exposure"]
            )
        else:
            # No ML signal — redistribute ml_confidence weight proportionally
            base_weight = 1.0 - FACTOR_WEIGHTS["ml_confidence"]
            gain_score = (
                oi_score * FACTOR_WEIGHTS["oi_change_pct"] / base_weight
                + iv_score * FACTOR_WEIGHTS["iv_percentile"] / base_weight
                + vol_score * FACTOR_WEIGHTS["volume_surge"] / base_weight
                + pcr_score * FACTOR_WEIGHTS["pcr_divergence"] / base_weight
                + premium_score * FACTOR_WEIGHTS["atm_premium_ratio"] / base_weight
                + momentum_score * FACTOR_WEIGHTS["momentum_score"] / base_weight
                + gex_score * FACTOR_WEIGHTS["gamma_exposure"] / base_weight
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
            "gamma_exposure_score": round(gex_score, 2),
            "expected_move_pct": round(expected_move_pct, 3),
            "recommendation": "TRADE" if gain_score >= MIN_GAIN_SCORE else "SKIP",
        }

    def _oi_change_score(self, df: pd.DataFrame, oi_hist: Optional[Dict]) -> float:
        """Score based on % change in total OI vs previous session.

        Priority:
          1. Session-level OI history (oi_hist dict with prev_oi / curr_oi)
          2. Intra-chain change_in_oi column from Dhan API (net OI change per strike)
          3. OI concentration fallback (weakest signal)
        """
        if oi_hist and "prev_oi" in oi_hist and oi_hist["prev_oi"] > 0:
            curr_oi = oi_hist.get("curr_oi", 0)
            change_pct = abs((curr_oi - oi_hist["prev_oi"]) / oi_hist["prev_oi"]) * 100
            # >5% OI change = strong; >15% = very strong
            return min(100.0, change_pct * 6.0)

        # Path 2: use change_in_oi column from Dhan API (oi - previous_oi per strike)
        chg_col = next(
            (c for c in df.columns if c.lower() in ("change_in_oi", "oi_change", "chng_in_oi", "oichange")), None
        )
        if chg_col is not None:
            net_change = pd.to_numeric(df[chg_col], errors="coerce").fillna(0)
            oi_col = next((c for c in df.columns if c.lower() in ("oi", "open_interest") and c != chg_col), None)
            total_oi = pd.to_numeric(df[oi_col], errors="coerce").sum() if oi_col else 0
            total_chg = net_change.abs().sum()
            if total_oi > 0:
                change_pct = (total_chg / total_oi) * 100
                return min(100.0, change_pct * 6.0)

        # Path 3: fallback: use intra-chain OI concentration
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
                "expiry_date",
                "strike",
                "option_type",
                "ltp",
                "spot_price",
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

        return round(straddle / spot_val / (T**0.5), 6)

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
            return min(100.0, (surge_ratio - 1.0) * 50 + 50)  # 1x=50, 2x=100
        # Fallback: absolute volume score
        return min(100.0, (curr_vol / 1_000_000) * 10)

    def _pcr_divergence_score(self, df: pd.DataFrame, spot: float) -> float:
        """
        Score based on PCR extremes — continuous scoring rather than buckets.

        Strategy: PCR < 0.7 (bearish excess — CE writers dominate) or PCR > 1.5
        (bullish excess — PE writers dominate) signals potential for sharp reversal moves.
        Near-ATM PCR (±2 strikes) is more informative than total chain PCR.

        Returns 0-100 where 90-100 = extreme imbalance (strong move likely).
        """
        oi_col = next((c for c in df.columns if c.lower() in ("oi", "open_interest") and "change" not in c.lower()), None)
        type_col = next((c for c in df.columns if c.lower() in ("option_type", "type", "ce_pe")), None)
        strike_col = next((c for c in df.columns if "strike" in c.lower()), None)

        if oi_col is None or type_col is None:
            return 50.0

        # Attempt near-ATM PCR first (more signal-dense)
        if strike_col is not None and spot > 0:
            df2 = df.copy()
            df2["_strike"] = pd.to_numeric(df2[strike_col], errors="coerce")
            # Typical ATM range: ±2% of spot (covers 3-4 strikes for NIFTY 50-pt spacing)
            atm_band = spot * 0.02
            near_atm = df2[df2["_strike"].between(spot - atm_band, spot + atm_band)]
            if len(near_atm) >= 2:
                ce_oi = pd.to_numeric(
                    near_atm[near_atm[type_col].str.upper().isin(["CE", "CALL"])][oi_col], errors="coerce"
                ).sum()
                pe_oi = pd.to_numeric(
                    near_atm[near_atm[type_col].str.upper().isin(["PE", "PUT"])][oi_col], errors="coerce"
                ).sum()
                if ce_oi > 0 and pe_oi > 0:
                    pcr = pe_oi / ce_oi
                    return self._pcr_to_score(pcr)

        # Full-chain PCR fallback
        ce_oi = pd.to_numeric(
            df[df[type_col].str.upper().isin(["CE", "CALL"])][oi_col], errors="coerce"
        ).sum()
        pe_oi = pd.to_numeric(
            df[df[type_col].str.upper().isin(["PE", "PUT"])][oi_col], errors="coerce"
        ).sum()
        if ce_oi <= 0:
            return 50.0

        pcr = pe_oi / ce_oi
        return self._pcr_to_score(pcr)

    @staticmethod
    def _pcr_to_score(pcr: float) -> float:
        """Convert PCR value to 0-100 score using continuous sigmoid-like mapping.

        Score is highest at PCR extremes (< 0.6 or > 1.8) because extreme positioning
        increases probability of sharp directional move (gamma squeeze / capitulation).
        Score is lowest at PCR ≈ 1.0 (balanced, no edge).
        """
        # Distance from balance point (1.0) on log scale
        log_pcr = abs(np.log(max(pcr, 1e-6)))
        # log(0.6/1.0) ≈ 0.51, log(1.8) ≈ 0.59 → target ~70-80 score at these extremes
        # Scale: 0 → 45, 0.5 → 72, 1.0 → 90, 1.5 → 100
        score = 45.0 + min(55.0, log_pcr * 110.0)
        return round(score, 1)

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
            (c for c in df.columns if c.lower() in ("change_pct", "pct_change", "spot_change", "change%")), None
        )
        if chg_col is not None:
            momentum = df[chg_col].mean()
            return min(100.0, max(0.0, 50 + momentum * 10))

        # Fallback: check if spot vs ATM CE LTP suggests direction
        return 50.0

    def _gamma_exposure_score(self, df: pd.DataFrame, spot: float) -> float:
        """
        Gamma Exposure (GEX) score.

        GEX = Σ (gamma × OI × contract_size) per strike, sign-adjusted by option type.
        Dealers are long gamma on PE and short gamma on CE (standard assumption).
        Net negative GEX means dealers must sell as market falls → amplifies moves.
        Net positive GEX means dealers act as stabiliser → dampens moves.

        Score interpretation:
          - Large |GEX| = high dealer hedging pressure = sharp moves more likely → high score
          - GEX ≈ 0 = neutral positioning → medium score (~50)
          - Returns 50.0 if gamma column not present (Dhan Greeks not available)
        """
        gamma_col = next((c for c in df.columns if c.lower() in ("gamma",)), None)
        oi_col = next(
            (c for c in df.columns if c.lower() in ("oi", "open_interest") and "change" not in c.lower()), None
        )
        type_col = next((c for c in df.columns if c.lower() in ("option_type", "type", "ce_pe")), None)

        if gamma_col is None or oi_col is None or type_col is None:
            return 50.0  # No Greeks available — neutral fallback

        df2 = df.copy()
        df2["_gamma"] = pd.to_numeric(df2[gamma_col], errors="coerce").fillna(0.0)
        df2["_oi"] = pd.to_numeric(df2[oi_col], errors="coerce").fillna(0.0)
        df2["_type"] = df2[type_col].str.upper()

        # NSE contract size is typically 50 (NIFTY), 15 (BANKNIFTY), etc.
        # We normalise by spot to make GEX comparable across underlyings.
        contract_size = 50  # conservative default; actual values don't affect rank ordering
        df2["_gex"] = df2.apply(
            lambda r: r["_gamma"] * r["_oi"] * contract_size * (1 if r["_type"] in ("PE", "PUT") else -1),
            axis=1,
        )
        net_gex = df2["_gex"].sum()

        if spot <= 0:
            return 50.0

        # Normalise: |net_gex| / spot → typical NIFTY range ~0-500 units GEX/spot
        normalised = abs(net_gex) / spot
        # Map to 0-100: normalised=0 → 50, normalised=50 → ~75, normalised=200 → ~95
        score = 50.0 + min(50.0, normalised * 0.5)
        return round(score, 1)

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
            .head(10)
            .to_dict(orient="records"),
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
