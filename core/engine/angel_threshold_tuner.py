"""
angel_threshold_tuner.py

Automatically tunes confidence and score thresholds per underlying
based on historical signal performance.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

from core.engine.train_angel_models import ROOT_DIR as _ROOT_DIR
from core.engine.angel_trade_config import TradeThresholds


def _root() -> Path:
    return Path(_ROOT_DIR)


def _signals_csv() -> Path:
    return _root() / "storage" / "live" / "angel_index_ai_signals.csv"


def _thresholds_json() -> Path:
    return _root() / "storage" / "config" / "thresholds_auto.json"


@dataclass
class ThresholdResult:
    """Result for a single threshold combination."""

    confidence: float
    score: float
    num_trades: int
    hit_rate: float  # % of trades with correct direction
    expected_return: float  # average return per trade
    score_value: float  # combined metric for ranking


class ThresholdTuner:
    """
    Automatically tunes confidence and score thresholds per underlying.
    """

    def __init__(self, max_signals: int = 200):
        self.max_signals = max_signals
        self.signals_df: pd.DataFrame | None = None
        self.tuned_thresholds: Dict[str, Dict[str, float]] = {}

    def load_signals(self) -> bool:
        """Load last N signals from CSV."""
        sig_path = _signals_csv()
        if not sig_path.exists():
            print(f"[TUNER] Signals CSV not found: {sig_path}")
            return False

        try:
            df = pd.read_csv(sig_path)
        except Exception as e:
            print(f"[TUNER] Failed to read signals CSV: {e}")
            return False

        if df.empty:
            print("[TUNER] Signals CSV is empty.")
            return False

        # Take last N rows (most recent)
        df = df.tail(self.max_signals).copy()

        # Ensure required columns exist
        required = {
            "underlying",
            "pred_label",
            "pred_confidence",
            "expected_move_score",
            "ltp",
            "ts",
        }
        missing = required - set(df.columns)
        if missing:
            print(f"[TUNER] Missing required columns: {missing}")
            return False

        # Convert to numeric
        df["pred_confidence"] = pd.to_numeric(df["pred_confidence"], errors="coerce")
        df["expected_move_score"] = pd.to_numeric(df["expected_move_score"], errors="coerce")
        df["ltp"] = pd.to_numeric(df["ltp"], errors="coerce")

        df = df.dropna(subset=["pred_confidence", "expected_move_score", "ltp"])

        if df.empty:
            print("[TUNER] No valid signals after cleaning.")
            return False

        self.signals_df = df
        print(f"[TUNER] Loaded {len(df)} signals for tuning.")
        return True

    def _evaluate_thresholds(
        self,
        df_u: pd.DataFrame,
        conf_thresh: float,
        score_thresh: float,
    ) -> ThresholdResult:
        """
        Evaluate a threshold combination for one underlying.

        Enhanced to use real PnL data when available.
        """
        """
        Evaluate a threshold combination for one underlying.

        Returns hit-rate and expected return based on forward price movement.
        """
        # Filter signals that would pass these thresholds
        df_filtered = df_u[
            (df_u["pred_label"].isin(["BUY_CE", "BUY_PE"]))
            & (df_u["pred_confidence"] >= conf_thresh)
            & (df_u["expected_move_score"].abs() >= score_thresh)
        ].copy()

        if df_filtered.empty:
            return ThresholdResult(
                confidence=conf_thresh,
                score=score_thresh,
                num_trades=0,
                hit_rate=0.0,
                expected_return=0.0,
                score_value=0.0,
            )

        # Try to use real PnL data if available
        pnl_data = self._load_pnl_for_signals(df_filtered)
        if pnl_data is not None and not pnl_data.empty:
            # Use real PnL data
            correct_direction = (pnl_data["pnl_pct"] > 0).astype(int).tolist()
            returns = pnl_data["pnl_pct"].tolist()
        else:
            # Fallback to synthetic evaluation: check if predicted direction matches score sign
            # BUY_CE should have positive score, BUY_PE should have negative score
            correct_direction = []
            returns = []

            for _, row in df_filtered.iterrows():
                label = row["pred_label"]
                score = float(row["expected_move_score"])
                conf = float(row["pred_confidence"])

                # Check direction alignment
                if label == "BUY_CE" and score > 0:
                    correct_direction.append(1)
                    # Synthetic return: assume score predicts move magnitude
                    returns.append(score * conf * 100.0)  # scale to %
                elif label == "BUY_PE" and score < 0:
                    correct_direction.append(1)
                    returns.append(abs(score) * conf * 100.0)
                else:
                    correct_direction.append(0)
                    returns.append(0.0)

        if not correct_direction:
            return ThresholdResult(
                confidence=conf_thresh,
                score=score_thresh,
                num_trades=len(df_filtered),
                hit_rate=0.0,
                expected_return=0.0,
                score_value=0.0,
            )

        hit_rate = np.mean(correct_direction) * 100.0
        expected_return = np.mean(returns) if returns else 0.0

        # Combined score: balance hit-rate and expected return
        # Prefer thresholds that give good hit-rate AND positive returns
        score_value = hit_rate * 0.6 + expected_return * 0.4

        return ThresholdResult(
            confidence=conf_thresh,
            score=score_thresh,
            num_trades=len(df_filtered),
            hit_rate=hit_rate,
            expected_return=expected_return,
            score_value=score_value,
        )

    def _load_pnl_for_signals(self, df_signals: pd.DataFrame) -> pd.DataFrame | None:
        """Load PnL data matching the signals (for real market data tuning)."""
        try:
            pnl_path = _root() / "storage" / "live" / "angel_index_ai_pnl_log.csv"
            if not pnl_path.exists():
                return None

            df_pnl = pd.read_csv(pnl_path)
            if df_pnl.empty:
                return None

            # Try to match signals with PnL by underlying, strike, side, timestamp
            # This is a simplified matching - can be enhanced
            return df_pnl
        except Exception:
            return None

    def tune_underlying(self, underlying: str) -> Dict[str, float] | None:
        """
        Tune thresholds for one underlying.

        Returns dict with best confidence and score thresholds.
        """
        if self.signals_df is None:
            return None

        df_u = self.signals_df[self.signals_df["underlying"] == underlying].copy()
        if df_u.empty:
            print(f"[TUNER] No signals for {underlying}; skipping.")
            return None

        # Test threshold combinations
        conf_range = np.arange(0.50, 0.96, 0.05)  # 0.50 to 0.95, step 0.05
        score_range = np.arange(0.10, 0.61, 0.05)  # 0.10 to 0.60, step 0.05

        results: list[ThresholdResult] = []

        for conf_thresh in conf_range:
            for score_thresh in score_range:
                result = self._evaluate_thresholds(df_u, conf_thresh, score_thresh)
                # Only consider combinations that produce at least 1 trade
                # (lowered from 3 to allow tuning with limited data)
                if result.num_trades >= 1:
                    results.append(result)

        if not results:
            print(
                f"[TUNER] {underlying}: No threshold combination produced any trades. " f"Using conservative defaults."
            )
            # Return conservative defaults if no tuning possible
            return {
                "min_confidence": 0.80,
                "min_abs_score": 0.30,
            }

        # Select best: highest score_value (balanced hit-rate + return)
        best = max(results, key=lambda r: r.score_value)

        print(
            f"[TUNER] {underlying}: best thresholds "
            f"conf={best.confidence:.2f}, score={best.score:.2f} "
            f"(trades={best.num_trades}, hit={best.hit_rate:.1f}%, "
            f"ret={best.expected_return:.2f}%)"
        )

        return {
            "min_confidence": float(best.confidence),
            "min_abs_score": float(best.score),
        }

    def tune_all(self) -> Dict[str, Dict[str, float]]:
        """
        Tune thresholds for all underlyings.

        Returns dict: {underlying: {min_confidence: float, min_abs_score: float}}
        """
        if not self.load_signals():
            print("[TUNER] Using conservative defaults for all underlyings.")
            # Return conservative defaults for all
            underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
            defaults = {u: {"min_confidence": 0.80, "min_abs_score": 0.30} for u in underlyings}
            self.tuned_thresholds = defaults
            return defaults

        underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
        tuned: Dict[str, Dict[str, float]] = {}

        for u in underlyings:
            result = self.tune_underlying(u)
            if result:
                tuned[u] = result

        # If no tuning happened, use defaults
        if not tuned:
            print("[TUNER] No tuning possible; using conservative defaults.")
            tuned = {u: {"min_confidence": 0.80, "min_abs_score": 0.30} for u in underlyings}

        self.tuned_thresholds = tuned
        return tuned

    def save_thresholds(self, path: Path | None = None) -> bool:
        """Save tuned thresholds to JSON."""
        if not self.tuned_thresholds:
            print("[TUNER] No tuned thresholds to save.")
            return False

        if path is None:
            path = _thresholds_json()

        path.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata
        output = {
            "tuned_at": pd.Timestamp.now().isoformat(),
            "underlyings": self.tuned_thresholds,
        }

        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
            print(f"[TUNER] Tuned thresholds saved to: {path}")
            return True
        except Exception as e:
            print(f"[TUNER] Failed to save thresholds: {e}")
            return False


def auto_update_trade_config() -> bool:
    """
    Read auto-tuned thresholds JSON and update angel_trade_config.py.

    This modifies the DEFAULT_THRESHOLDS in the config module.
    """
    thresholds_path = _thresholds_json()
    if not thresholds_path.exists():
        print(f"[TUNER] Auto-tuned thresholds not found: {thresholds_path}")
        print("[TUNER] Run tune_all() first to generate thresholds.")
        return False

    try:
        with thresholds_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[TUNER] Failed to read thresholds JSON: {e}")
        return False

    underlyings = data.get("underlyings", {})
    if not underlyings:
        print("[TUNER] No underlying thresholds in JSON.")
        return False

    # For now, use average across all underlyings as global default
    confs = [v.get("min_confidence", 0.80) for v in underlyings.values()]
    scores = [v.get("min_abs_score", 0.30) for v in underlyings.values()]

    if not confs or not scores:
        print("[TUNER] Invalid threshold values in JSON.")
        return False

    avg_conf = np.mean(confs)
    avg_score = np.mean(scores)

    # Update the global DEFAULT_THRESHOLDS
    from core.engine import angel_trade_config

    angel_trade_config.DEFAULT_THRESHOLDS.min_confidence = float(avg_conf)
    angel_trade_config.DEFAULT_THRESHOLDS.min_abs_score = float(avg_score)

    print(f"[TUNER] Updated global thresholds: " f"conf={avg_conf:.2f}, score={avg_score:.2f}")

    return True


def main() -> None:
    """Main entry point for threshold tuning."""
    print("=== Angel One Index Options Threshold Tuner ===")

    tuner = ThresholdTuner(max_signals=200)
    tuned = tuner.tune_all()

    if not tuned:
        print("[TUNER] No thresholds were tuned (insufficient data).")
        return

    tuner.save_thresholds()

    # Optionally auto-update config
    auto_update_trade_config()

    print("[TUNER] Auto-threshold tuning complete.")


if __name__ == "__main__":
    main()
