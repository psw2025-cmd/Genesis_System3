import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import sys
from pathlib import Path

# Define _ROOT_DIR relative to this script's location
# dhan_trade_decision.py is in PROJECT_DIR/core/engine/
_ROOT_DIR = Path(__file__).parent.parent.parent.absolute()
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

from core.utils.logger import logger
from core.engine.train_dhan_models import ROOT_DIR as _ROOT_DIR
from core.engine.dhan_trade_config import DEFAULT_THRESHOLDS
from core.engine.dhan_trade_rules import TradeRuleEngine
from core.engine.dhan_safety_checks import get_safety_validator


@dataclass
class TradeConfig:
    min_confidence: float = DEFAULT_THRESHOLDS.min_confidence  # minimum prediction confidence
    min_abs_score: float = DEFAULT_THRESHOLDS.min_abs_score  # minimum |expected_move_score|
    max_moneyness_pct: float = DEFAULT_THRESHOLDS.max_atm_dist_pct  # stay near ATM (|moneyness| <= 1%)
    max_candidates_per_underlying: int = 2
    target_factor: float = DEFAULT_THRESHOLDS.target_pct  # target move in option premium (%)
    sl_factor: float = DEFAULT_THRESHOLDS.stoploss_pct  # stoploss in option premium (%)


def _root() -> Path:
    return Path(_ROOT_DIR)


def _trades_csv() -> Path:
    return _root() / "storage" / "live" / "dhan_index_ai_trades_plan.csv"


def _compute_trade_score(row: pd.Series) -> float:
    """
    Higher score = more attractive trade.
    Uses expected_move_score, confidence, and moneyness penalty.
    """
    label = row.get("pred_label", "HOLD")
    conf = float(row.get("pred_confidence", 0.0))
    score = float(row.get("expected_move_score", 0.0))
    moneyness = float(row.get("moneyness", 0.0))

    # Basic alignment: CE trades should have positive score, PE trades negative
    if label == "BUY_CE" and score <= 0:
        return 0.0
    if label == "BUY_PE" and score >= 0:
        return 0.0
    if label == "HOLD":
        return 0.0

    # Penalize far OTM/ITM (|moneyness| too large)
    # For example, if moneyness = 1.5 (%), penalty > 1 reduces score
    m_penalty = 1.0 + max(0.0, abs(moneyness) - 1.0) * 0.5

    base = abs(score) * conf
    final_score = base / m_penalty
    return final_score


def build_trade_plan(
    df_signals: pd.DataFrame,
    cfg: TradeConfig | None = None,
) -> pd.DataFrame:
    """
    From full signals snapshot, build a small table of best trade ideas.
    One row per chosen trade with entry/target/SL suggestions.
    """
    if df_signals is None or df_signals.empty:
        return pd.DataFrame()

    if cfg is None:
        cfg = TradeConfig()

    engine = TradeRuleEngine(DEFAULT_THRESHOLDS)

    df = df_signals.copy()

    # Evaluate each row via rule engine
    decisions: list[dict] = []
    for _, row in df.iterrows():
        decision = engine.evaluate(row)
        decisions.append(decision)

    if not decisions:
        return pd.DataFrame()

    dec_df = pd.DataFrame(decisions, index=df.index)

    # Keep only eligible BUY_CE / BUY_PE trades
    mask = (dec_df["eligible"]) & (dec_df["action"].isin(["BUY_CE", "BUY_PE"]))
    if not mask.any():
        return df.iloc[0:0].copy()

    df_sel = df.loc[mask].copy()
    df_sel["trade_score"] = dec_df.loc[mask, "trade_score"].astype(float)

    # Group by underlying and pick top candidates per index
    selected_rows: list[pd.DataFrame] = []
    for u, g in df_sel.groupby("underlying"):
        g_sorted = g.sort_values("trade_score", ascending=False)
        selected_rows.append(g_sorted.head(cfg.max_candidates_per_underlying))

    if not selected_rows:
        return df.iloc[0:0].copy()

    df_sel = pd.concat(selected_rows, ignore_index=True)

    # Safety validation for each trade
    validator = get_safety_validator()
    valid_rows = []
    for idx, row in df_sel.iterrows():
        validation = validator.validate_trade_plan(row)
        if validation["valid"]:
            if validation["warnings"]:
                for warn in validation["warnings"]:
                    logger.warning(f"Trade {idx} warning: {warn}")
            valid_rows.append(idx)
        else:
            logger.warning(f"Trade {idx} rejected: {validation['reason']}")

    if not valid_rows:
        return df.iloc[0:0].copy()

    df_sel = df_sel.loc[valid_rows].copy()

    # Compute entry, target, SL, risk/reward
    df_sel["entry_price"] = df_sel["ltp"].astype(float)

    direction = np.where(df_sel["pred_label"] == "BUY_CE", 1.0, -1.0)

    df_sel["target_price"] = df_sel["entry_price"] * (1.0 + direction * cfg.target_factor / 100.0)
    df_sel["sl_price"] = df_sel["entry_price"] * (1.0 - direction * cfg.sl_factor / 100.0)

    move_target = (df_sel["target_price"] - df_sel["entry_price"]) / df_sel["entry_price"] * 100.0
    move_sl = (df_sel["entry_price"] - df_sel["sl_price"]) / df_sel["entry_price"] * 100.0
    df_sel["rr_ratio"] = move_target.abs() / move_sl.abs().replace(0, np.nan)

    # Text fields
    df_sel["suggested_action"] = df_sel["pred_label"]
    df_sel["risk_note"] = np.where(
        df_sel["rr_ratio"] >= 1.5,
        "Good RR",
        "OK/Low RR",
    )

    cols = [
        "ts",
        "underlying",
        "expiry",
        "strike",
        "side",
        "ltp",
        "spot",
        "moneyness",
        "pred_label",
        "pred_confidence",
        "expected_move_score",
        "trade_score",
        "entry_price",
        "target_price",
        "sl_price",
        "rr_ratio",
        "suggested_action",
        "risk_note",
    ]
    cols = [c for c in cols if c in df_sel.columns]
    return df_sel[cols].copy()


