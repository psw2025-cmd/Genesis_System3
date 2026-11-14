"""Model holdout must follow market time and reject resampled/leaky features."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest

from model_training_v2 import TrainingConfig, point_in_time_split, train_models_per_underlying


def _dated_frame():
    start = datetime(2026, 9, 1, 9, 30, tzinfo=timezone.utc)
    rows = []
    for day in range(40):
        ts = start + timedelta(days=day)
        rows.append({"underlying": "NIFTY", "signal": "BUY" if day % 2 else "HOLD",
                     "ts": ts.isoformat(), "label_available_at": (ts + timedelta(hours=1)).isoformat(),
                     "data_origin": "dhan_timestamped", "feature_oi_change": float(day),
                     "fwd_ret_2": float(day % 2)})
    return pd.DataFrame(rows)


def test_holdout_is_chronological_and_forward_return_is_excluded():
    train, test, features = point_in_time_split(_dated_frame(), 0.2)
    assert features == ["feature_oi_change"]
    assert train["_label_time"].max() < test["_feature_time"].min()
    assert train["_feature_time"].max() < test["_feature_time"].min()


def test_missing_proof_or_future_feature_blocks_training():
    frame = _dated_frame()
    with pytest.raises(ValueError, match="POINT_IN_TIME_PROOF_MISSING"):
        point_in_time_split(frame.drop(columns=["label_available_at"]), 0.2)
    frame["feature_future_return"] = frame["fwd_ret_2"]
    with pytest.raises(ValueError, match="SAFE_FEATURE_SCHEMA_MISSING"):
        point_in_time_split(frame, 0.2)


def test_smote_rows_cannot_train_or_overwrite_model_artifacts(tmp_path: Path):
    frame = _dated_frame()
    frame["data_origin"] = "smote"
    config = TrainingConfig(min_samples_per_underlying=10, model_dir=str(tmp_path / "models"))
    result = train_models_per_underlying(frame, config)
    assert result["underlyings_trained"] == []
    assert any("UNVERIFIED_OR_RESAMPLED_TRAINING_DATA" in warning for warning in result["warnings"])
    assert not list((tmp_path / "models").glob("*.pkl"))


def test_phase391_does_not_feed_presplit_smote_csv_to_trainer():
    source = (Path(__file__).resolve().parents[1] / "core/engine/system3_phase391_xgboost_training.py").read_text()
    assert 'csv_path = "storage/datasets/phase_389_engineered_features.csv"' in source
    trainer = (Path(__file__).resolve().parents[1] / "model_training_v2.py").read_text()
    assert '"model_proof_ready": False' in trainer
    assert '"ready_for_live": False' in trainer
