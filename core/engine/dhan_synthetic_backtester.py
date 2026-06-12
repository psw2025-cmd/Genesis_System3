"""
Synthetic backtester for Dhan index options.

Uses:
- Trained models from core/models/dhan/*_model.pkl
- Trade rules / thresholds from core/engine/dhan_trade_config.py
- Synthetic intraday price paths (index + options)

Produces:
- Detailed trade log CSV
- Summary stats CSV
"""

import os
import json
import time
import math
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import joblib

from core.engine.train_dhan_models import ROOT_DIR as _ROOT_DIR
from core.engine.dhan_trade_config import DEFAULT_THRESHOLDS
from core.engine.dhan_live_ai_signals import load_models_and_meta, _ensure_features_for_df


PROJECT_ROOT = Path(_ROOT_DIR)
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan"
BACKTEST_DIR = PROJECT_ROOT / "storage" / "backtests"
BACKTEST_DIR.mkdir(parents=True, exist_ok=True)


# Base spot prices (approximate)
BASE_SPOTS = {
    "NIFTY": 22000.0,
    "BANKNIFTY": 49000.0,
    "FINNIFTY": 28000.0,
    "MIDCPNIFTY": 14000.0,
    "SENSEX": 72000.0,
}

# Strike step sizes
STRIKE_STEPS = {
    "NIFTY": 50,
    "BANKNIFTY": 100,
    "FINNIFTY": 50,
    "MIDCPNIFTY": 25,
    "SENSEX": 100,
}


def generate_synthetic_intraday_paths(
    underlying_list=("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"),
    steps_per_day=60,
    seed=42,
) -> pd.DataFrame:
    """
    Generate synthetic intraday index + options snapshot sequences.

    Returns: DataFrame with columns:
        ['ts', 'underlying', 'strike', 'side', 'spot', 'ltp', 'moneyness',
         'atm_dist_abs', 'atm_dist_pct', 'ce_pe_ratio', 'ce_pe_diff',
         'spot_chg_1_pct', 'ltp_chg_1_pct', 'spot_roll_std_5', 'ltp_roll_std_5']
    """
    np.random.seed(seed)
    all_rows = []

    start_time = datetime.now().replace(hour=9, minute=15, second=0, microsecond=0)

    for underlying in underlying_list:
        base_spot = BASE_SPOTS[underlying]
        strike_step = STRIKE_STEPS[underlying]

        # Generate spot path (random walk with small drift)
        spot_path = [base_spot]
        for i in range(1, steps_per_day):
            # Small random walk: drift ±0.1% per step
            change_pct = np.random.normal(0.0, 0.15)  # ~0.15% volatility per step
            new_spot = spot_path[-1] * (1.0 + change_pct / 100.0)
            spot_path.append(new_spot)

        # For each timestep, generate option legs
        for step_idx, spot in enumerate(spot_path):
            ts = start_time + timedelta(minutes=step_idx)

            # Compute ATM strike (nearest strike_step)
            atm_strike = round(spot / strike_step) * strike_step

            # 3 strikes: atm - 1, atm, atm + 1
            strikes = [atm_strike - strike_step, atm_strike, atm_strike + strike_step]

            # For each strike and side, synthesize ltp
            for strike in strikes:
                for side in ["CE", "PE"]:
                    # Synthesize premium based on moneyness
                    moneyness = (spot - strike) / strike * 100.0  # %
                    atm_dist_abs = abs(spot - strike)
                    atm_dist_pct = abs(moneyness)

                    # Premium formula: higher near ATM, lower far OTM
                    if side == "CE":
                        # CE: higher premium when spot > strike (ITM)
                        base_premium = max(0.1, abs(moneyness) * 10.0)
                        # Add some randomness
                        ltp = base_premium * (1.0 + np.random.normal(0.0, 0.1))
                    else:  # PE
                        # PE: higher premium when spot < strike (ITM)
                        base_premium = max(0.1, abs(moneyness) * 10.0)
                        ltp = base_premium * (1.0 + np.random.normal(0.0, 0.1))

                    # Ensure minimum premium
                    ltp = max(1.0, ltp)

                    all_rows.append(
                        {
                            "ts": ts,
                            "underlying": underlying,
                            "strike": strike,
                            "side": side,
                            "spot": spot,
                            "ltp": ltp,
                            "moneyness": moneyness,
                            "atm_dist_abs": atm_dist_abs,
                            "atm_dist_pct": atm_dist_pct,
                        }
                    )

    df = pd.DataFrame(all_rows)

    # Compute additional features (similar to training)
    df = df.sort_values(["underlying", "side", "strike", "ts"])

    # CE/PE ratio and diff (per underlying, strike, ts)
    df["ce_pe_ratio"] = 1.0
    df["ce_pe_diff"] = 0.0

    for underlying in underlying_list:
        for strike in df[df["underlying"] == underlying]["strike"].unique():
            for ts in df[df["underlying"] == underlying]["ts"].unique():
                mask = (df["underlying"] == underlying) & (df["strike"] == strike) & (df["ts"] == ts)
                ce_row = df[mask & (df["side"] == "CE")]
                pe_row = df[mask & (df["side"] == "PE")]

                if not ce_row.empty and not pe_row.empty:
                    ce_ltp = ce_row.iloc[0]["ltp"]
                    pe_ltp = pe_row.iloc[0]["ltp"]
                    ratio = ce_ltp / pe_ltp if pe_ltp > 0 else 1.0
                    diff = ce_ltp - pe_ltp

                    df.loc[mask & (df["side"] == "CE"), "ce_pe_ratio"] = ratio
                    df.loc[mask & (df["side"] == "CE"), "ce_pe_diff"] = diff
                    df.loc[mask & (df["side"] == "PE"), "ce_pe_ratio"] = 1.0 / ratio if ratio > 0 else 1.0
                    df.loc[mask & (df["side"] == "PE"), "ce_pe_diff"] = -diff

    # Rolling features (spot_chg_1_pct, ltp_chg_1_pct, rolling std)
    df["spot_chg_1_pct"] = 0.0
    df["ltp_chg_1_pct"] = 0.0
    df["spot_roll_std_5"] = 0.0
    df["ltp_roll_std_5"] = 0.0

    for underlying in underlying_list:
        for strike in df[df["underlying"] == underlying]["strike"].unique():
            for side in ["CE", "PE"]:
                mask = (df["underlying"] == underlying) & (df["strike"] == strike) & (df["side"] == side)
                subset = df[mask].sort_values("ts").copy()

                if len(subset) > 1:
                    subset["spot_chg_1_pct"] = subset["spot"].pct_change(1) * 100.0
                    subset["ltp_chg_1_pct"] = subset["ltp"].pct_change(1) * 100.0
                    subset["spot_roll_std_5"] = subset["spot"].rolling(5, min_periods=1).std()
                    subset["ltp_roll_std_5"] = subset["ltp"].rolling(5, min_periods=1).std()

                    df.loc[mask, "spot_chg_1_pct"] = subset["spot_chg_1_pct"].values
                    df.loc[mask, "ltp_chg_1_pct"] = subset["ltp_chg_1_pct"].values
                    df.loc[mask, "spot_roll_std_5"] = subset["spot_roll_std_5"].values
                    df.loc[mask, "ltp_roll_std_5"] = subset["ltp_roll_std_5"].values

    # Fill NaNs
    df = df.fillna(0.0)

    return df