def append_trade_plan(plan_df: pd.DataFrame, path: Path | None = None) -> None:
    if plan_df is None or plan_df.empty:
        logger.info("Trade plan empty; nothing to append.")
        return
    if path is None:
        path = _trades_csv()
    path.parent.mkdir(parents=True, exist_ok=True)
    header = not path.exists()
    plan_df.to_csv(path, mode="a", index=False, header=header, encoding="utf-8")
    logger.info("Trade plan appended: rows=%d, path=%s", len(plan_df), str(path))


def print_trade_summary(plan_df: pd.DataFrame) -> None:
    if plan_df is None or plan_df.empty:
        print("[TRADE] No eligible trade candidates in this snapshot.")
        return

    print("=== AI TRADE PLAN SNAPSHOT ===")
    for _, r in plan_df.iterrows():
        print(
            f"{r.get('underlying')} {r.get('expiry')} "
            f"strike={r.get('strike')} side={r.get('side')} "
            f"signal={r.get('pred_label')} conf={r.get('pred_confidence'):.3f} "
            f"score={r.get('trade_score'):.3f} "
            f"entry={r.get('entry_price'):.2f} "
            f"target={r.get('target_price'):.2f} "
            f"SL={r.get('sl_price'):.2f} "
            f"RR={r.get('rr_ratio'):.2f} "
            f"[{r.get('risk_note')}]"
        )


def main() -> None:
    root = _root()
    signals_csv = root / "storage" / "live" / "dhan_index_ai_signals.csv"
    if not signals_csv.exists():
        empty_csv_header = (
            "ts,underlying,expiry,strike,side,ltp,spot,moneyness,pred_label,pred_confidence,expected_move_score\n"
        )
        try:
            signals_csv.parent.mkdir(parents=True, exist_ok=True)
            with open(signals_csv, "w", encoding="utf-8") as f:
                f.write(empty_csv_header)
            logger.info(
                f"Signals CSV not found: '{signals_csv}'. Created an empty file with header. This phase will proceed with an empty DataFrame."
            )
        except Exception as e:
            msg = f"Signals CSV not found: '{signals_csv}', and failed to create an empty one: {e}"
            print(f"[ERROR] {msg}")
            logger.error(msg)
            return
        msg = f"Signals CSV not found: {signals_csv}"
        print(f"[ERROR] {msg}")
        logger.error(msg)
        return

    try:
        df = pd.read_csv(signals_csv, engine="python", on_bad_lines="skip")
    except Exception as e:
        msg = f"Failed to read signals CSV: {e}"
        print(f"[ERROR] {msg}")
        logger.error(msg)
        return

    if df.empty:
        msg = "Signals CSV is empty or contained only headers after creation. No trade plan will be generated."
        print(f"[INFO] {msg}")
        logger.info(msg)
        return
        msg = "Signals CSV is empty."
        print(f"[ERROR] {msg}")
        logger.error(msg)
        return

    # Simple: use last snapshot; assuming 'ts' column exists
    if "ts" in df.columns:
        last_ts = df["ts"].max()
        df_last = df[df["ts"] == last_ts].copy()
    else:
        df_last = df.tail(50).copy()

    cfg = TradeConfig()
    plan_df = build_trade_plan(df_last, cfg)
    print_trade_summary(plan_df)
    append_trade_plan(plan_df)


if __name__ == "__main__":
    main()
