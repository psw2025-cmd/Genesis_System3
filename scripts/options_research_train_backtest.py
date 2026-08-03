#!/usr/bin/env python3
"""Leakage-controlled options model training and costed ranked backtest.

Research only: no order endpoints, no model promotion, no live configuration changes.
Features are timestamped at t; targets use a strictly later observation at t+horizon.
The final holdout is chronological and is evaluated once by this run.
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import accuracy_score, brier_score_loss, mean_absolute_error, roc_auc_score
from sklearn.utils.class_weight import compute_sample_weight

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = Path(os.getenv("SYSTEM3_RESEARCH_DATA_ROOT", ROOT / "storage" / "research_options"))
DEFAULT_REPORT_DIR = ROOT / "reports" / "latest" / "options_bigdata_research"
FEATURE_COLUMNS = [
    "ret_1", "ret_5", "ret_15", "rv_15", "volume_z_30", "oi_change_1", "iv_change_1",
    "moneyness_pct", "expiry_code", "is_weekly", "strike_offset_num", "option_is_call",
    "instrument_is_index", "exchange_is_bse", "minute_of_day_sin", "minute_of_day_cos",
]
TRUTHY = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Split:
    train_end: pd.Timestamp
    validation_start: pd.Timestamp
    validation_end: pd.Timestamp
    test_start: pd.Timestamp


def ensure_analyzer_only() -> None:
    for name in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED"):
        if str(os.getenv(name, "0")).strip().lower() in TRUTHY:
            raise RuntimeError(f"{name} must remain disabled")


def read_partitions(data_root: Path, max_files: int | None = None) -> pd.DataFrame:
    files = sorted(data_root.glob("dhan_rolling/**/*.parquet"))
    csv_files = sorted(data_root.glob("dhan_rolling/**/*.csv.gz"))
    selected = (files + csv_files)[:max_files] if max_files else files + csv_files
    frames: list[pd.DataFrame] = []
    for path in selected:
        frame = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, compression="gzip")
        frame["source_file"] = str(path)
        frames.append(frame)
    if not frames:
        raise FileNotFoundError(f"no Dhan rolling partitions under {data_root}")
    return pd.concat(frames, ignore_index=True)


def _strike_offset_number(value: object) -> float:
    text = str(value or "ATM").upper().strip()
    if text == "ATM":
        return 0.0
    try:
        if "+" in text:
            return float(text.rsplit("+", 1)[1])
        if "-" in text:
            return -float(text.rsplit("-", 1)[1])
    except ValueError:
        return np.nan
    return np.nan


def build_features(raw: pd.DataFrame, horizon_bars: int = 30, round_trip_cost_bps: float = 40.0) -> pd.DataFrame:
    required = {"timestamp", "underlying", "option_type", "close", "volume", "oi", "iv", "strike", "spot"}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    if horizon_bars <= 0:
        raise ValueError("horizon_bars must be positive")

    df = raw.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True, errors="coerce").dt.tz_convert("Asia/Kolkata")
    numeric = ["open", "high", "low", "close", "volume", "oi", "iv", "strike", "spot", "expiry_code"]
    for col in numeric:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["expiry_code"] = df.get("expiry_code", 0).fillna(0).astype(float)
    df["expiry_flag"] = df.get("expiry_flag", "MONTH").fillna("MONTH").astype(str).str.upper()
    df["strike_offset"] = df.get("strike_offset", "ATM").fillna("ATM").astype(str)
    df["instrument"] = df.get("instrument", "OPTSTK").fillna("OPTSTK").astype(str).str.upper()
    df["exchange_segment"] = df.get("exchange_segment", "NSE_FNO").fillna("NSE_FNO").astype(str).str.upper()
    df["security_id"] = df.get("security_id", "").fillna("").astype(str)
    df["option_type"] = df["option_type"].astype(str).str.upper()

    group_cols = [
        "exchange_segment", "security_id", "underlying", "instrument", "option_type",
        "expiry_flag", "expiry_code", "strike_offset",
    ]
    df = df.sort_values(group_cols + ["timestamp"]).drop_duplicates(group_cols + ["timestamp"], keep="last")
    grouped = df.groupby(group_cols, sort=False, observed=True)

    df["ret_1"] = grouped["close"].pct_change(1, fill_method=None)
    df["ret_5"] = grouped["close"].pct_change(5, fill_method=None)
    df["ret_15"] = grouped["close"].pct_change(15, fill_method=None)
    df["rv_15"] = grouped["ret_1"].transform(lambda s: s.rolling(15, min_periods=10).std())
    df["volume_z_30"] = grouped["volume"].transform(
        lambda s: (s - s.rolling(30, min_periods=15).mean()) / s.rolling(30, min_periods=15).std().replace(0, np.nan)
    )
    df["oi_change_1"] = grouped["oi"].pct_change(1, fill_method=None)
    df["iv_change_1"] = grouped["iv"].pct_change(1, fill_method=None)
    df["moneyness_pct"] = np.where(
        df["option_type"].isin(["CALL", "CE"]),
        (df["spot"] - df["strike"]) / df["spot"].replace(0, np.nan),
        (df["strike"] - df["spot"]) / df["spot"].replace(0, np.nan),
    )
    df["is_weekly"] = (df["expiry_flag"] == "WEEK").astype(int)
    df["strike_offset_num"] = df["strike_offset"].map(_strike_offset_number)
    df["option_is_call"] = df["option_type"].isin(["CALL", "CE"]).astype(int)
    df["instrument_is_index"] = (df["instrument"] == "OPTIDX").astype(int)
    df["exchange_is_bse"] = (df["exchange_segment"] == "BSE_FNO").astype(int)
    minute = df["timestamp"].dt.hour * 60 + df["timestamp"].dt.minute
    df["minute_of_day_sin"] = np.sin(2 * np.pi * minute / 1440)
    df["minute_of_day_cos"] = np.cos(2 * np.pi * minute / 1440)

    df["target_timestamp"] = grouped["timestamp"].shift(-horizon_bars)
    future_close = grouped["close"].shift(-horizon_bars)
    gross_return = future_close / df["close"] - 1.0
    cost = round_trip_cost_bps / 10_000.0
    df["target_net_return"] = gross_return - cost
    df["target_positive"] = (df["target_net_return"] > 0).astype(int)
    df = df.replace([np.inf, -np.inf], np.nan).dropna(
        subset=FEATURE_COLUMNS + ["timestamp", "target_timestamp", "target_net_return"]
    )
    return df


def chronological_split(
    df: pd.DataFrame,
    train_fraction: float = 0.60,
    validation_fraction: float = 0.20,
    embargo_days: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Split]:
    dates = np.array(sorted(pd.unique(df["timestamp"].dt.floor("D"))))
    if len(dates) < 10:
        raise ValueError("at least 10 distinct trading days required")
    if embargo_days < 0:
        raise ValueError("embargo_days must be non-negative")

    train_end_idx = max(0, int(len(dates) * train_fraction) - 1)
    validation_end_idx = max(train_end_idx + embargo_days + 1, int(len(dates) * (train_fraction + validation_fraction)) - 1)
    validation_end_idx = min(validation_end_idx, len(dates) - embargo_days - 2)
    validation_start_idx = train_end_idx + embargo_days + 1
    test_start_idx = validation_end_idx + embargo_days + 1
    if validation_start_idx > validation_end_idx or test_start_idx >= len(dates):
        raise ValueError("not enough dates after embargo")

    train_end = pd.Timestamp(dates[train_end_idx])
    validation_start = pd.Timestamp(dates[validation_start_idx])
    validation_end = pd.Timestamp(dates[validation_end_idx])
    test_start = pd.Timestamp(dates[test_start_idx])
    feature_day = df["timestamp"].dt.floor("D")
    label_day = df["target_timestamp"].dt.floor("D")

    train = df[(feature_day <= train_end) & (label_day <= train_end)].copy()
    validation = df[
        (feature_day >= validation_start) & (feature_day <= validation_end) & (label_day <= validation_end)
    ].copy()
    test = df[feature_day >= test_start].copy()
    if min(len(train), len(validation), len(test)) == 0:
        raise ValueError("chronological split empty after label-boundary purge and embargo")
    if train["target_timestamp"].max().floor("D") > train_end:
        raise AssertionError("training label crossed train boundary")
    if validation["target_timestamp"].max().floor("D") > validation_end:
        raise AssertionError("validation label crossed validation boundary")
    return train, validation, test, Split(train_end, validation_start, validation_end, test_start)


def max_drawdown(returns: Iterable[float]) -> float:
    equity = np.cumprod(1 + np.asarray(list(returns), dtype=float))
    if equity.size == 0:
        return 0.0
    peak = np.maximum.accumulate(equity)
    return float(np.max((peak - equity) / np.where(peak == 0, 1, peak)))


def _decision_snapshot(scored: pd.DataFrame, decision_time: str) -> pd.DataFrame:
    try:
        hour, minute = [int(value) for value in decision_time.split(":", 1)]
    except Exception as exc:
        raise ValueError("decision_time must use HH:MM") from exc
    cutoff_minutes = hour * 60 + minute
    scored = scored.copy()
    scored["day"] = scored["timestamp"].dt.floor("D")
    scored["minute"] = scored["timestamp"].dt.hour * 60 + scored["timestamp"].dt.minute
    eligible = scored[scored["minute"] <= cutoff_minutes].copy()
    if eligible.empty:
        raise ValueError(f"no rows at or before decision time {decision_time}")
    contract_cols = [
        "day", "exchange_segment", "underlying", "instrument", "option_type",
        "expiry_flag", "expiry_code", "strike_offset",
    ]
    latest_contract = eligible.sort_values("timestamp").groupby(contract_cols, observed=True).tail(1)
    one_contract_per_underlying = (
        latest_contract.sort_values(["day", "underlying", "prediction"], ascending=[True, True, False])
        .groupby(["day", "exchange_segment", "underlying"], observed=True)
        .head(1)
    )
    return one_contract_per_underlying


def evaluate_ranked(
    test: pd.DataFrame,
    predictions: np.ndarray,
    probabilities: np.ndarray,
    top_k: int = 3,
    decision_time: str = "10:00",
) -> dict:
    keep = [
        "timestamp", "target_timestamp", "exchange_segment", "underlying", "instrument", "option_type",
        "expiry_flag", "expiry_code", "strike_offset", "target_net_return",
    ]
    scored = test[keep].copy()
    scored["prediction"] = predictions
    scored["probability"] = probabilities
    snapshot = _decision_snapshot(scored, decision_time)
    selected = snapshot.sort_values(["day", "prediction"], ascending=[True, False]).groupby("day", observed=True).head(top_k)
    actual_top = snapshot.sort_values(["day", "target_net_return"], ascending=[True, False]).groupby("day", observed=True).head(top_k)

    overlaps: list[float] = []
    daily_rho: list[float] = []
    for day, group in snapshot.groupby("day", observed=True):
        selected_symbols = set(selected.loc[selected["day"] == day, "underlying"])
        actual_symbols = set(actual_top.loc[actual_top["day"] == day, "underlying"])
        overlaps.append(len(selected_symbols & actual_symbols) / max(min(top_k, len(actual_symbols)), 1))
        if group["prediction"].nunique() > 1 and group["target_net_return"].nunique() > 1:
            rho = spearmanr(group["prediction"], group["target_net_return"], nan_policy="omit").statistic
            if not np.isnan(rho):
                daily_rho.append(float(rho))

    returns = selected["target_net_return"].to_numpy(dtype=float)
    wins = returns[returns > 0]
    losses = returns[returns <= 0]
    profit_factor = float(wins.sum() / abs(losses.sum())) if losses.sum() < 0 else None
    symbol_counts = selected["underlying"].value_counts().to_dict()
    return {
        "decision_time_ist": decision_time,
        "candidate_underlyings": int(snapshot["underlying"].nunique()),
        "test_days": int(snapshot["day"].nunique()),
        "trades": int(len(selected)),
        "unique_traded_underlyings": int(selected["underlying"].nunique()),
        "trades_by_underlying": {str(k): int(v) for k, v in symbol_counts.items()},
        "winning_trades": int((returns > 0).sum()),
        "win_rate": float((returns > 0).mean()) if len(returns) else 0.0,
        "net_return_sum": float(returns.sum()),
        "mean_net_return": float(returns.mean()) if len(returns) else 0.0,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown(returns),
        "median_daily_spearman": float(np.median(daily_rho)) if daily_rho else None,
        "mean_top_k_overlap": float(np.mean(overlaps)) if overlaps else None,
    }


def train_and_backtest(
    features: pd.DataFrame,
    output_dir: Path,
    top_k: int = 3,
    decision_time: str = "10:00",
    embargo_days: int = 1,
) -> dict:
    train, validation, test, split = chronological_split(features, embargo_days=embargo_days)
    x_train, y_train = train[FEATURE_COLUMNS], train["target_net_return"]
    x_valid, y_valid = validation[FEATURE_COLUMNS], validation["target_net_return"]
    x_test, y_test = test[FEATURE_COLUMNS], test["target_net_return"]
    reg = HistGradientBoostingRegressor(
        max_iter=250, learning_rate=0.05, max_leaf_nodes=31, l2_regularization=1.0, random_state=42
    )
    clf = HistGradientBoostingClassifier(
        max_iter=250, learning_rate=0.05, max_leaf_nodes=31, l2_regularization=1.0, random_state=42
    )
    reg.fit(x_train, y_train)
    sample_weight = compute_sample_weight(class_weight="balanced", y=train["target_positive"])
    clf.fit(x_train, train["target_positive"], sample_weight=sample_weight)
    valid_pred = reg.predict(x_valid)
    test_pred = reg.predict(x_test)
    test_prob = clf.predict_proba(x_test)[:, 1]
    test_class = (test_prob >= 0.5).astype(int)
    metrics = {
        "feature_columns": FEATURE_COLUMNS,
        "rows": int(len(features)),
        "distinct_days": int(features["timestamp"].dt.floor("D").nunique()),
        "train_rows": int(len(train)),
        "validation_rows": int(len(validation)),
        "test_rows": int(len(test)),
        "train_end": split.train_end.isoformat(),
        "validation_start": split.validation_start.isoformat(),
        "validation_end": split.validation_end.isoformat(),
        "test_start": split.test_start.isoformat(),
        "embargo_days": embargo_days,
        "validation_mae": float(mean_absolute_error(y_valid, valid_pred)),
        "test_mae": float(mean_absolute_error(y_test, test_pred)),
        "test_direction_accuracy": float(accuracy_score(test["target_positive"], test_class)),
        "test_brier": float(brier_score_loss(test["target_positive"], test_prob)),
        "test_roc_auc": float(roc_auc_score(test["target_positive"], test_prob)) if test["target_positive"].nunique() > 1 else None,
        "ranked_backtest": evaluate_ranked(test, test_pred, test_prob, top_k, decision_time),
        "promotion_allowed": False,
        "live_trading_enabled": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump({"regressor": reg, "classifier": clf, "features": FEATURE_COLUMNS}, output_dir / "research_model.joblib")
    (output_dir / "training_metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--horizon-bars", type=int, default=30)
    parser.add_argument("--cost-bps", type=float, default=40.0)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--decision-time", default="10:00")
    parser.add_argument("--embargo-days", type=int, default=1)
    parser.add_argument("--max-files", type=int, default=None)
    args = parser.parse_args()
    ensure_analyzer_only()
    try:
        raw = read_partitions(args.data_root, args.max_files)
        features = build_features(raw, args.horizon_bars, args.cost_bps)
        metrics = train_and_backtest(features, args.report_dir, args.top_k, args.decision_time, args.embargo_days)
        status = "PASS" if metrics["ranked_backtest"]["trades"] > 0 else "FAIL"
        summary = {
            "status": status,
            **metrics,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "order_placement_allowed": False,
        }
        (args.report_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2))
        return 0 if status == "PASS" else 2
    except Exception as exc:
        args.report_dir.mkdir(parents=True, exist_ok=True)
        summary = {
            "status": "BLOCKED",
            "reason": f"{type(exc).__name__}: {exc}",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "promotion_allowed": False,
        }
        (args.report_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
