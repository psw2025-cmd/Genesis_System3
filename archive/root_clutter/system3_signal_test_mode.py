"""
System3 Signal Test Mode - DRY-RUN analysis of recent signals.

Reads recent rows from storage/live/angel_index_ai_signals.csv and reports:
- Distribution of component scores (trend/volatility/momentum/ai/final)
- BUY/SELL/HOLD counts
- Top 5 BUY and SELL candidates (if any)

SAFETY: Read-only. Does NOT touch any execution or live-trading flags.
"""

import sys
from pathlib import Path
from datetime import datetime
import argparse

import pandas as pd
import numpy as np

from core.engine.scoring_engine.threshold_calibrator import (
    suggest_thresholds_from_history,
)

ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _signals_csv() -> Path:
    return ROOT_DIR / "storage" / "live" / "angel_index_ai_signals.csv"


def load_recent_signals(lookback_snapshots: int) -> pd.DataFrame:
    path = _signals_csv()
    if not path.exists():
        print(f"[WARN] Signals CSV not found: {path}")
        return pd.DataFrame()
    # Be robust to occasional malformed lines in the live CSV
    try:
        df = pd.read_csv(path)
    except Exception:
        # Fallback: use python engine and skip bad lines
        try:
            df = pd.read_csv(path, engine="python", on_bad_lines="skip")
            print("[WARN] Some malformed lines were skipped while reading signals CSV.")
        except Exception as exc:
            print(f"[ERROR] Failed to read signals CSV: {exc}")
            return pd.DataFrame()

    # Backward compatibility: derive signal/final_score from older schema
    if "signal" not in df.columns and "pred_label" in df.columns:
        pl = df["pred_label"].astype(str).fillna("")

        def _map_pred_label(x: str) -> str:
            x_up = x.upper()
            if "BUY" in x_up:
                return "BUY"
            if "SELL" in x_up:
                return "SELL"
            return "HOLD"

        df["signal"] = pl.map(_map_pred_label)

    if "final_score" not in df.columns:
        if "expected_move_score" in df.columns:
            df["final_score"] = pd.to_numeric(
                df["expected_move_score"],
                errors="coerce",
            ).fillna(0.0)
        elif "pred_confidence" in df.columns:
            # Use confidence as weak proxy if nothing else
            df["final_score"] = pd.to_numeric(
                df["pred_confidence"],
                errors="coerce",
            ).fillna(0.0)
    if df.empty:
        print("[WARN] Signals CSV is empty")
        return df

    # Try to approximate snapshots by timestamp ordering
    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("ts")

    # If each snapshot appends many rows, we still just take the tail
    rows = min(len(df), lookback_snapshots * 100)
    if rows < len(df):
        df = df.tail(rows)

    return df


def filter_underlyings(df: pd.DataFrame, underlyings: list[str]) -> pd.DataFrame:
    if df.empty or "underlying" not in df.columns:
        return df
    return df[df["underlying"].isin(underlyings)].copy()


def describe_scores(df: pd.DataFrame) -> None:
    if df.empty:
        print("[INFO] No data to describe scores.")
        return

    print("\n=== SCORE DISTRIBUTIONS ===")
    cols = [
        "final_score",
        "greeks_score",
        "trend_score",
        "volatility_score",
        "momentum_score",
        "breakout_score",
        "ai_score",
    ]
    for col in cols:
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        print(
            f"{col:16s}: "
            f"min={s.min(): .3f}, max={s.max(): .3f}, "
            f"mean={s.mean(): .3f}, std={s.std(): .3f}"
        )


def describe_signals(df: pd.DataFrame, label: str = "SIGNAL COUNTS") -> None:
    if df.empty or "signal" not in df.columns:
        print("[INFO] No signal column available.")
        return

    print(f"\n=== {label} ===")
    counts = df["signal"].value_counts(dropna=False).to_dict()
    for sig, cnt in counts.items():
        print(f"{sig}: {cnt}")


