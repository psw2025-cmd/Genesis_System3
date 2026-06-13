from pathlib import Path

import pandas as pd

from core.engine.train_dhan_models import ROOT_DIR as _ROOT_DIR


def _root() -> Path:
    return Path(_ROOT_DIR)


def _signals_csv() -> Path:
    return _root() / "storage" / "live" / "dhan_index_ai_signals.csv"


def _trades_plan_csv() -> Path:
    return _root() / "storage" / "live" / "dhan_index_ai_trades_plan.csv"


def seed_dummy_trades(max_trades: int = 3) -> None:
    sig_path = _signals_csv()
    if not sig_path.exists():
        print("[DUMMY] Signals CSV not found:", sig_path)
        return

    df = pd.read_csv(sig_path)
    if df.empty:
        print("[DUMMY] Signals CSV is empty.")
        return

    # Require basic columns to exist (adapted to actual column names)
    required = {
        "underlying",
        "strike",
        "side",
        "ltp",
        "spot",
        "expected_move_score",
        "pred_confidence",
        "ts",
    }
    missing = required - set(df.columns)
    if missing:
        print("[DUMMY] Missing columns in signals CSV:", missing)
        return

    # Work on last snapshot only (max ts)
    last_ts = df["ts"].max()
    df_last = df[df["ts"] == last_ts].copy()

    # Pick strongest candidates by |expected_move_score|
    df_last["abs_score"] = df_last["expected_move_score"].astype(float).abs()
    df_last = df_last.sort_values("abs_score", ascending=False).head(max_trades)

    if df_last.empty:
        print("[DUMMY] No rows in last snapshot to create dummy trades.")
        return

    trades = []
    for _, row in df_last.iterrows():
        ltp = float(row["ltp"])
        # simple +/- % around current price
        target = ltp * 1.10  # +10%
        sl = ltp * 0.95  # -5%

        trades.append(
            {
                "ts": row["ts"],
                "underlying": row["underlying"],
                "strike": row["strike"],
                "side": row["side"],
                "entry_price": ltp,
                "target_price": target,
                "sl_price": sl,
                # Treat as BUY trades for testing CE/PE branches
                "pred_label": "BUY_CE" if row["side"] == "CE" else "BUY_PE",
                "pred_confidence": row["pred_confidence"],
                "expected_move_score": row["expected_move_score"],
            }
        )

    out_path = _trades_plan_csv()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_trades = pd.DataFrame(trades)
    df_trades.to_csv(out_path, index=False, encoding="utf-8")
    print(f"[DUMMY] Seeded {len(df_trades)} dummy trades to: {out_path}")


def main() -> None:
    seed_dummy_trades(max_trades=3)


if __name__ == "__main__":
    main()
