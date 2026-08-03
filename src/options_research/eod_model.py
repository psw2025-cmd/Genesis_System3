"""Chronological incremental model and distinct-underlying costed evaluation."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import SGDClassifier, SGDRegressor
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from .eod_features import FEATURE_COLUMNS, file_trade_date


@dataclass(frozen=True)
class DateSplit:
    train_end: str
    validation_start: str
    validation_end: str
    test_start: str
    train_days: int
    validation_days: int
    test_days: int


def split_files(feature_root: Path, embargo_days: int = 1) -> tuple[list[Path], list[Path], list[Path], DateSplit]:
    files = sorted(feature_root.glob("**/*_features.parquet"), key=file_trade_date)
    dates = [file_trade_date(path) for path in files]
    if len(files) < 30:
        raise ValueError("at least 30 feature sessions required")
    train_end_idx = int(len(files) * 0.60) - 1
    validation_start_idx = train_end_idx + embargo_days + 1
    validation_end_idx = int(len(files) * 0.80) - 1
    test_start_idx = validation_end_idx + embargo_days + 1
    if validation_start_idx > validation_end_idx or test_start_idx >= len(files):
        raise ValueError("insufficient sessions after embargo")
    train = files[: train_end_idx + 1]
    valid = files[validation_start_idx : validation_end_idx + 1]
    test = files[test_start_idx:]
    split = DateSplit(
        str(dates[train_end_idx].date()), str(dates[validation_start_idx].date()),
        str(dates[validation_end_idx].date()), str(dates[test_start_idx].date()),
        len(train), len(valid), len(test),
    )
    return train, valid, test, split


def iter_batches(files: Iterable[Path]):
    for path in files:
        yield path, pd.read_parquet(path)


def train_incremental(train_files: list[Path], epochs: int = 2):
    scaler = StandardScaler()
    positive = negative = rows = 0
    for _, frame in iter_batches(train_files):
        x = frame[FEATURE_COLUMNS].astype(float).to_numpy()
        scaler.partial_fit(x)
        y = frame["target_positive"].astype(int).to_numpy()
        positive += int(y.sum())
        negative += int(len(y) - y.sum())
        rows += len(y)
    class_weight = {0: rows / max(2 * negative, 1), 1: rows / max(2 * positive, 1)}
    reg = SGDRegressor(
        loss="huber", penalty="elasticnet", alpha=1e-5, l1_ratio=0.05,
        learning_rate="adaptive", eta0=0.005, average=True, random_state=42,
    )
    clf = SGDClassifier(
        loss="log_loss", penalty="elasticnet", alpha=1e-5, l1_ratio=0.05,
        learning_rate="optimal", average=True, random_state=42,
    )
    classes = np.array([0, 1], dtype=int)
    initialized = False
    for _ in range(epochs):
        for _, frame in iter_batches(train_files):
            x = scaler.transform(frame[FEATURE_COLUMNS].astype(float).to_numpy())
            y_reg = frame["target_net_return"].clip(-0.99, 5.0).astype(float).to_numpy()
            y_cls = frame["target_positive"].astype(int).to_numpy()
            weights = np.where(y_cls == 1, class_weight[1], class_weight[0])
            reg.partial_fit(x, y_reg)
            if not initialized:
                clf.partial_fit(x, y_cls, classes=classes, sample_weight=weights)
                initialized = True
            else:
                clf.partial_fit(x, y_cls, sample_weight=weights)
    return scaler, reg, clf, {
        "train_rows": rows, "train_positive": positive, "train_negative": negative, "epochs": epochs,
    }


def max_drawdown(returns: list[float]) -> float:
    if not returns:
        return 0.0
    bounded = np.clip(np.asarray(returns, dtype=float), -0.999, 10.0)
    equity = np.cumprod(1 + bounded)
    peak = np.maximum.accumulate(equity)
    return float(np.max((peak - equity) / np.maximum(peak, 1e-12)))


def evaluate(files: list[Path], scaler, reg, clf, top_k: int, costs: list[float], row_sample_per_day: int = 2000) -> dict:
    returns_by_cost = {str(cost): [] for cost in costs}
    rho_values: list[float] = []
    overlap_values: list[float] = []
    row_truth: list[int] = []
    row_prob: list[float] = []
    total_rows = days = candidates = trades = base_wins = 0
    symbol_counts: Counter[str] = Counter()
    for _, frame in iter_batches(files):
        x = scaler.transform(frame[FEATURE_COLUMNS].astype(float).to_numpy())
        frame = frame.copy()
        frame["prediction"] = reg.predict(x)
        frame["probability"] = clf.predict_proba(x)[:, 1]
        total_rows += len(frame)
        stride = max(1, len(frame) // max(row_sample_per_day, 1))
        sampled = frame.iloc[::stride].head(row_sample_per_day)
        row_truth.extend(sampled["target_positive"].astype(int).tolist())
        row_prob.extend(sampled["probability"].astype(float).tolist())
        predicted = frame.sort_values(["symbol", "prediction"], ascending=[True, False]).groupby("symbol", observed=True).head(1)
        actual = frame.sort_values(["symbol", "gross_return"], ascending=[True, False]).groupby("symbol", observed=True).head(1)
        selected = predicted.nlargest(min(top_k, len(predicted)), "prediction")
        actual_top = actual.nlargest(min(top_k, len(actual)), "gross_return")
        days += 1
        candidates += len(predicted)
        trades += len(selected)
        base_wins += int((selected["target_net_return"] > 0).sum())
        symbol_counts.update(selected["symbol"].astype(str))
        overlap_values.append(len(set(selected["symbol"]) & set(actual_top["symbol"])) / max(len(actual_top), 1))
        actual_map = actual.set_index("symbol")["gross_return"]
        aligned = predicted[["symbol", "prediction"]].copy()
        aligned["actual_best"] = aligned["symbol"].map(actual_map)
        if aligned["prediction"].nunique() > 1 and aligned["actual_best"].nunique() > 1:
            rho = spearmanr(aligned["prediction"], aligned["actual_best"], nan_policy="omit").statistic
            if not np.isnan(rho):
                rho_values.append(float(rho))
        for cost in costs:
            returns_by_cost[str(cost)].extend((selected["gross_return"] - cost / 10000.0).astype(float).tolist())
    stress = {}
    for cost, values in returns_by_cost.items():
        arr = np.asarray(values, dtype=float)
        positive = arr[arr > 0]
        negative = arr[arr <= 0]
        stress[cost] = {
            "trades": len(values),
            "win_rate": float((arr > 0).mean()) if len(arr) else 0.0,
            "mean_net_return": float(arr.mean()) if len(arr) else 0.0,
            "net_return_sum": float(arr.sum()),
            "profit_factor": float(positive.sum() / abs(negative.sum())) if negative.sum() < 0 else None,
            "max_drawdown": max_drawdown(values),
        }
    auc = roc_auc_score(row_truth, row_prob) if len(set(row_truth)) > 1 else None
    brier = float(np.mean((np.asarray(row_prob) - np.asarray(row_truth)) ** 2)) if row_truth else None
    return {
        "days": days,
        "rows_scored": total_rows,
        "row_metric_sample": len(row_truth),
        "candidate_underlying_days": candidates,
        "trades": trades,
        "base_cost_wins": base_wins,
        "distinct_traded_symbols": len(symbol_counts),
        "top_traded_symbols": dict(symbol_counts.most_common(30)),
        "median_daily_spearman": float(np.median(rho_values)) if rho_values else None,
        "mean_top_k_overlap": float(np.mean(overlap_values)) if overlap_values else None,
        "row_roc_auc": auc,
        "row_brier": brier,
        "cost_stress": stress,
    }