def top_candidates(df: pd.DataFrame) -> None:
    if df.empty:
        print("[INFO] No data for top candidates.")
        return

    if "signal" not in df.columns:
        print("[INFO] No 'signal' column; cannot compute BUY/SELL lists.")
        return

    print("\n=== TOP BUY CANDIDATES ===")
    buys = df[df["signal"] == "BUY"].copy()
    if buys.empty:
        print("No BUY candidates in lookback window.")
    else:
        buys = buys.sort_values("final_score", ascending=False).head(5)
        print(
            buys[
                [
                    c
                    for c in [
                        "ts",
                        "underlying",
                        "strike",
                        "side",
                        "ltp",
                        "spot",
                        "final_score",
                        "trend_score",
                        "volatility_score",
                        "momentum_score",
                        "ai_score",
                    ]
                    if c in buys.columns
                ]
            ].to_string(index=False)
        )

    print("\n=== TOP SELL CANDIDATES ===")
    sells = df[df["signal"] == "SELL"].copy()
    if sells.empty:
        print("No SELL candidates in lookback window.")
    else:
        sells = sells.sort_values("final_score", ascending=True).head(5)
        print(
            sells[
                [
                    c
                    for c in [
                        "ts",
                        "underlying",
                        "strike",
                        "side",
                        "ltp",
                        "spot",
                        "final_score",
                        "trend_score",
                        "volatility_score",
                        "momentum_score",
                        "ai_score",
                    ]
                    if c in sells.columns
                ]
            ].to_string(index=False)
        )