def load_models() -> dict:
    """
    Load per-underlying models and their metadata from MODELS_DIR.
    Returns dict: underlying -> {model, feature_cols, classes}
    """
    models = {}
    underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]

    for underlying in underlyings:
        model_path = MODELS_DIR / f"{underlying}_model.pkl"
        meta_path = MODELS_DIR / f"{underlying}_model_meta.json"

        if not model_path.exists() or not meta_path.exists():
            print(f"[BACKTEST] Model not found for {underlying}; skipping.")
            continue

        try:
            model = joblib.load(model_path)
            with meta_path.open("r") as f:
                meta = json.load(f)

            # Feature columns: training code stores this under "features"
            feature_cols = meta.get("features") or meta.get("feature_cols")
            if not feature_cols:
                # Fallback to model's own feature names if available
                feature_cols = getattr(model, "feature_names_in_", None)
                if feature_cols is None:
                    print(f"[BACKTEST] No feature list in meta/model for {underlying}; skipping.")
                    continue

            feature_cols = list(feature_cols)

            # Use model.classes_ for label ordering
            classes = getattr(model, "classes_", None)
            if classes is None:
                classes = meta.get("classes", [])

            models[underlying] = {
                "model": model,
                "feature_cols": feature_cols,
                "classes": list(classes),
            }
            print(f"[BACKTEST] Loaded {underlying}: {len(feature_cols)} features, {len(classes)} classes")
        except Exception as e:
            print(f"[BACKTEST] Failed to load model for {underlying}: {e}")
            continue

    return models


