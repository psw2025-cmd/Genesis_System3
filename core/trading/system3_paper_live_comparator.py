#!/usr/bin/env python3
"""Genesis System3 — truthful PAPER market/prediction comparator.

Production/PAPER truth rules:
- use broker-backed prices only; never synthesize or hard-code fallback market prices;
- use only a symbol-specific model artifact;
- invoke the model's real ``predict`` method when the artifact explicitly declares a
  one-feature input contract compatible with this narrow comparator;
- otherwise fail closed with DATA_NOT_READY / MODEL_NOT_READY;
- never place broker orders. This module records PAPER/reference observations only.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, time as dt_time, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import joblib

_BASE_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _BASE_DIR.parents[1] if len(_BASE_DIR.parents) >= 2 else _BASE_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from core.brokers.dhan.market_ltp import INDEX_SECURITY_IDS, fetch_market_quotes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("system3_paper_live_comparator")

IST = ZoneInfo("Asia/Kolkata")


class DataNotReady(RuntimeError):
    """Raised when an authoritative broker quote is unavailable."""


class ModelNotReady(RuntimeError):
    """Raised when no compatible symbol-specific model can be proven."""


def is_market_open_ist(now_dt: Optional[datetime] = None) -> bool:
    """Return the normal weekday NSE cash-session state.

    Official holiday/special-session authority belongs to the central market-session
    service. This helper deliberately does not claim calendar authority; callers use it
    only to avoid generating PAPER fills outside the normal session window.
    """
    now = now_dt or datetime.now(IST)
    if now.weekday() >= 5:
        return False
    return dt_time(9, 15, 0) <= now.time() <= dt_time(15, 30, 0)


def fetch_live_ltp(symbol: str = "NIFTY") -> Optional[float]:
    """Fetch an authoritative positive LTP from Dhan; return ``None`` if unavailable."""
    symbol_clean = symbol.upper()
    sec_id = INDEX_SECURITY_IDS.get(symbol_clean)
    if not sec_id:
        return None

    quotes = fetch_market_quotes({"IDX_I": [str(sec_id)]})
    q = quotes.get(str(sec_id), {}) if isinstance(quotes, dict) else {}
    ltp = q.get("ltp") if isinstance(q, dict) else None
    try:
        value = float(ltp)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def load_prediction(model_path: Path, current_ltp: float) -> float:
    """Invoke a compatible model's real prediction method.

    This narrow comparator can only prove a model whose artifact explicitly declares a
    single input feature. Multi-feature models must be served through the registered
    feature-pipeline inference path instead of guessing their schema here.
    """
    if model_path is None or not model_path.exists():
        raise ModelNotReady("symbol-specific model artifact is unavailable")

    model_obj = joblib.load(model_path)
    predict = getattr(model_obj, "predict", None)
    if not callable(predict):
        raise ModelNotReady("model artifact does not expose predict()")

    n_features = getattr(model_obj, "n_features_in_", None)
    if n_features != 1:
        raise ModelNotReady(
            "comparator refuses unproven feature schema; expected n_features_in_=1"
        )

    raw = predict([[float(current_ltp)]])
    try:
        predicted = float(raw[0])
    except (TypeError, ValueError, IndexError, KeyError) as exc:
        raise ModelNotReady("model predict() returned a non-numeric result") from exc

    if predicted <= 0:
        raise ModelNotReady("model predict() returned a non-positive price")
    return round(predicted, 2)


class System3PaperLiveComparator:
    """Read-only PAPER comparator with broker truth and fail-closed model semantics."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.root = _REPO_ROOT
        self.state_dir = output_dir or (self.root / "state" / "paper_trades")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_file = self.state_dir / "paper_live_comparison_ledger.json"
        self.chart_file = self.state_dir / "live_vs_pred_chart.png"

    def discover_model_for_symbol(self, symbol: str) -> Optional[Path]:
        """Return only a symbol-specific model; never fall back to an arbitrary pickle."""
        sym = symbol.upper()
        matching_models: List[Path] = []
        for p in self.root.rglob("*.pkl"):
            try:
                if p.stat().st_size > 1000 and sym in p.name.upper():
                    matching_models.append(p)
            except OSError:
                continue
        if not matching_models:
            return None
        matching_models.sort(key=lambda x: (len(x.name), x.name))
        return matching_models[0]

    def run_live_loop(
        self,
        symbol: str = "NIFTY",
        iterations: int = 5,
        delay_s: float = 2.0,
    ) -> Dict[str, Any]:
        """Collect broker observations and PAPER comparison rows without inventing truth."""
        market_open = is_market_open_ist()
        symbol_clean = symbol.upper()
        chosen_model = self.discover_model_for_symbol(symbol_clean)
        model_name = chosen_model.name if chosen_model else None

        live_ltp_series: List[float] = []
        pred_series: List[float] = []
        rows: List[Dict[str, Any]] = []

        for i in range(1, iterations + 1):
            observed_at = datetime.now(timezone.utc).isoformat()
            ltp = fetch_live_ltp(symbol_clean)

            base_row: Dict[str, Any] = {
                "iteration": i,
                "timestamp": observed_at,
                "symbol": symbol_clean,
                "market_status": "OPEN" if market_open else "CLOSED",
                "data_source": "dhan",
                "simulated_quantity": 0,
                "gross_pnl": 0.0,
                "transaction_costs": 0.0,
                "net_pnl": 0.0,
                "model_used": model_name,
                "live_trading_enabled": False,
                "order_placement_allowed": False,
            }

            if ltp is None:
                rows.append(
                    {
                        **base_row,
                        "execution_status": "DATA_NOT_READY",
                        "reason": "authoritative Dhan LTP unavailable",
                        "live_ltp": None,
                        "predicted_price": None,
                        "signal_action": "NO_TRADE",
                    }
                )
            elif chosen_model is None:
                live_ltp_series.append(ltp)
                rows.append(
                    {
                        **base_row,
                        "execution_status": "MODEL_NOT_READY",
                        "reason": "no symbol-specific model artifact found",
                        "live_ltp": ltp,
                        "predicted_price": None,
                        "signal_action": "NO_TRADE",
                    }
                )
            else:
                live_ltp_series.append(ltp)
                try:
                    pred = load_prediction(chosen_model, ltp)
                except ModelNotReady as exc:
                    rows.append(
                        {
                            **base_row,
                            "execution_status": "MODEL_NOT_READY",
                            "reason": str(exc),
                            "live_ltp": ltp,
                            "predicted_price": None,
                            "signal_action": "NO_TRADE",
                        }
                    )
                else:
                    pred_series.append(pred)
                    expected_alpha_pct = ((pred - ltp) / ltp) * 100.0
                    action = "BUY" if pred > ltp else "SELL" if pred < ltp else "NO_TRADE"
                    if not market_open:
                        status_label = "MARKET_CLOSED_SNAPSHOT"
                    elif action == "NO_TRADE":
                        status_label = "NO_TRADE"
                    else:
                        status_label = "PAPER_SIGNAL_ONLY"
                    rows.append(
                        {
                            **base_row,
                            "execution_status": status_label,
                            "reason": None,
                            "live_ltp": ltp,
                            "predicted_price": pred,
                            "signal_action": action,
                            "expected_alpha_pct": round(expected_alpha_pct, 4),
                        }
                    )

            if i < iterations:
                time.sleep(delay_s)

        if live_ltp_series and pred_series and len(live_ltp_series) == len(pred_series):
            self._generate_chart(symbol_clean, live_ltp_series, pred_series, market_open)

        ready_predictions = [row for row in rows if row.get("predicted_price") is not None]
        summary = {
            "symbol": symbol_clean,
            "market_open_ist": market_open,
            "market_session": "NORMAL_SESSION" if market_open else "MARKET_CLOSED_STANDBY",
            "simulated_at_utc": datetime.now(timezone.utc).isoformat(),
            "iterations_requested": iterations,
            "iterations_recorded": len(rows),
            "model_active": model_name,
            "prediction_rows_ready": len(ready_predictions),
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate_pct": 0.0,
            "cumulative_net_pnl": 0.0,
            "chart_saved_path": str(self.chart_file) if self.chart_file.exists() else None,
            "live_ltp_series": live_ltp_series,
            "predicted_series": pred_series,
            "trades": rows,
            "truth_contract": "REAL_ONLY_FAIL_CLOSED_V1",
            "live_trading_enabled": False,
            "order_placement_allowed": False,
        }

        self.ledger_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary

    def _generate_chart(
        self,
        symbol: str,
        live_ltps: List[float],
        preds: List[float],
        market_open: bool,
    ) -> None:
        """Generate a comparison chart only from real broker observations + real inference."""
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            plt.figure(figsize=(10, 5), dpi=120)
            iters = list(range(1, len(live_ltps) + 1))
            plt.plot(iters, live_ltps, marker="o", linewidth=2.5, label=f"Dhan {symbol} Spot")
            plt.plot(iters, preds, marker="s", linewidth=2.0, linestyle="--", label=f"Model prediction ({symbol})")
            status_tag = "NORMAL SESSION" if market_open else "MARKET CLOSED SNAPSHOT"
            plt.title(f"Genesis System3 — Broker Spot vs Model Prediction [{status_tag}]", fontsize=13, fontweight="bold", pad=12)
            plt.xlabel("Observation", fontsize=10)
            plt.ylabel("Price (INR)", fontsize=10)
            plt.grid(True, linestyle=":", alpha=0.6)
            plt.legend(frameon=True)
            plt.tight_layout()
            self.chart_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(self.chart_file)
            plt.close()
        except Exception as exc:
            logger.debug("Matplotlib chart generation skipped: %s", exc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Genesis System3 truthful PAPER comparator")
    parser.add_argument("--symbol", default="NIFTY", help="Underlying index symbol")
    parser.add_argument("--live-loop", type=int, default=5, help="Number of observations")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between observations")
    args = parser.parse_args()

    engine = System3PaperLiveComparator()
    result = engine.run_live_loop(symbol=args.symbol, iterations=args.live_loop, delay_s=args.delay)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
