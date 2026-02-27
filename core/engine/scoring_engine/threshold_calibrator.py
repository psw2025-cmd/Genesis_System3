from pathlib import Path
from typing import Dict, Any

import pandas as pd


def suggest_thresholds_from_history(
    csv_path: Path,
    lookback_rows: int = 2000,
    buy_quantile: float = 0.85,
    sell_quantile: float = 0.15,
) -> Dict[str, Any]:
    """
    System3 AI upgrade: Suggest BUY/SELL thresholds from historical DRY-RUN scores.

    Reads up to the last `lookback_rows` rows from the given CSV and uses the
    distribution of `final_score` (or a compatible proxy) to propose:
      - buy_threshold (upper quantile)
      - sell_threshold (lower quantile)

    Returns a dict:
      {
        "buy": float,
        "sell": float,
        "rows_used": int,
        "raw_buy": float | None,
        "raw_sell": float | None,
      }

    If insufficient data is available, returns defaults:
      buy = 0.40, sell = -0.40
    """

    def _defaults(reason: str) -> Dict[str, Any]:
        return {
            "buy": 0.40,
            "sell": -0.40,
            "rows_used": 0,
            "raw_buy": None,
            "raw_sell": None,
            "reason": reason,
        }

    if not csv_path.exists():
        return _defaults("csv_missing")

    try:
        df = pd.read_csv(csv_path)
    except Exception:
        # Be lenient and try python engine with bad lines skipped
        try:
            df = pd.read_csv(csv_path, engine="python", on_bad_lines="skip")
        except Exception:
            return _defaults("csv_unreadable")

    if df.empty:
        return _defaults("empty")

    if len(df) > lookback_rows:
        df = df.tail(lookback_rows)

    # Detect score column
    score_col = None
    if "final_score" in df.columns:
        score_col = "final_score"
    elif "expected_move_score" in df.columns:
        score_col = "expected_move_score"

    if score_col is None:
        return _defaults("no_score_column")

    series = pd.to_numeric(df[score_col], errors="coerce").dropna()
    if len(series) < 50:
        return _defaults("too_few_rows")

    raw_buy = float(series.quantile(buy_quantile))
    raw_sell = float(series.quantile(sell_quantile))

    def clamp(x: float) -> float:
        return max(-1.0, min(1.0, x))

    buy = clamp(raw_buy)
    sell = clamp(raw_sell)

    return {
        "buy": buy,
        "sell": sell,
        "rows_used": int(len(series)),
        "raw_buy": raw_buy,
        "raw_sell": raw_sell,
        "reason": "ok",
    }