def run_models_on_snapshot(df_snapshot: pd.DataFrame, models: dict) -> pd.DataFrame:
    """
    Given one snapshot DataFrame (one timestamp, several legs),
    run models per underlying and return DataFrame with columns:
    ['underlying', 'strike', 'side', 'ltp', 'spot',
     'signal', 'confidence', 'score']
    """
    results = []

    for underlying, model_info in models.items():
        df_u = df_snapshot[df_snapshot["underlying"] == underlying].copy()
        if df_u.empty:
            continue

        model = model_info["model"]
        feature_cols = model_info["feature_cols"]
        classes = model_info["classes"]

        if not feature_cols:
            print(f"[BACKTEST] No feature columns for {underlying}; skipping.")
            continue

        # Ensure features exist
        df_u = _ensure_features_for_df(df_u, feature_cols)

        # Verify all features are present
        missing = [c for c in feature_cols if c not in df_u.columns]
        if missing:
            print(f"[BACKTEST] Missing features for {underlying}: {missing}")
            continue

        # Build feature matrix
        X = df_u[feature_cols].values

        if X.shape[1] == 0:
            print(
                f"[BACKTEST] Empty feature matrix for {underlying} (cols={len(feature_cols)}, df_cols={list(df_u.columns)[:5]}...)"
            )
            continue

        # Predict
        try:
            probs = model.predict_proba(X)
            preds = model.predict(X)
        except Exception as e:
            print(f"[BACKTEST] Prediction failed for {underlying}: {e}")
            continue

        # Map predictions to labels
        for idx, row in df_u.iterrows():
            pred_idx = list(df_u.index).index(idx)
            pred_class = preds[pred_idx]
            prob_vec = probs[pred_idx]

            # Find class index
            if pred_class in classes:
                class_idx = classes.index(pred_class)
                confidence = float(prob_vec[class_idx])
            else:
                confidence = float(np.max(prob_vec))

            signal = pred_class

            # Compute score
            spot = float(row.get("spot", 0.0))
            strike = float(row.get("strike", 0.0))
            moneyness = float(row.get("moneyness", 0.0))

            if signal == "BUY_CE":
                # Positive score for CE
                score = confidence * (1.0 - abs(moneyness) / 10.0)  # penalize far OTM
            elif signal == "BUY_PE":
                # Negative score for PE
                score = -confidence * (1.0 - abs(moneyness) / 10.0)
            else:  # HOLD
                score = 0.0

            results.append(
                {
                    "underlying": underlying,
                    "strike": row["strike"],
                    "side": row["side"],
                    "ltp": row["ltp"],
                    "spot": spot,
                    "signal": signal,
                    "confidence": confidence,
                    "score": score,
                }
            )

    return pd.DataFrame(results)


def select_trades_from_signals(
    df_signals: pd.DataFrame,
    conf_thresh: float,
    score_thresh: float,
) -> pd.DataFrame:
    """
    From signals DataFrame, select trade candidates based on:
    - signal in {'BUY_CE', 'BUY_PE'}
    - confidence >= conf_thresh
    - abs(score) >= score_thresh
    - near-ATM (optional, |atm_dist_pct| <= 0.5 or similar)

    Returns DataFrame of planned trades.
    """
    df = df_signals.copy()

    # Filter eligible trades
    mask = (
        (df["signal"].isin(["BUY_CE", "BUY_PE"]))
        & (df["confidence"] >= conf_thresh)
        & (df["score"].abs() >= score_thresh)
    )

    df_trades = df[mask].copy()

    if df_trades.empty:
        return pd.DataFrame()

    # Add metadata
    df_trades["conf_thresh"] = conf_thresh
    df_trades["score_thresh"] = score_thresh
    df_trades["ltp_entry"] = df_trades["ltp"]
    df_trades["spot_entry"] = df_trades["spot"]

    return df_trades


