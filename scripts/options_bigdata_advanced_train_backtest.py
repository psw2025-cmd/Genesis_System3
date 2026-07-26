#!/usr/bin/env python3
"""Train advanced analyzer-only models on the complete NSE F&O archive.

The pipeline uses chronological train/validation/frozen-test partitions,
next-session-open execution targets, conservative stop-before-target ordering,
explicit no-fill outcomes, transaction-cost stress and capped portfolio
exposure. Live trading and order placement remain disabled.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.options_research.advanced_model import (
    MAX_DAILY_EXPOSURE,
    PER_TRADE_ALLOCATION,
    SelectionConfig,
    deterministic_sample,
    evaluate_files,
    normalized_paper_ledger,
    train_lightgbm_challenger,
    validation_search,
)
from src.options_research.eod_features import FEATURE_COLUMNS, generate_features
from src.options_research.eod_model import split_files, train_incremental

TRUTHY = {"1", "true", "yes", "on"}


def ensure_analyzer_only() -> None:
    enabled = [
        name for name in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED")
        if str(os.getenv(name, "0")).strip().lower() in TRUTHY
    ]
    if enabled:
        raise RuntimeError(f"live flags must remain disabled: {enabled}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fit_final_lightgbm(files: list[Path], best_params: dict, max_rows: int, seed: int = 42):
    import lightgbm as lgb

    frame = deterministic_sample(files, max_rows=max_rows, seed=seed)
    x = frame[FEATURE_COLUMNS].astype(np.float32)
    y = frame["target_net_return"].astype(np.float32)
    params = dict(best_params)
    model = lgb.LGBMRegressor(
        objective="huber",
        n_estimators=900,
        random_state=seed,
        n_jobs=-1,
        verbosity=-1,
        **params,
    )
    model.fit(x, y)
    return model, {
        "rows": int(len(frame)),
        "sessions": len(files),
        "best_params": params,
        "model": "LightGBMRegressor",
    }


def walk_forward_baseline(files: list[Path], folds: int, cost_bps: float) -> dict:
    """Anchored expanding-window diagnostics using only pre-frozen sessions."""
    if folds <= 0 or len(files) < 120:
        return {"folds_requested": folds, "folds_executed": 0, "rows": []}
    rows = []
    total = len(files)
    initial = max(60, int(total * 0.45))
    remaining = total - initial
    block = max(20, remaining // folds)
    for fold in range(folds):
        train_end = min(total - 20, initial + fold * block)
        test_end = total if fold == folds - 1 else min(total, train_end + block)
        train = files[:train_end]
        test = files[train_end:test_end]
        if len(test) < 10:
            continue
        scaler, regressor, classifier, training = train_incremental(train, epochs=1)
        config = SelectionConfig(lightgbm_weight=0.0, top_k=3, min_probability=0.0)
        metrics, _ = evaluate_files(
            test, scaler, regressor, classifier, None, config, [float(cost_bps)]
        )
        rows.append({
            "fold": fold + 1,
            "train_sessions": len(train),
            "test_sessions": len(test),
            "train_start": train[0].name,
            "train_end": train[-1].name,
            "test_start": test[0].name,
            "test_end": test[-1].name,
            "training": training,
            "metrics": metrics,
        })
    base_key = str(float(cost_bps))
    mean_returns = [
        row["metrics"]["cost_stress"][base_key]["mean_daily_return"] for row in rows
    ]
    sharpes = [
        row["metrics"]["cost_stress"][base_key]["annualized_sharpe"]
        for row in rows
        if row["metrics"]["cost_stress"][base_key]["annualized_sharpe"] is not None
    ]
    return {
        "folds_requested": folds,
        "folds_executed": len(rows),
        "mean_fold_daily_return": float(np.mean(mean_returns)) if mean_returns else None,
        "positive_mean_return_folds": sum(value > 0 for value in mean_returns),
        "mean_fold_sharpe": float(np.mean(sharpes)) if sharpes else None,
        "rows": rows,
    }


def candidate_assessment(
    frozen: dict,
    base_cost_bps: float,
    selected_config: SelectionConfig,
) -> dict:
    key = str(float(base_cost_bps))
    metric = frozen["cost_stress"][key]
    probability_gate = (
        selected_config.min_probability <= 0
        or (frozen.get("row_roc_auc") or 0) > 0.50
    )
    gates = {
        "minimum_filled_trades_400": int(metric["trades"] >= 400),
        "fill_rate_above_80pct": int((frozen.get("fill_rate") or 0) >= 0.80),
        "positive_mean_portfolio_daily_return": int(metric["mean_daily_return"] > 0),
        "profit_factor_above_1": int((metric["profit_factor"] or 0) > 1.0),
        "sharpe_above_0": int((metric["annualized_sharpe"] or 0) > 0),
        "max_drawdown_below_25pct": int(metric["max_drawdown"] < 0.25),
        "positive_rank_correlation": int((frozen.get("median_daily_spearman") or 0) > 0),
        "top_k_overlap_above_5pct": int((frozen.get("mean_top_k_overlap") or 0) > 0.05),
        "classifier_unused_or_auc_above_random": int(probability_gate),
    }
    passed = sum(gates.values())
    return {
        "research_candidate": passed == len(gates),
        "gates_passed": passed,
        "gates_total": len(gates),
        "gates": gates,
        "promotion_allowed": False,
        "reason": (
            "Research candidate only; forward paper trading, broker fill/slippage "
            "reconciliation and operational risk gates remain mandatory."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--report-root", type=Path, required=True)
    parser.add_argument("--base-cost-bps", type=float, default=80.0)
    parser.add_argument("--embargo-days", type=int, default=1)
    parser.add_argument("--baseline-epochs", type=int, default=2)
    parser.add_argument("--optuna-trials", type=int, default=12)
    parser.add_argument("--challenger-train-rows", type=int, default=1_200_000)
    parser.add_argument("--challenger-valid-rows", type=int, default=250_000)
    parser.add_argument("--challenger-final-rows", type=int, default=1_500_000)
    parser.add_argument("--walk-forward-folds", type=int, default=3)
    parser.add_argument("--paper-capital-inr", type=float, default=100_000.0)
    args = parser.parse_args()

    ensure_analyzer_only()
    args.report_root.mkdir(parents=True, exist_ok=True)
    feature_root = args.work_root / "eod_features"
    costs = [40.0, 80.0, 120.0, 200.0]

    generation = generate_features(args.data_root, feature_root, args.base_cost_bps)
    train_files, valid_files, test_files, split = split_files(feature_root, args.embargo_days)

    baseline_scaler, baseline_regressor, baseline_classifier, baseline_training = train_incremental(
        train_files, epochs=args.baseline_epochs
    )
    challenger, challenger_tuning = train_lightgbm_challenger(
        train_files,
        valid_files,
        max_train_rows=args.challenger_train_rows,
        max_valid_rows=args.challenger_valid_rows,
        trials=args.optuna_trials,
    )
    best_config, validation_rows = validation_search(
        valid_files,
        baseline_scaler,
        baseline_regressor,
        baseline_classifier,
        challenger,
        costs=[args.base_cost_bps],
    )
    validation_path = args.report_root / "validation_search.json"
    validation_path.write_text(
        json.dumps(validation_rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    pretest_files = train_files + valid_files
    walk_forward = walk_forward_baseline(
        pretest_files, args.walk_forward_folds, args.base_cost_bps
    )
    (args.report_root / "walk_forward_proof.json").write_text(
        json.dumps(walk_forward, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    final_scaler, final_regressor, final_classifier, final_baseline_training = train_incremental(
        pretest_files, epochs=args.baseline_epochs
    )
    final_challenger, final_challenger_training = fit_final_lightgbm(
        pretest_files,
        challenger_tuning["best_params"],
        max_rows=args.challenger_final_rows,
    )
    frozen, selected_trades = evaluate_files(
        test_files,
        final_scaler,
        final_regressor,
        final_classifier,
        final_challenger,
        best_config,
        costs,
    )

    selected_path = args.report_root / "frozen_selected_trades.csv"
    selected_trades.to_csv(selected_path, index=False)
    ledger, paper = normalized_paper_ledger(
        selected_trades,
        cost_bps=args.base_cost_bps,
        initial_capital_inr=args.paper_capital_inr,
    )
    ledger_path = args.report_root / "normalized_paper_daily.csv"
    ledger.to_csv(ledger_path, index=False)
    paper_path = args.report_root / "normalized_paper_summary.json"
    paper_path.write_text(json.dumps(paper, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    model_path = args.report_root / "advanced_ensemble_model.joblib"
    joblib.dump({
        "features": FEATURE_COLUMNS,
        "scaler": final_scaler,
        "baseline_regressor": final_regressor,
        "baseline_classifier": final_classifier,
        "challenger": final_challenger,
        "selection": asdict(best_config),
        "per_trade_allocation": PER_TRADE_ALLOCATION,
        "maximum_daily_exposure": MAX_DAILY_EXPOSURE,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }, model_path)

    assessment = candidate_assessment(frozen, args.base_cost_bps, best_config)
    proof = {
        "status": "EXECUTED",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "data_root": str(args.data_root),
        "feature_root": str(feature_root),
        "feature_generation": generation,
        "split": asdict(split),
        "baseline_training_before_validation": baseline_training,
        "challenger_tuning": challenger_tuning,
        "validation_candidates": len(validation_rows),
        "validation_best": validation_rows[0],
        "selected_config": asdict(best_config),
        "walk_forward": walk_forward,
        "final_baseline_training": final_baseline_training,
        "final_challenger_training": final_challenger_training,
        "frozen_test": frozen,
        "paper_simulation": paper,
        "candidate_assessment": assessment,
        "execution_assumptions": {
            "signal_data_cutoff": "SESSION_T_CLOSE",
            "entry": "SESSION_T_PLUS_1_OPEN",
            "stop_loss_pct": generation.get("stop_loss_pct"),
            "take_profit_pct": generation.get("take_profit_pct"),
            "same_bar_stop_before_target": True,
            "minimum_premium": generation.get("minimum_premium"),
            "minimum_volume": generation.get("minimum_volume"),
            "minimum_open_interest": generation.get("minimum_open_interest"),
            "minimum_days_to_expiry": generation.get("minimum_days_to_expiry"),
            "maximum_days_to_expiry": generation.get("maximum_days_to_expiry"),
            "per_trade_allocation": PER_TRADE_ALLOCATION,
            "maximum_daily_exposure": MAX_DAILY_EXPOSURE,
            "no_fill_return": 0.0,
        },
        "model_path": str(model_path),
        "model_bytes": model_path.stat().st_size,
        "model_sha256": sha256_file(model_path),
        "validation_search_path": str(validation_path),
        "selected_trades_path": str(selected_path),
        "paper_ledger_path": str(ledger_path),
        "all_valid_pretest_rows_used_by_baseline": True,
        "challenger_sample_spans_every_pretest_session": True,
        "frozen_test_opened_after_validation_selection": True,
        "transaction_cost_bps": costs,
        "pnl_currency": "INR",
        "paper_pnl_is_normalized_notional": True,
        "historical_lot_sizes_used": False,
        "broker_fills_used": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "real_orders_attempted": 0,
        "promotion_allowed": False,
    }
    proof_path = args.report_root / "advanced_model_backtest_proof.json"
    proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
