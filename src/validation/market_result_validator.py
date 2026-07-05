"""
Market Result Validator
=======================
Daily validation: compares predicted top-gain symbols vs ACTUAL NSE top movers.
Computes Spearman rank correlation (ρ) as the key accuracy metric.
Saves reports to state/market_validations/ and emits retrain signal if accuracy drops.
"""

import json
import logging
import os
import sys
import time
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from core.utils.logger import logger
except ImportError:
    logger = logging.getLogger("market_result_validator")

try:
    import requests

    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

RANK_HISTORY_FILE = os.path.join(ROOT_DIR, "state", "gain_rank_history.json")
VALIDATION_DIR = os.path.join(ROOT_DIR, "state", "market_validations")
RETRAIN_FLAG_FILE = os.path.join(ROOT_DIR, "state", "retrain_signal.json")

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
}
NSE_OPTION_CHAIN_URL = "https://www.nseindia.com/api/option-chain-indices"
NSE_FNO_MOST_ACTIVE_URL = "https://www.nseindia.com/api/live-analysis-most-active-securities?index=options"

TRACKED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
RETRAIN_THRESHOLD_RHO = 0.40  # Fire retrain signal if ρ < this for 3 consecutive days
RETRAIN_CONSECUTIVE_DAYS = 3


class MarketResultValidator:
    """
    Validates daily predictions against actual NSE market results.
    Key metric: Spearman Rank Correlation (ρ) between predicted and actual top movers.
    """

    def __init__(self):
        os.makedirs(VALIDATION_DIR, exist_ok=True)

    # ------------------------------------------------------------------ #
    #  Primary API (called by daily_gain_scanner and daily runner)        #
    # ------------------------------------------------------------------ #

    def validate_today(self, prediction_snapshot: Optional[List[Dict]] = None) -> Dict:
        """
        Run full daily validation.
        Returns report dict with rank_correlation, grade, match rates.
        """
        today = date.today().isoformat()
        if prediction_snapshot is None:
            prediction_snapshot = self._load_today_predictions(today)
        if not prediction_snapshot:
            return self._error_report("No predictions found for today")

        actual_results = self._fetch_actual_top_movers()
        if not actual_results:
            return self._error_report("Could not fetch actual market results")

        correlation, details = self._compute_rank_correlation(prediction_snapshot, actual_results)
        grade = self._grade(correlation)

        report = {
            "date": today,
            "validated_at": datetime.now().isoformat(),
            "rank_correlation_spearman": round(correlation, 4),
            "grade": grade,
            "predicted_top_symbols": [r["underlying"] for r in prediction_snapshot[:5]],
            "actual_top_symbols": [r["symbol"] for r in actual_results[:5]],
            "match_rate_top3": self._top_k_overlap(prediction_snapshot, actual_results, k=3),
            "match_rate_top5": self._top_k_overlap(prediction_snapshot, actual_results, k=5),
            "details": details,
            "interpretation": self._interpret(correlation, grade),
            "retrain_signal": False,
        }

        self._save_report(report, today)

        # Check if retrain signal should fire
        if self._should_retrain():
            report["retrain_signal"] = True
            self._emit_retrain_signal()

        logger.info(
            f"MarketResultValidator: {today} ρ={correlation:.3f} grade={grade} "
            f"top3_match={report['match_rate_top3']:.0%}"
        )
        return report

    # Aliases for compatibility with daily_gain_scanner.py
    def run_daily_validation(self) -> Dict:
        return self.validate_today()

    def get_accuracy_trend(self, last_n_days: int = 14) -> Dict:
        return self.get_rolling_accuracy(days=last_n_days)

    def get_rolling_accuracy(self, days: int = 10) -> Dict:
        """Returns rolling validation stats for last N days."""
        reports = self._load_recent_reports(days)
        if not reports:
            return {"error": "No validation reports found", "days": days}

        correlations = [r["rank_correlation_spearman"] for r in reports if "rank_correlation_spearman" in r]
        top3_rates = [r["match_rate_top3"] for r in reports if "match_rate_top3" in r]
        grades = [r.get("grade") for r in reports]

        retrain_needed = len(correlations) >= RETRAIN_CONSECUTIVE_DAYS and all(
            c < RETRAIN_THRESHOLD_RHO for c in correlations[-RETRAIN_CONSECUTIVE_DAYS:]
        )

        return {
            "days_analyzed": len(reports),
            "avg_rank_correlation": round(np.mean(correlations), 4) if correlations else 0,
            "avg_top3_match_rate": round(np.mean(top3_rates), 4) if top3_rates else 0,
            "best_day": max(reports, key=lambda r: r.get("rank_correlation_spearman", 0), default={}).get("date"),
            "worst_day": min(reports, key=lambda r: r.get("rank_correlation_spearman", 1), default={}).get("date"),
            "grades": grades,
            "retrain_signal": retrain_needed,
        }

    # ------------------------------------------------------------------ #
    #  Fetch actual market data from NSE                                  #
    # ------------------------------------------------------------------ #

    def _fetch_actual_top_movers(self) -> List[Dict]:
        nse_data = self._fetch_nse_most_active_options()
        if nse_data:
            return nse_data
        logger.warning("NSE most-active API unavailable — falling back to per-symbol OI")
        results = []
        for symbol in TRACKED_UNDERLYINGS:
            data = self._fetch_nse_option_chain(symbol)
            if data:
                results.append(data)
        results.sort(key=lambda x: x.get("composite_score", 0), reverse=True)
        for i, r in enumerate(results):
            r["market_rank"] = i + 1
        return results

    def _fetch_nse_most_active_options(self) -> List[Dict]:
        if not _REQUESTS_OK:
            return []
        try:
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)
            time.sleep(1)
            resp = session.get(NSE_FNO_MOST_ACTIVE_URL, headers=NSE_HEADERS, timeout=15)
            if resp.status_code != 200:
                return []
            raw = resp.json().get("data", [])
            results = []
            rank = 1
            for item in raw[:20]:
                sym = item.get("symbol", "")
                normalized = self._normalize_symbol(sym)
                if normalized and normalized in TRACKED_UNDERLYINGS:
                    results.append(
                        {
                            "symbol": normalized,
                            "volume": item.get("totalTradedVolume", 0),
                            "oi_change_pct": item.get("pChange", 0),
                            "price_change_pct": item.get("pChange", 0),
                            "composite_score": abs(item.get("pChange", 0)),
                            "market_rank": rank,
                        }
                    )
                    rank += 1
            return results
        except Exception as e:
            logger.warning(f"NSE most-active fetch failed: {e}")
            return []

    def _fetch_nse_option_chain(self, symbol: str) -> Optional[Dict]:
        if not _REQUESTS_OK:
            return None
        try:
            from core.data.nse_session import NSEFetchError, fetch_option_chain_json

            data = fetch_option_chain_json(symbol)
            records = data.get("records", {}).get("data", [])
            total_oi = sum(
                (r.get("CE", {}).get("openInterest", 0) + r.get("PE", {}).get("openInterest", 0)) for r in records
            )
            total_oi_change = sum(
                abs(r.get("CE", {}).get("changeinOpenInterest", 0))
                + abs(r.get("PE", {}).get("changeinOpenInterest", 0))
                for r in records
            )
            oi_change_pct = (total_oi_change / total_oi * 100) if total_oi > 0 else 0
            return {
                "symbol": symbol,
                "oi_change_pct": round(oi_change_pct, 2),
                "price_change_pct": 0,
                "composite_score": oi_change_pct,
            }
        except NSEFetchError as e:
            logger.warning(f"NSE chain fetch failed for {symbol}: {e}")
            return None
        except Exception as e:
            logger.warning(f"NSE chain fetch failed for {symbol}: {e}")
            return None

    # ------------------------------------------------------------------ #
    #  Rank correlation                                                   #
    # ------------------------------------------------------------------ #

    def _compute_rank_correlation(self, predictions: List[Dict], actuals: List[Dict]) -> Tuple[float, List[Dict]]:
        pred_ranks = {r["underlying"]: r.get("rank", i + 1) for i, r in enumerate(predictions)}
        actual_ranks = {r["symbol"]: r.get("market_rank", i + 1) for i, r in enumerate(actuals)}

        max_pred = max(pred_ranks.values(), default=5) + 1
        max_actual = max(actual_ranks.values(), default=5) + 1
        for sym in list(pred_ranks):
            actual_ranks.setdefault(sym, max_actual)
        for sym in list(actual_ranks):
            pred_ranks.setdefault(sym, max_pred)

        symbols = sorted(set(pred_ranks) | set(actual_ranks))
        pred_arr = np.array([pred_ranks[s] for s in symbols], dtype=float)
        actual_arr = np.array([actual_ranks[s] for s in symbols], dtype=float)

        if len(symbols) >= 2:
            rho = float(np.corrcoef(_rank_array(pred_arr), _rank_array(actual_arr))[0, 1])
        else:
            rho = 0.0
        if np.isnan(rho):
            rho = 0.0

        details = [
            {
                "symbol": s,
                "predicted_rank": int(pred_ranks[s]),
                "actual_rank": int(actual_ranks[s]),
                "rank_diff": int(abs(pred_ranks[s] - actual_ranks[s])),
            }
            for s in symbols
        ]
        return rho, details

    def _top_k_overlap(self, predictions: List[Dict], actuals: List[Dict], k: int) -> float:
        pred_top = {r["underlying"] for r in predictions[:k]}
        actual_top = {r["symbol"] for r in actuals[:k]}
        return len(pred_top & actual_top) / k if pred_top else 0.0

    # ------------------------------------------------------------------ #
    #  Grading                                                            #
    # ------------------------------------------------------------------ #

    def _grade(self, rho: float) -> str:
        if rho >= 0.85:
            return "A+"
        elif rho >= 0.70:
            return "A"
        elif rho >= 0.55:
            return "B"
        elif rho >= 0.40:
            return "C"
        elif rho >= 0.20:
            return "D"
        return "F"

    def _interpret(self, rho: float, grade: str) -> str:
        msgs = {
            "A+": "Excellent — predictions nearly match market. Strategy is highly aligned.",
            "A": "Good — strong alignment between predictions and actual top movers.",
            "B": "Acceptable — moderate alignment. Review factor weights.",
            "C": "Weak — limited alignment. Investigate which factors are off.",
            "D": "Poor — predictions missed actual top movers. Retrain signals.",
            "F": "Failed — no meaningful correlation. Full model review required.",
        }
        return msgs.get(grade, "Unknown")

    # ------------------------------------------------------------------ #
    #  Retrain signal                                                     #
    # ------------------------------------------------------------------ #

    def _should_retrain(self) -> bool:
        reports = self._load_recent_reports(RETRAIN_CONSECUTIVE_DAYS)
        if len(reports) < RETRAIN_CONSECUTIVE_DAYS:
            return False
        recent_rhos = [r.get("rank_correlation_spearman", 1.0) for r in reports[-RETRAIN_CONSECUTIVE_DAYS:]]
        return all(rho < RETRAIN_THRESHOLD_RHO for rho in recent_rhos)

    def _emit_retrain_signal(self) -> None:
        signal = {
            "triggered_at": datetime.now().isoformat(),
            "reason": f"Rank correlation below {RETRAIN_THRESHOLD_RHO} for "
            f"{RETRAIN_CONSECUTIVE_DAYS} consecutive days",
            "action": "retrain ensemble_predictor and reoptimize gain_rank factor weights",
        }
        try:
            os.makedirs(os.path.dirname(RETRAIN_FLAG_FILE), exist_ok=True)
            with open(RETRAIN_FLAG_FILE, "w") as f:
                json.dump(signal, f, indent=2)
            logger.warning(f"RETRAIN SIGNAL emitted: {signal['reason']}")
        except Exception as e:
            logger.error(f"Could not write retrain signal: {e}")

    # ------------------------------------------------------------------ #
    #  Persistence                                                        #
    # ------------------------------------------------------------------ #

    def _load_today_predictions(self, today: str) -> List[Dict]:
        if not os.path.exists(RANK_HISTORY_FILE):
            return []
        try:
            with open(RANK_HISTORY_FILE) as f:
                history = json.load(f)
            for snap in reversed(history):
                if snap.get("date") == today:
                    return snap.get("predictions", [])
        except Exception:
            pass
        return []

    def _save_report(self, report: Dict, today: str) -> None:
        path = os.path.join(VALIDATION_DIR, f"market_validation_{today}.json")
        try:
            with open(path, "w") as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save validation report: {e}")

    def _load_recent_reports(self, days: int) -> List[Dict]:
        reports = []
        try:
            for fname in sorted(os.listdir(VALIDATION_DIR), reverse=True)[:days]:
                if fname.endswith(".json"):
                    fpath = os.path.join(VALIDATION_DIR, fname)
                    with open(fpath) as f:
                        reports.append(json.load(f))
        except Exception:
            pass
        return reports

    def _error_report(self, msg: str) -> Dict:
        return {
            "date": date.today().isoformat(),
            "error": msg,
            "rank_correlation_spearman": 0.0,
            "grade": "F",
            "retrain_signal": False,
        }

    def _normalize_symbol(self, sym: str) -> Optional[str]:
        for u in TRACKED_UNDERLYINGS:
            if u in sym.upper():
                return u
        return None


def _rank_array(arr: np.ndarray) -> np.ndarray:
    temp = arr.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(1, len(arr) + 1)
    return ranks.astype(float)