def simulate_trade_pnl(
    trade_row: pd.Series,
    future_snapshots: pd.DataFrame,
    exit_steps: int = 3,
    sl_pct: float = 5.0,
    tp_pct: float = 10.0,
) -> dict:
    """
    Given one planned trade and future snapshots for that option,
    simulate PnL with simple rules:
    - Stoploss if price moves -sl_pct
    - Take-profit if price moves +tp_pct
    - Else exit at last step's price.

    Returns dict with pct_pnl, exit_reason, exit_price.
    """
    underlying = trade_row["underlying"]
    strike = trade_row["strike"]
    side = trade_row["side"]
    signal = trade_row["signal"]
    entry_price = float(trade_row["ltp_entry"])

    # Filter future snapshots for this option
    mask = (
        (future_snapshots["underlying"] == underlying)
        & (future_snapshots["strike"] == strike)
        & (future_snapshots["side"] == side)
    )
    future = future_snapshots[mask].sort_values("ts").head(exit_steps)

    if future.empty:
        return {
            "pct_pnl": 0.0,
            "exit_reason": "NO_DATA",
            "exit_price": entry_price,
        }

    # Check for TP/SL at each step
    for _, future_row in future.iterrows():
        future_price = float(future_row["ltp"])
        pct_change = ((future_price - entry_price) / entry_price) * 100.0

        # For BUY_CE: profit if price goes up
        # For BUY_PE: profit if price goes down (but we track ltp, so same logic)
        if signal == "BUY_CE":
            if pct_change >= tp_pct:
                return {
                    "pct_pnl": pct_change,
                    "exit_reason": "TAKE_PROFIT",
                    "exit_price": future_price,
                }
            if pct_change <= -sl_pct:
                return {
                    "pct_pnl": pct_change,
                    "exit_reason": "STOP_LOSS",
                    "exit_price": future_price,
                }
        elif signal == "BUY_PE":
            # For PE, we want price to go down, but ltp tracks premium
            # Simplified: same logic (premium moves with spot direction)
            if pct_change >= tp_pct:
                return {
                    "pct_pnl": pct_change,
                    "exit_reason": "TAKE_PROFIT",
                    "exit_price": future_price,
                }
            if pct_change <= -sl_pct:
                return {
                    "pct_pnl": pct_change,
                    "exit_reason": "STOP_LOSS",
                    "exit_price": future_price,
                }

    # No TP/SL hit; exit at last step
    last_price = float(future.iloc[-1]["ltp"])
    pct_change = ((last_price - entry_price) / entry_price) * 100.0

    return {
        "pct_pnl": pct_change,
        "exit_reason": "TIMEOUT",
        "exit_price": last_price,
    }


