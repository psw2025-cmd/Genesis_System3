"""No fabricated live model or trade evidence is permitted in ML UI."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from dashboard.backend.ml_intelligence_service import (
    get_ml_intelligence_data,
    get_ml_performance_data,
)


def test_absent_artifacts_fail_closed(tmp_path: Path):
    data = get_ml_performance_data(tmp_path)
    assert data["status"] == "BLOCKED"
    assert data["ready_for_live"] is False
    assert data["model_proof_ready"] is False
    assert data["predictions"] == []
    assert data["feature_importance"] == []
    assert data["pipeline"]["freshness_sec"] is None
    assert data["validation_summary"]["gate_status"] == "BLOCKED"


def test_real_file_not_equivalent_to_loaded_model(tmp_path: Path):
    folder = tmp_path / "models" / "xgboost_v1"
    folder.mkdir(parents=True)
    weights = b"sample-not-executable-model" * 100
    (folder / "NIFTY_xgb_model.pkl").write_bytes(weights)
    (folder / "NIFTY_xgb_meta.json").write_text(
        json.dumps({"n_features": 129, "n_samples": 965, "accuracy": 1.0}),
        encoding="utf-8",
    )
    payload = get_ml_intelligence_data(root=tmp_path)
    assert payload["status"] == "BLOCKED"
    assert payload["prediction_status"] == "NO_CURRENT_VERIFIED_PREDICTION_LEDGER"
    assert payload["models"][0]["artifact_sha256"] == hashlib.sha256(weights).hexdigest()
    assert payload["models"][0]["metadata_reported_features"] == 129
    assert payload["models"][0]["model_loaded"] is False
    assert payload["models"][0]["inference_verified"] is False
    assert payload["models"][0]["calibration_status"] == "NOT_VERIFIED"
    assert payload["validation_summary"]["spearman_rho_avg_5day"] is None


def test_accuracy_report_claim_cannot_promote_model(tmp_path: Path):
    folder = tmp_path / "reports" / "latest"
    folder.mkdir(parents=True)
    (folder / "model_accuracy_report.json").write_text(
        json.dumps({"summary": {"proof_pass_count": 30, "rows": 30}}),
        encoding="utf-8",
    )
    data = get_ml_performance_data(tmp_path)
    assert data["validation_summary"]["proof_pass_count_reported"] == 30
    assert data["validation_summary"]["gate_status"] == "BLOCKED"
    assert data["predictions"] == []
    assert data["ready_for_live"] is False


def test_small_placeholder_weights_not_promoted(tmp_path: Path):
    folder = tmp_path / "models" / "xgboost_v1"
    folder.mkdir(parents=True)
    (folder / "NIFTY_xgb_model.pkl").write_bytes(b"placeholder")
    result = get_ml_performance_data(tmp_path)
    assert result["candidate_model_count"] == 1
    assert result["active_models"][0]["status"] == "ARTIFACT_TOO_SMALL"
    assert result["active_models"][0]["model_proof_ready"] is False


def test_metadata_invalid_file_is_reported_unverified(tmp_path: Path):
    folder = tmp_path / "models" / "xgboost_v1"
    folder.mkdir(parents=True)
    (folder / "SENSEX_xgb_model.pkl").write_bytes(b"0" * 2000)
    (folder / "SENSEX_xgb_meta.json").write_text("{BAD JSON", encoding="utf-8")
    model = get_ml_performance_data(tmp_path)["active_models"][0]
    assert model["metadata_available"] is False
    assert model["model_proof_ready"] is False
