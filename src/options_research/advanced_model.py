"""Advanced chronological ensemble, frozen holdout and normalized paper ledger.

The implementation deliberately combines:
- an incremental SGD baseline trained on every valid pre-test feature row;
- a tuned LightGBM challenger trained on a deterministic sample spanning every
  training session;
- validation-only selection of ensemble weight, top-k and probability filter;
- one final frozen holdout evaluation under multiple transaction-cost stresses.

No function in this module places orders or enables live trading.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

from .eod_features import FEATURE_COLUMNS, file_trade_date
from .eod_model import train_incremental


@dataclass(frozen=True)
class SelectionConfig:
    lightgbm_weight: float
    top_k: int
    min_probability: float


@dataclass
class MetricAccumulator:
    trade_returns: dict[float, list[float]]
    daily_returns: dict[float, list[float]]
    rho: list[float]
    overlap: list[float]
    row_truth: list[int]
    row_probability: list[float]
    trades: list[dict]
    days: int = 0
    rows_scored: int = 0
    candidate_underlying_days: int = 0


def new_accumulator(costs: Iterable[float]) -> MetricAccumulator:
    return MetricAccumulator(
        trade_returns={float(cost): [] for cost in costs},
        daily_returns={float(cost): [] for cost in costs},
        rho=[], overlap=[], row_truth=[], row_probability=[], trades=[],
    )


def read_feature(path: Path) -> pd.DataFrame:
    columns = [
        "symbol", "expiry", "strike", "option_type", "instrument", "trade_date",
        *FEATURE_COLUMNS, "gross_return", "target_net_return", "target_positive",
        "close", "volume", "oi",
    ]
    return pd.read_parquet(path, columns=columns)


def deterministic_sample(files: list[Path], max_rows: int, seed: int = 42) -> pd.DataFrame:
    """Sample every session, retaining both liquid and broad-market rows."""
    if not files:
        raise ValueError("feature files are required")
    per_day = max(100, math.ceil(max_rows / len(files)))
    frames: list[pd.DataFrame] = []
    for index, path in enumerate(files):
        frame = read_feature(path)
        if frame.empty:
            continue
        take = min(per_day, len(frame))
        liquid_take = min(max(1, take // 2), len(frame))
        liquid = frame.nlargest(liquid_take, ["volume", "oi"])
        remaining = frame.drop(index=liquid.index)
        random_take = min(take - len(liquid), len(remaining))
        random_rows = remaining.sample(n=random_take, random_state=seed + index) if random_take else remaining.iloc[:0]
        frames.append(pd.concat([liquid, random_rows], ignore_index=True))
    if not frames:
        raise ValueError("no sampled feature rows")
    result = pd.concat(frames, ignore_index=True)
    if len(result) > max_rows:
        result = result.sample(n=max_rows, random_state=seed).sort_values("trade_date")
    return result.reset_index(drop=True)


def train_lightgbm_challenger(
    train_files: list[Path],
    valid_files: list[Path],
    max_train_rows: int = 1_200_000,
    max_valid_rows: int = 250_000,
    trials: int = 12,
    seed: int = 42,
):
    import lightgbm as lgb
    import optuna

    train = deterministic_sample(train_files, max_train_rows, seed)
    valid = deterministic_sample(valid_files, max_valid_rows, seed + 1000)
    x_train = train[FEATURE_COLUMNS].astype(np.float32)
    y_train = train["target_net_return"].clip(-0.99, 5.0).astype(np.float32)
    x_valid = valid[FEATURE_COLUMNS].astype(np.float32)
    y_valid = valid["target_net_return"].clip(-0.99, 5.0).astype(np.float32)

    def objective(trial: optuna.Trial) -> float:
        model = lgb.LGBMRegressor(
            objective="huber",
            n_estimators=600,
            learning_rate=trial.suggest_float("learning_rate", 0.015, 0.12, log=True),
            num_leaves=trial.suggest_int("num_leaves", 15, 127),
            max_depth=trial.suggest_int("max_depth", 4, 12),
            min_child_samples=trial.suggest_int("min_child_samples", 50, 1000, log=True),
            subsample=trial.suggest_float("subsample", 0.65, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.60, 1.0),
            reg_alpha=trial.suggest_float("reg_alpha", 1e-6, 5.0, log=True),
            reg_lambda=trial.suggest_float("reg_lambda", 1e-6, 10.0, log=True),
            random_state=seed,
            n_jobs=-1,
            verbosity=-1,
        )
        model.fit(
            x_train, y_train,
            eval_set=[(x_valid, y_valid)],
            eval_metric="l1",
            callbacks=[lgb.early_stopping(40, verbose=False)],
        )
        prediction = model.predict(x_valid)
        rho = spearmanr(prediction, y_valid, nan_policy="omit").statistic
        mae = float(np.mean(np.abs(prediction - y_valid)))
        return (float(rho) if not np.isnan(rho) else -1.0) - 0.02 * mae

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=seed),
    )
    study.optimize(objective, n_trials=max(1, trials), show_progress_bar=False)
    best = dict(study.best_params)
    model = lgb.LGBMRegressor(
        objective="huber",
        n_estimators=900,
        random_state=seed,
        n_jobs=-1,
        verbosity=-1,
        **best,
    )
    model.fit(
        x_train, y_train,
        eval_set=[(x_valid, y_valid)],
        eval_metric="l1",
        callbacks=[lgb.early_stopping(60, verbose=False)],
    )
    return model, {
        "model": "LightGBMRegressor",
        "train_sample_rows": int(len(train)),
        "validation_sample_rows": int(len(valid)),
        "training_sessions": len(train_files),
        "validation_sessions": len(valid_files),
        "optuna_trials": len(study.trials),
        "best_objective": float(study.best_value),
        "best_params": best,
        "best_iteration": int(getattr(model, "best_iteration_", 0) or 0),
    }


def score_frame(frame: pd.DataFrame, scaler, regressor, classifier, challenger=None) -> pd.DataFrame:
    x = frame[FEATURE_COLUMNS].astype(float).to_numpy()
    scaled = scaler.transform(x)
    baseline = regressor.predict(scaled)
    probability = classifier.predict_proba(scaled)[:, 1]
    scored = frame.copy()
    scored["baseline_prediction"] = baseline
    scored["probability"] = probability
    scored["baseline_rank"] = pd.Series(baseline, index=scored.index).rank(pct=True, method="average")
    if challenger is not None:
        challenger_prediction = challenger.predict(frame[FEATURE_COLUMNS].astype(np.float32))
        scored["challenger_prediction"] = challenger_prediction
        scored["challenger_rank"] = pd.Series(challenger_prediction, index=scored.index).rank(pct=True, method="average")
    else:
        scored["challenger_prediction"] = baseline
        scored["challenger_rank"] = scored["baseline_rank"]
    return scored


def selected_rows(scored: pd.DataFrame, config: SelectionConfig) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    weight = float(config.lightgbm_weight)
    scored = scored.copy()
    scored["ensemble_score"] = (1.0 - weight) * scored["baseline_rank"] + weight * scored["challenger_rank"]
    eligible = scored[scored["probability"] >= config.min_probability]
    if eligible.empty:
        return eligible, eligible, eligible
    predicted = (
        eligible.sort_values(["symbol", "ensemble_score"], ascending=[True, False])
        .groupby("symbol", observed=True).head(1)
    )
    selected = predicted.nlargest(min(config.top_k, len(predicted)), "ensemble_score")
    actual = (
        scored.sort_values(["symbol", "gross_return"], ascending=[True, False])
        .groupby("symbol", observed=True).head(1)
    )
    return selected, predicted, actual


def update_accumulator(
    accumulator: MetricAccumulator,
    scored: pd.DataFrame,
    config: SelectionConfig,
    costs: Iterable[float],
    row_sample_per_day: int = 1500,
) -> None:
    selected, predicted, actual = selected_rows(scored, config)
    accumulator.days += 1
    accumulator.rows_scored += len(scored)
    accumulator.candidate_underlying_days += len(predicted)
    stride = max(1, len(scored) // max(1, row_sample_per_day))
    sampled = scored.iloc[::stride].head(row_sample_per_day)
    accumulator.row_truth.extend(sampled["target_positive"].astype(int).tolist())
    accumulator.row_probability.extend(sampled["probability"].astype(float).tolist())

    actual_top = actual.nlargest(min(config.top_k, len(actual)), "gross_return")
    if not actual_top.empty:
        accumulator.overlap.append(
            len(set(selected["symbol"]) & set(actual_top["symbol"])) / max(len(actual_top), 1)
        )
    actual_map = actual.set_index("symbol")["gross_return"] if not actual.empty else pd.Series(dtype=float)
    aligned = predicted[["symbol", "ensemble_score"]].copy() if not predicted.empty else predicted
    if not aligned.empty:
        aligned["actual_best"] = aligned["symbol"].map(actual_map)
        if aligned["ensemble_score"].nunique() > 1 and aligned["actual_best"].nunique() > 1:
            rho = spearmanr(aligned["ensemble_score"], aligned["actual_best"], nan_policy="omit").statistic
            if not np.isnan(rho):
                accumulator.rho.append(float(rho))

    trade_date = str(pd.Timestamp(scored["trade_date"].iloc[0]).date()) if not scored.empty else ""
    for cost in costs:
        net = (selected["gross_return"] - float(cost) / 10000.0).astype(float).tolist()
        accumulator.trade_returns[float(cost)].extend(net)
        accumulator.daily_returns[float(cost)].append(float(np.mean(net)) if net else 0.0)
    for row in selected.itertuples(index=False):
        accumulator.trades.append({
            "trade_date": trade_date,
            "symbol": str(row.symbol),
            "expiry": str(pd.Timestamp(row.expiry).date()),
            "strike": float(row.strike),
            "option_type": str(row.option_type),
            "close": float(row.close),
            "gross_return": float(row.gross_return),
            "probability": float(row.probability),
            "ensemble_score": float(row.ensemble_score),
        })


def max_drawdown(daily_returns: list[float]) -> float:
    if not daily_returns:
        return 0.0
    bounded = np.clip(np.asarray(daily_returns, dtype=float), -0.95, 2.0)
    equity = np.cumprod(1.0 + bounded)
    peak = np.maximum.accumulate(equity)
    return float(np.max((peak - equity) / np.maximum(peak, 1e-12)))


def consecutive_losses(values: list[float]) -> int:
    longest = current = 0
    for value in values:
        if value <= 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def metric_summary(trades: list[float], daily: list[float]) -> dict:
    trade_array = np.asarray(trades, dtype=float)
    daily_array = np.asarray(daily, dtype=float)
    positive = trade_array[trade_array > 0]
    negative = trade_array[trade_array <= 0]
    bounded_daily = np.clip(daily_array, -0.95, 2.0)
    equity_total = float(np.prod(1.0 + bounded_daily) - 1.0) if len(bounded_daily) else 0.0
    years = len(bounded_daily) / 252.0
    cagr = float((1.0 + equity_total) ** (1.0 / years) - 1.0) if years > 0 and equity_total > -1 else None
    mean_daily = float(daily_array.mean()) if len(daily_array) else 0.0
    std_daily = float(daily_array.std(ddof=1)) if len(daily_array) > 1 else 0.0
    downside = daily_array[daily_array < 0]
    downside_std = float(downside.std(ddof=1)) if len(downside) > 1 else 0.0
    sharpe = mean_daily / std_daily * math.sqrt(252) if std_daily > 0 else None
    sortino = mean_daily / downside_std * math.sqrt(252) if downside_std > 0 else None
    drawdown = max_drawdown(daily)
    var95 = float(np.quantile(daily_array, 0.05)) if len(daily_array) else None
    cvar95 = float(daily_array[daily_array <= var95].mean()) if len(daily_array) and var95 is not None else None
    return {
        "trades": int(len(trade_array)),
        "winners": int((trade_array > 0).sum()),
        "losers": int((trade_array <= 0).sum()),
        "win_rate": float((trade_array > 0).mean()) if len(trade_array) else 0.0,
        "mean_trade_return": float(trade_array.mean()) if len(trade_array) else 0.0,
        "median_trade_return": float(np.median(trade_array)) if len(trade_array) else 0.0,
        "net_return_sum": float(trade_array.sum()) if len(trade_array) else 0.0,
        "average_win": float(positive.mean()) if len(positive) else 0.0,
        "average_loss": float(negative.mean()) if len(negative) else 0.0,
        "profit_factor": float(positive.sum() / abs(negative.sum())) if negative.sum() < 0 else None,
        "daily_observations": int(len(daily_array)),
        "mean_daily_return": mean_daily,
        "annualized_sharpe": sharpe,
        "annualized_sortino": sortino,
        "max_drawdown": drawdown,
        "calmar": float(cagr / drawdown) if cagr is not None and drawdown > 0 else None,
        "compounded_total_return": equity_total,
        "cagr": cagr,
        "daily_var_95": var95,
        "daily_cvar_95": cvar95,
        "max_consecutive_losing_trades": consecutive_losses(trades),
    }


def finalize(accumulator: MetricAccumulator, costs: Iterable[float]) -> dict:
    cost_metrics = {
        str(float(cost)): metric_summary(
            accumulator.trade_returns[float(cost)], accumulator.daily_returns[float(cost)]
        ) for cost in costs
    }
    auc = roc_auc_score(accumulator.row_truth, accumulator.row_probability) if len(set(accumulator.row_truth)) > 1 else None
    brier = (
        float(np.mean((np.asarray(accumulator.row_probability) - np.asarray(accumulator.row_truth)) ** 2))
        if accumulator.row_truth else None
    )
    return {
        "days": accumulator.days,
        "rows_scored": accumulator.rows_scored,
        "candidate_underlying_days": accumulator.candidate_underlying_days,
        "trades": len(accumulator.trades),
        "median_daily_spearman": float(np.median(accumulator.rho)) if accumulator.rho else None,
        "mean_top_k_overlap": float(np.mean(accumulator.overlap)) if accumulator.overlap else None,
        "row_metric_sample": len(accumulator.row_truth),
        "row_roc_auc": float(auc) if auc is not None else None,
        "row_brier": brier,
        "cost_stress": cost_metrics,
    }


def evaluate_files(files, scaler, regressor, classifier, challenger, config, costs) -> tuple[dict, pd.DataFrame]:
    accumulator = new_accumulator(costs)
    for path in files:
        frame = read_feature(path)
        if frame.empty:
            continue
        scored = score_frame(frame, scaler, regressor, classifier, challenger)
        update_accumulator(accumulator, scored, config, costs)
    return finalize(accumulator, costs), pd.DataFrame(accumulator.trades)


def validation_search(files, scaler, regressor, classifier, challenger, costs=(80.0,)) -> tuple[SelectionConfig, list[dict]]:
    configs = [
        SelectionConfig(weight, top_k, probability)
        for weight in ((0.0, 0.5, 1.0) if challenger is not None else (0.0,))
        for top_k in (1, 3, 5)
        for probability in (0.50, 0.55, 0.60)
    ]
    accumulators = {config: new_accumulator(costs) for config in configs}
    for path in files:
        frame = read_feature(path)
        if frame.empty:
            continue
        scored = score_frame(frame, scaler, regressor, classifier, challenger)
        for config in configs:
            update_accumulator(accumulators[config], scored, config, costs)
    rows = []
    for config in configs:
        result = finalize(accumulators[config], costs)
        metric = result["cost_stress"][str(float(list(costs)[0]))]
        spearman = result.get("median_daily_spearman") or 0.0
        sharpe = metric.get("annualized_sharpe") or 0.0
        composite = (
            100.0 * metric["mean_daily_return"]
            + 0.30 * spearman
            + 0.03 * sharpe
            - 0.50 * metric["max_drawdown"]
        )
        rows.append({
            "lightgbm_weight": config.lightgbm_weight,
            "top_k": config.top_k,
            "min_probability": config.min_probability,
            "composite": float(composite),
            "metrics": result,
        })
    rows.sort(key=lambda row: row["composite"], reverse=True)
    best = rows[0]
    return SelectionConfig(
        float(best["lightgbm_weight"]), int(best["top_k"]), float(best["min_probability"])
    ), rows


def normalized_paper_ledger(trades: pd.DataFrame, cost_bps: float, initial_capital_inr: float) -> tuple[pd.DataFrame, dict]:
    if trades.empty:
        return pd.DataFrame(), {
            "initial_capital_inr": initial_capital_inr,
            "ending_capital_inr": initial_capital_inr,
            "net_pnl_inr": 0.0,
            "days": 0,
            "trades": 0,
        }
    frame = trades.copy()
    frame["net_return"] = frame["gross_return"] - cost_bps / 10000.0
    daily = frame.groupby("trade_date", sort=True)["net_return"].mean().clip(-0.95, 2.0)
    capital = float(initial_capital_inr)
    rows = []
    for trade_date, daily_return in daily.items():
        start = capital
        pnl = start * float(daily_return)
        capital = start + pnl
        rows.append({
            "trade_date": trade_date,
            "start_capital_inr": start,
            "daily_net_return": float(daily_return),
            "pnl_inr": pnl,
            "end_capital_inr": capital,
            "selected_trades": int((frame["trade_date"] == trade_date).sum()),
        })
    ledger = pd.DataFrame(rows)
    proof = {
        "status": "NORMALIZED_NOTIONAL_SIMULATION",
        "initial_capital_inr": float(initial_capital_inr),
        "ending_capital_inr": float(capital),
        "net_pnl_inr": float(capital - initial_capital_inr),
        "days": int(len(ledger)),
        "trades": int(len(frame)),
        "cost_bps": float(cost_bps),
        "historical_lot_sizes_used": False,
        "broker_fills_used": False,
        "live_trading_enabled": False,
    }
    return ledger, proof