def run_backtest(
    steps_per_day: int = 60,
    profile: str = "CONSERVATIVE",
    conf_thresh: float | None = None,
    score_thresh: float | None = None,
    exit_steps: int = 3,
    sl_pct: float = 5.0,
    tp_pct: float = 10.0,
) -> None:
    """
    Main backtest runner:
    - Generate synthetic intraday paths
    - For each timestep except last exit_steps:
        * Build snapshot signals using models
        * Select trades using thresholds
        * For each trade, simulate PnL on next 'exit_steps' snapshots
    - Collect all trades and PnL into a DataFrame
    - Save detailed and summary CSVs
    - Print summary to console.

    Args:
        profile: 'CONSERVATIVE' uses production-like thresholds, 'DEV' uses relaxed thresholds for testing
    """
    print("=== ANGEL ONE INDEX OPTIONS - SYNTHETIC BACKTEST ===")

    # Profile logic
    if profile.upper() == "CONSERVATIVE":
        if conf_thresh is None:
            conf_thresh = 0.80
        if score_thresh is None:
            score_thresh = 0.30
        profile_name = "CONSERVATIVE"
    elif profile.upper() == "DEV":
        # Relaxed thresholds just for dev/testing
        if conf_thresh is None:
            conf_thresh = 0.60
        if score_thresh is None:
            score_thresh = 0.15
        profile_name = "DEV"
    else:
        raise ValueError(f"Unknown profile: {profile}")

    print(f"[BACKTEST] Profile: {profile_name}, conf>={conf_thresh:.2f}, |score|>={score_thresh:.2f}")
    print(f"[BACKTEST] Exit steps: {exit_steps}, SL={sl_pct}%, TP={tp_pct}%")

    # Load models
    print("[BACKTEST] Loading models...")
    models = load_models()
    if not models:
        print("[ERROR] No models loaded. Run training first.")
        return

    print(f"[BACKTEST] Loaded {len(models)} models.")

    # Generate synthetic paths
    print(f"[BACKTEST] Generating synthetic intraday paths ({steps_per_day} steps)...")
    df_paths = generate_synthetic_intraday_paths(steps_per_day=steps_per_day)
    print(f"[BACKTEST] Generated {len(df_paths)} option legs across all timesteps.")

    # Get unique timestamps
    timestamps = sorted(df_paths["ts"].unique())
    print(f"[BACKTEST] Processing {len(timestamps)} timesteps...")

    all_trades = []
    signal_stats = {"total": 0, "BUY_CE": 0, "BUY_PE": 0, "HOLD": 0, "passed_filter": 0}
    conf_values = []
    score_values = []

    # Process each timestep (except last exit_steps)
    for i, ts in enumerate(timestamps[:-exit_steps]):
        if (i + 1) % 10 == 0:
            print(f"[BACKTEST] Processing timestep {i+1}/{len(timestamps)-exit_steps}...")

        # Get snapshot for this timestamp
        df_snap = df_paths[df_paths["ts"] == ts].copy()

        # Run models
        df_signals = run_models_on_snapshot(df_snap, models)
        if df_signals.empty:
            continue

        # Collect signal statistics
        signal_stats["total"] += len(df_signals)
        for signal_type in ["BUY_CE", "BUY_PE", "HOLD"]:
            signal_stats[signal_type] += (df_signals["signal"] == signal_type).sum()
        conf_values.extend(df_signals["confidence"].tolist())
        score_values.extend(df_signals["score"].abs().tolist())

        # Select trades
        df_trades = select_trades_from_signals(df_signals, conf_thresh, score_thresh)
        signal_stats["passed_filter"] += len(df_trades)
        if df_trades.empty:
            continue

        # Get future snapshots for PnL simulation
        future_start_idx = i + 1
        future_end_idx = min(i + 1 + exit_steps, len(timestamps))
        future_ts = timestamps[future_start_idx:future_end_idx]
        df_future = df_paths[df_paths["ts"].isin(future_ts)].copy()

        # Simulate PnL for each trade
        for _, trade_row in df_trades.iterrows():
            pnl_result = simulate_trade_pnl(trade_row, df_future, exit_steps, sl_pct, tp_pct)

            trade_record = {
                "ts": ts,
                "underlying": trade_row["underlying"],
                "strike": trade_row["strike"],
                "side": trade_row["side"],
                "signal": trade_row["signal"],
                "confidence": trade_row["confidence"],
                "score": trade_row["score"],
                "ltp_entry": trade_row["ltp_entry"],
                "spot_entry": trade_row["spot_entry"],
                "exit_price": pnl_result["exit_price"],
                "pct_pnl": pnl_result["pct_pnl"],
                "exit_reason": pnl_result["exit_reason"],
            }
            all_trades.append(trade_record)

    # Print signal statistics
    print(f"\n[BACKTEST] Signal Statistics:")
    print(f"  Total signals: {signal_stats['total']}")
    print(f"  BUY_CE: {signal_stats['BUY_CE']}, BUY_PE: {signal_stats['BUY_PE']}, HOLD: {signal_stats['HOLD']}")
    if conf_values:
        print(f"  Confidence range: {min(conf_values):.3f} - {max(conf_values):.3f} (avg: {np.mean(conf_values):.3f})")
    if score_values:
        print(f"  Score range: {min(score_values):.3f} - {max(score_values):.3f} (avg: {np.mean(score_values):.3f})")
    print(
        f"  Signals passing filter (conf>={conf_thresh:.2f}, |score|>={score_thresh:.2f}): {signal_stats['passed_filter']}"
    )

    if not all_trades:
        print("\n[BACKTEST] No trades generated in backtest.")
        print(f"[BACKTEST] Pipeline is healthy; try profile='DEV' for more trades.")
        return

    # Build DataFrames
    df_trades_detailed = pd.DataFrame(all_trades)
    print(f"[BACKTEST] Generated {len(df_trades_detailed)} trades.")

    # Summary by underlying
    summary_rows = []
    for underlying in df_trades_detailed["underlying"].unique():
        df_u = df_trades_detailed[df_trades_detailed["underlying"] == underlying]
        trade_count = len(df_u)
        wins = (df_u["pct_pnl"] > 0).sum()
        win_rate = (wins / trade_count * 100.0) if trade_count > 0 else 0.0
        avg_pnl = df_u["pct_pnl"].mean()
        max_pnl = df_u["pct_pnl"].max()
        min_pnl = df_u["pct_pnl"].min()

        summary_rows.append(
            {
                "underlying": underlying,
                "trade_count": trade_count,
                "win_rate_pct": win_rate,
                "avg_pnl_pct": avg_pnl,
                "max_pnl_pct": max_pnl,
                "min_pnl_pct": min_pnl,
            }
        )

    df_summary = pd.DataFrame(summary_rows)

    # Save CSVs
    detailed_path = BACKTEST_DIR / "dhan_backtest_trades_detailed.csv"
    summary_path = BACKTEST_DIR / "dhan_backtest_summary.csv"

    df_trades_detailed.to_csv(detailed_path, index=False)
    df_summary.to_csv(summary_path, index=False)

    # Print summary
    print("\n=== Synthetic Backtest Summary ===")
    print(df_summary.to_string(index=False))
    print(f"\n[BACKTEST] Detailed trades: {detailed_path}")
    print(f"[BACKTEST] Summary: {summary_path}")


if __name__ == "__main__":
    print("=== ANGEL ONE INDEX OPTIONS - SYNTHETIC BACKTEST ===")
    # Default to DEV when run directly, so we see trades and PnL
    run_backtest(profile="DEV")
