"""
Market Result Validator
=======================
Compares the system's predicted top-gain symbols against actual NSE market
top movers/gainers for that day.

Key metric: Rank Correlation Score (Spearman's ρ)
  - 1.0 = perfect match (our top picks = actual market top gainers)
  - 0.0 = random
  - <0.0 = inversely wrong

Workflow:
  1. Load today's gain_rank predictions from state/gain_rank_history.json
  2. Fetch actual NSE market top OI gainers / price movers (post-market)
  3. Compute rank correlation + hit rate (how many of our top-N in market top-N)
  4. Save daily report to state/market_validations/market_validation_YYYY-MM-DD.json
  5. Flag if performance degrades — triggers retraining signal
"""

import json
import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import requests

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from core.utils.logger import logger
except ImportError:
    logger = logging.getLogger("market_result_validator")

RANK_HISTORY_FILE = os.path.join(ROOT_DIR, "state", "gain_rank_history.json")
VALIDATION_DIR = os.path.join(ROOT_DIR, "state", "market_validations")

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

TRACKED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]

RETRAINING_THRESHOLD_CORRELATION = 0.3
RETRAINING_THRESHOLD_HIT_RATE = 0.4


def _rank_array(values: List[float]) -> List[float]:
    """Convert values to ranks (1 = highest). Exported for alias import."""
    arr = np.array(values, dtype=float)
    order = np.argsort(-arr)      # descending
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, len(arr) + 1)
    return ranks.tolist()


