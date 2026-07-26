#!/usr/bin/env python3
"""Generate all valid EOD option features, train incrementally, and backtest holdout."""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.options_research.eod_features import FEATURE_COLUMNS, generate_features
from src.options_research.eod_model import evaluate, split_files, train_incremental

TRUTHY = {"1", "true", "yes", "on"}


def ensure_analyzer_only() -> None:
    for name in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED"):
        if str(os.getenv(name, "0")).strip().lower() in TRUTHY:
            raise RuntimeError(f"{name} must remain disabled")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--report-root", type=Path, required=True)
    parser.add_argument("--base-cost-bps", type=float, default=80.0)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--embargo-days", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=2)
    args = parser.parse_args()
    ensure_analyzer_only()
    args.report_root.mkdir(parents=True, exist_ok=True)
    feature_root = args.work_root / "eod_features"
    generation = generate_features(args.data_root, feature_root, args.base_cost_bps)
    train_files, valid_files, test_files, split = split_files(feature_root, args.embargo_days)
    scaler, regressor, classifier, training = train_incremental(train_files, args.epochs)
    validation = evaluate(valid_files, scaler, regressor, classifier, args.top_k, [args.base_cost_bps])
    frozen_test = evaluate(test_files, scaler, regressor, classifier, args.top_k, [40.0, 80.0, 120.0])
    model_path = args.report_root / "eod_incremental_model.joblib"
    joblib.dump(
        {"scaler": scaler, "regressor": regressor, "classifier": classifier, "features": FEATURE_COLUMNS},
        model_path,
    )
    proof = {
        "status": "EXECUTED",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "feature_generation": generation,
        "split": asdict(split),
        "training": training,
        "validation": validation,
        "frozen_test": frozen_test,
        "model_path": str(model_path),
        "all_valid_train_rows_used": True,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "promotion_allowed": False,
        "pnl_currency_claimed": False,
        "note": "Return-based EOD research; no intraday fills or rupee P&L claim.",
    }
    (args.report_root / "eod_model_backtest_proof.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
