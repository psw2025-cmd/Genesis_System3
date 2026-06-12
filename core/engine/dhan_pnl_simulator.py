import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.train_dhan_models import ROOT_DIR as _ROOT_DIR


@dataclass
class PnLConfig:
    max_snapshots_ahead: int = 10  # how many future snapshots to look at


def _root() -> Path:
    return Path(_ROOT_DIR)


def _signals_csv() -> Path:
    return _root() / "storage" / "live" / "dhan_index_ai_signals.csv"


def _trades_plan_csv() -> Path:
    return _root() / "storage" / "live" / "dhan_index_ai_trades_plan.csv"


def _pnl_out_csv() -> Path:
    return _root() / "storage" / "live" / "dhan_index_ai_pnl_log.csv"


def _load_data():
    sig_path = _signals_csv()
    trades_path = _trades_plan_csv()

    if not sig_path.exists():
        print("[ERROR] Signals CSV not found:", sig_path)
        return None, None
    if not trades_path.exists():
        print("[ERROR] Trades plan CSV not found:", trades_path)
        return None, None

    try:
        df_sig = pd.read_csv(sig_path, engine="python", on_bad_lines="skip")
    except Exception as e:
        print(f"[ERROR] Failed to load signals CSV: {e}")
        return None, None

    try:
        df_tr = pd.read_csv(trades_path, engine="python", on_bad_lines="skip")
    except Exception as e:
        print(f"[ERROR] Failed to load trades plan CSV: {e}")
        return None, None

    if df_sig.empty:
        print("[ERROR] Signals CSV is empty.")
        return None, None
    if df_tr.empty:
        print("[ERROR] Trades plan CSV is empty.")
        return None, None

    return df_sig, df_tr


def _compute_trade_pnl(
    trade_row: pd.Series,
    df_sig: pd.DataFrame,
    cfg: PnLConfig,
) -> dict:
    """
    Simulate this trade using subsequent snapshots:
    - Entry at trade_row['entry_price']
    - Look ahead up to cfg.max_snapshots_ahead snapshots for the same instrument.
    - If TP touched first -> result = 'TP'
    - Else if SL touched first -> result = 'SL'
    - Else -> result = 'TIMEOUT', exit at last seen price.
    """
    u = trade_row.get("underlying")
    strike = trade_row.get("strike")
    side = trade_row.get("side")
    label = trade_row.get("pred_label", "")
    ts_entry = trade_row.get("ts")
    entry = float(trade_row.get("entry_price"))
    target = float(trade_row.get("target_price"))
    sl = float(trade_row.get("sl_price"))

    # Filter signals for same instrument and ts > entry ts
    df_inst = df_sig[
        (df_sig["underlying"] == u)
        & (df_sig["strike"] == strike)
        & (df_sig["side"] == side)
        & (df_sig["ts"] > ts_entry)
    ].copy()

    if df_inst.empty:
        # no future data, can't evaluate
        return {
            "result": "NO_DATA",
            "exit_price": entry,
            "pnl_pct": 0.0,
            "max_fav_pct": 0.0,
            "max_adv_pct": 0.0,
        }

    df_inst = df_inst.sort_values("ts").head(cfg.max_snapshots_ahead)

    prices = df_inst["ltp"].astype(float).values
    max_fav = 0.0
    max_adv = 0.0
    exit_price = prices[-1]
    result = "TIMEOUT"

    for p in prices:
        if label == "BUY_CE":
            ret_pct = (p - entry) / entry * 100.0
            max_fav = max(max_fav, ret_pct)
            max_adv = min(max_adv, ret_pct)

            if p >= target:
                exit_price = p
                result = "TP"
                break
            if p <= sl:
                exit_price = p
                result = "SL"
                break

        elif label == "BUY_PE":
            # For PE, price rises when underlying falls, so reverse sign
            ret_pct_pe = (entry - p) / entry * 100.0
            max_fav = max(max_fav, ret_pct_pe)
            max_adv = min(max_adv, ret_pct_pe)

            if p <= sl:  # SL is below entry for PE in our scheme
                exit_price = p
                result = "SL"
                break
            if p >= target:  # target is above entry
                exit_price = p
                result = "TP"
                break

        else:
            # Should not happen (we only trade BUY_CE/BUY_PE)
            return {
                "result": "INVALID_LABEL",
                "exit_price": entry,
                "pnl_pct": 0.0,
                "max_fav_pct": 0.0,
                "max_adv_pct": 0.0,
            }

    # Compute realized pnl
    if label == "BUY_CE":
        pnl_pct = (exit_price - entry) / entry * 100.0
    else:  # BUY_PE
        pnl_pct = (entry - exit_price) / entry * 100.0

    return {
        "result": result,
        "exit_price": exit_price,
        "pnl_pct": pnl_pct,
        "max_fav_pct": max_fav,
        "max_adv_pct": max_adv,
    }


def run_pnl_simulation(cfg: PnLConfig | None = None) -> pd.DataFrame | None:
    if cfg is None:
        cfg = PnLConfig()

    df_sig, df_tr = _load_data()
    if df_sig is None or df_tr is None:
        return None

    df_tr = df_tr.copy()

    results: list[dict] = []
    for _, row in df_tr.iterrows():
        # Skip HOLD trades if any slipped in
        if row.get("pred_label") not in ("BUY_CE", "BUY_PE"):
            continue
        info = _compute_trade_pnl(row, df_sig, cfg)
        merged = row.to_dict()
        merged.update(info)
        results.append(merged)

    if not results:
        print("[PNL] No trades to evaluate (no BUY_* in trade plan).")
        return None

    df_out = pd.DataFrame(results)

    out_path = _pnl_out_csv()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_path, index=False, encoding="utf-8")
    print(f"[PNL] Detailed trade PnL log written to: {out_path}")

    # Print quick summary
    summary = df_out.groupby("underlying")["pnl_pct"].agg(["count", "mean", "max", "min"]).reset_index()
    print("\n=== PnL SUMMARY BY UNDERLYING ===")
    print(summary.to_string(index=False))

    return df_out


def main() -> None:
    cfg = PnLConfig()
    run_pnl_simulation(cfg)


if __name__ == "__main__":
    main()