def log_to_file(df: pd.DataFrame, lookback: int, underlyings: list[str]) -> None:
    logs_dir = ROOT_DIR / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts_str = datetime.now().strftime("%Y%m%d_%H%M")
    path = logs_dir / f"signal_test_mode_{ts_str}.log"

    try:
        with path.open("w", encoding="utf-8") as f:
            f.write(f"Timestamp: {ts_str}\n")
            f.write(f"Lookback snapshots: {lookback}\n")
            f.write(f"Underlyings: {','.join(underlyings)}\n")
            f.write(f"Rows loaded: {len(df)}\n")
            if "signal" in df.columns:
                counts = df["signal"].value_counts(dropna=False).to_dict()
                f.write(f"Signal counts: {counts}\n")
    except Exception:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="System3 Signal Test Mode (DRY-RUN analysis)"
    )
    parser.add_argument(
        "--lookback-snapshots",
        type=int,
        default=20,
        help="Approximate number of recent snapshots to analyse.",
    )
    parser.add_argument(
        "--underlyings",
        type=str,
        default="NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY,SENSEX",
        help="Comma-separated list of underlyings to include.",
    )
    parser.add_argument(
        "--auto-thresholds",
        action="store_true",
        help="Use auto-calibrated BUY/SELL thresholds from historical final_score.",
    )
    parser.add_argument(
        "--use-live-thresholds",
        action="store_true",
        help="Use thresholds from system3_live_thresholds.json (from Phase 222 EV analysis).",
    )
    args = parser.parse_args()

    underlyings = [u.strip() for u in args.underlyings.split(",") if u.strip()]

    print("=== SYSTEM3 SIGNAL TEST MODE (DRY-RUN) ===")
    print(f"Lookback snapshots: {args.lookback_snapshots}")
    print(f"Underlyings: {', '.join(underlyings)}")

    df = load_recent_signals(args.lookback_snapshots)
    if df.empty:
        print("[WARN] No recent signals loaded.")
        return

    df = filter_underlyings(df, underlyings)
    if df.empty:
        print("[WARN] No signals after underlying filter.")
        return

    # Store original signals for comparison
    df_original = df.copy()
    
    # Optional auto-threshold calibration for analysis-only reclassification
    auto_counts = None
    live_counts = None
    
    if args.auto_thresholds:
        csv_path = _signals_csv()
        calib = suggest_thresholds_from_history(
            csv_path,
            lookback_rows=args.lookback_snapshots,
        )
        print(
            "\n[AUTO-THRESHOLDS] "
            f"rows_used={calib.get('rows_used', 0)}, "
            f"raw_buy={calib.get('raw_buy')}, raw_sell={calib.get('raw_sell')}, "
            f"buy={calib.get('buy')}, sell={calib.get('sell')}, "
            f"reason={calib.get('reason')}"
        )
        # Recompute signal column locally from final_score using suggested thresholds
        s = pd.to_numeric(df["final_score"], errors="coerce").fillna(0.0)
        buy_thr = float(calib["buy"])
        sell_thr = float(calib["sell"])

        def _cls(x: float) -> str:
            if x > buy_thr:
                return "BUY"
            if x < sell_thr:
                return "SELL"
            return "HOLD"

        df["signal"] = s.apply(_cls)
        auto_counts = df["signal"].value_counts().to_dict()
        print(
            f"[INFO] Using auto-thresholds buy={buy_thr:.3f}, sell={sell_thr:.3f} "
            "for analysis only (no changes written to CSV)."
        )
    
    # Optional live-thresholds from Phase 222 EV analysis
    if args.use_live_thresholds:
        try:
            from core.engine.threshold_loader import load_thresholds
            thresholds = load_thresholds(prefer_candidates=True)
            
            s = pd.to_numeric(df_original["final_score"], errors="coerce").fillna(0.0)
            
            def _cls_live(row: pd.Series) -> str:
                score = row["final_score"]
                underlying = row.get("underlying", "")
                
                # Get thresholds for this underlying or use default
                if underlying in thresholds:
                    buy_thr = thresholds[underlying]["buy"]
                    sell_thr = thresholds[underlying]["sell"]
                else:
                    buy_thr = thresholds.get("default", {}).get("buy", 0.40)
                    sell_thr = thresholds.get("default", {}).get("sell", -0.40)
                
                if score > buy_thr:
                    return "BUY"
                if score < sell_thr:
                    return "SELL"
                return "HOLD"
            
            df_live = df_original.copy()
            df_live["signal"] = df_live.apply(_cls_live, axis=1)
            live_counts = df_live["signal"].value_counts().to_dict()
            
            print("\n[LIVE-THRESHOLDS] Loaded from system3_live_thresholds.json")
            for key, val in thresholds.items():
                if key in ["default", "NIFTY", "BANKNIFTY"]:
                    print(f"  {key}: buy={val['buy']:.3f}, sell={val['sell']:.3f}")
            
            # If both modes requested, show comparison
            if args.auto_thresholds:
                print("\n=== THRESHOLD COMPARISON ===")
                print("Auto-Thresholds Counts:", auto_counts)
                print("Live-Thresholds Counts:", live_counts)
            
            # Use live thresholds for main output
            df = df_live
        except Exception as e:
            print(f"[WARN] Failed to load live thresholds: {e}")
            if not args.auto_thresholds:
                print("[INFO] Using existing signal labels from CSV.")
    
    if not args.auto_thresholds and not args.use_live_thresholds:
        print("[INFO] Using existing signal labels from CSV (no threshold override).")

    describe_scores(df)
    describe_signals(df, label="SIGNAL COUNTS (analysis)")
    top_candidates(df)
    log_to_file(df, args.lookback_snapshots, underlyings)
    
    # Generate comparison report if both modes were used
    if args.auto_thresholds and args.use_live_thresholds and auto_counts and live_counts:
        comparison_path = ROOT_DIR / "docs" / "system3_thresholds_comparison.md"
        comparison_path.parent.mkdir(parents=True, exist_ok=True)
        
        with comparison_path.open("w", encoding="utf-8") as f:
            f.write("# System3 Thresholds Comparison\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Lookback Snapshots**: {args.lookback_snapshots}\n\n")
            f.write("## Signal Counts Comparison\n\n")
            f.write("| Signal | Auto-Thresholds | Live-Thresholds | Difference |\n")
            f.write("|--------|----------------|-----------------|------------|\n")
            for sig in ["BUY", "SELL", "HOLD"]:
                auto_cnt = auto_counts.get(sig, 0)
                live_cnt = live_counts.get(sig, 0)
                diff = live_cnt - auto_cnt
                f.write(f"| {sig} | {auto_cnt} | {live_cnt} | {diff:+d} |\n")
        
        print(f"\n[INFO] Comparison report saved to: {comparison_path}")


if __name__ == "__main__":
    main()