class MarketResultValidator:
    """
    Validates predicted top-gain symbols against actual NSE market results.
    Primary metric: Spearman rank correlation between predicted and actual rankings.
    """

    def __init__(self):
        os.makedirs(VALIDATION_DIR, exist_ok=True)
        self._session = self._build_nse_session()

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def run_daily_validation(self, target_date: Optional[str] = None) -> Dict:
        """Full daily validation pipeline."""
        target = target_date or datetime.now().strftime("%Y-%m-%d")
        logger.info(f"MarketResultValidator: running for {target}")

        predictions = self._load_predictions(target)
        if not predictions:
            return self._empty_report(target, reason="no_predictions_found")

        actual_rankings = self._fetch_actual_market_rankings()
        if not actual_rankings:
            return self._empty_report(target, reason="market_data_unavailable")

        report = self._compute_validation(target, predictions, actual_rankings)
        self._save_report(target, report)
        self._log_summary(report)
        return report

    def load_validation_history(self, last_n_days: int = 30) -> List[Dict]:
        reports = []
        if not os.path.isdir(VALIDATION_DIR):
            return reports
        for fname in sorted(os.listdir(VALIDATION_DIR), reverse=True)[:last_n_days]:
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(VALIDATION_DIR, fname)) as f:
                        reports.append(json.load(f))
                except Exception:
                    pass
        return reports

    def get_accuracy_trend(self, last_n_days: int = 14) -> Dict:
        """Rolling accuracy trend — used to detect drift and trigger retraining."""
        history = self.load_validation_history(last_n_days)
        if not history:
            return {"status": "no_data", "days": 0}

        correlations = [r["spearman_correlation"] for r in history
                        if r.get("spearman_correlation") is not None]
        hit_rates = [r["hit_rate"] for r in history if r.get("hit_rate") is not None]

        if not correlations:
            return {"status": "no_data", "days": 0}

        avg_corr = float(np.mean(correlations))
        avg_hit = float(np.mean(hit_rates)) if hit_rates else 0.0
        trend = float(np.polyfit(range(len(correlations)), correlations, 1)[0]) \
            if len(correlations) > 2 else 0.0
        retrain = avg_corr < RETRAINING_THRESHOLD_CORRELATION \
            or avg_hit < RETRAINING_THRESHOLD_HIT_RATE

        return {
            "days_analyzed": len(correlations),
            "avg_spearman_correlation": round(avg_corr, 4),
            "avg_hit_rate": round(avg_hit, 4),
            "correlation_trend": round(trend, 6),
            "retrain_signal": retrain,
            "status": "RETRAIN_NEEDED" if retrain else "OK",
        }

    # ------------------------------------------------------------------ #
    #  Predictions loader                                                  #
    # ------------------------------------------------------------------ #

    def _load_predictions(self, target_date: str) -> List[Dict]:
        if not os.path.exists(RANK_HISTORY_FILE):
            return []
        try:
            with open(RANK_HISTORY_FILE) as f:
                history = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load rank history: {e}")
            return []

        day_entries = [e for e in history if e.get("date") == target_date]
        if not day_entries:
            return []
        return day_entries[-1].get("predictions", [])

    # ------------------------------------------------------------------ #
    #  NSE market data                                                     #
    # ------------------------------------------------------------------ #

    def _fetch_actual_market_rankings(self) -> List[Dict]:
        results = []
        for symbol in TRACKED_UNDERLYINGS:
            try:
                data = self._fetch_nse_option_chain(symbol)
                if data:
                    results.append(data)
                time.sleep(0.5)
            except Exception as e:
                logger.warning(f"NSE fetch failed for {symbol}: {e}")

        if not results:
            results = self._fallback_from_stored_chain()

        results.sort(key=lambda x: x.get("combined_gain_score", 0), reverse=True)
        for i, r in enumerate(results):
            r["actual_rank"] = i + 1
        return results

    def _fetch_nse_option_chain(self, symbol: str) -> Optional[Dict]:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        try:
            resp = self._session.get(url, timeout=10)
            resp.raise_for_status()
            payload = resp.json()
        except Exception as e:
            logger.warning(f"NSE API failed for {symbol}: {e}")
            return None

        try:
            records = payload["records"]["data"]
            underlying_value = payload["records"].get("underlyingValue", 0)

            total_ce_oi     = sum(r["CE"]["openInterest"] for r in records if "CE" in r)
            total_pe_oi     = sum(r["PE"]["openInterest"] for r in records if "PE" in r)
            total_ce_chg    = sum(r["CE"].get("changeinOpenInterest", 0) for r in records if "CE" in r)
            total_pe_chg    = sum(r["PE"].get("changeinOpenInterest", 0) for r in records if "PE" in r)
            total_oi        = total_ce_oi + total_pe_oi
            total_chg       = total_ce_chg + total_pe_chg
            oi_change_pct   = (total_chg / total_oi * 100) if total_oi > 0 else 0.0

            atm = sorted(records, key=lambda r: abs(r.get("strikePrice", 0) - underlying_value))[:3]
            ce_pchg = float(np.mean([r["CE"].get("pChange", 0) for r in atm if "CE" in r] or [0]))
            pe_pchg = float(np.mean([r["PE"].get("pChange", 0) for r in atm if "PE" in r] or [0]))
            combined = abs(oi_change_pct) * 0.6 + (abs(ce_pchg) + abs(pe_pchg)) * 0.4

            return {
                "underlying": symbol,
                "oi_change_pct": round(oi_change_pct, 3),
                "atm_ce_pchange": round(ce_pchg, 3),
                "atm_pe_pchange": round(pe_pchg, 3),
                "combined_gain_score": round(combined, 3),
                "underlying_value": underlying_value,
            }
        except (KeyError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"NSE parse error for {symbol}: {e}")
            return None

    def _fallback_from_stored_chain(self) -> List[Dict]:
        return [{"underlying": s, "combined_gain_score": 0.0} for s in TRACKED_UNDERLYINGS]

    # ------------------------------------------------------------------ #
    #  Validation computation                                              #
    # ------------------------------------------------------------------ #

    def _compute_validation(self, target_date: str, predictions: List[Dict],
                            actual_rankings: List[Dict]) -> Dict:
        pred_order   = [p["underlying"] for p in sorted(predictions,    key=lambda x: x.get("rank", 99))]
        actual_order = [a["underlying"] for a in sorted(actual_rankings, key=lambda x: x.get("actual_rank", 99))]
        common = [s for s in pred_order if s in actual_order]

        if len(common) < 2:
            return self._empty_report(target_date, reason="insufficient_overlap")

        pred_ranks   = [pred_order.index(s) + 1   for s in common]
        actual_ranks = [actual_order.index(s) + 1  for s in common]
        spearman_corr = self._spearman(pred_ranks, actual_ranks)

        top_n = min(3, len(pred_order), len(actual_order))
        hit_rate = len(set(pred_order[:top_n]) & set(actual_order[:top_n])) / top_n

        retrain = (spearman_corr < RETRAINING_THRESHOLD_CORRELATION
                   or hit_rate < RETRAINING_THRESHOLD_HIT_RATE)

        return {
            "date": target_date,
            "timestamp": datetime.now().isoformat(),
            "predicted_ranking": pred_order,
            "actual_ranking": actual_order,
            "common_symbols": common,
            "spearman_correlation": round(spearman_corr, 4),
            "hit_rate": round(hit_rate, 4),
            "top_n_evaluated": top_n,
            "retrain_signal": retrain,
            "status": "RETRAIN_NEEDED" if retrain else "OK",
            "actual_details": actual_rankings,
        }

    @staticmethod
    def _spearman(x: List[float], y: List[float]) -> float:
        n = len(x)
        if n < 2:
            return 0.0
        d_sq = sum((xi - yi) ** 2 for xi, yi in zip(x, y))
        return 1 - (6 * d_sq) / (n * (n ** 2 - 1))

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #

    def _save_report(self, target_date: str, report: Dict) -> None:
        path = os.path.join(VALIDATION_DIR, f"market_validation_{target_date}.json")
        try:
            with open(path, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Saved: {path}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

    def _log_summary(self, report: Dict) -> None:
        logger.info(
            f"[Validation] {report['date']} | "
            f"ρ={report.get('spearman_correlation','N/A')} | "
            f"Hit={report.get('hit_rate',0):.0%} | "
            f"{report.get('status')}"
        )
        if report.get("retrain_signal"):
            logger.warning("RETRAIN SIGNAL — accuracy below threshold")

    def _empty_report(self, target_date: str, reason: str) -> Dict:
        return {
            "date": target_date,
            "timestamp": datetime.now().isoformat(),
            "status": "SKIPPED",
            "reason": reason,
            "spearman_correlation": None,
            "hit_rate": None,
            "retrain_signal": False,
        }

    def _build_nse_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(NSE_HEADERS)
        try:
            session.get("https://www.nseindia.com", timeout=8)
        except Exception:
            pass
        return session


if __name__ == "__main__":
    v = MarketResultValidator()
    report = v.run_daily_validation()
    print(json.dumps(report, indent=2))
