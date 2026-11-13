"""Evidence-backed ML intelligence for the PAPER/ANALYZE dashboard.

Never fabricate inference timestamps, model accuracy, feature freshness, or
probabilities. A serialized model file proves neither that it loaded nor that
it generated a successful prediction. Read-only artifact inspection only.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]
MIN_MODEL_BYTES = 1024


def _read_json(path: Path) -> Optional[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, ValueError, UnicodeDecodeError):
        return None


def _artifact_rows(root: Path) -> list[dict]:
    """Hash present weights without unpickling untrusted model files."""
    folder = root / "models" / "xgboost_v1"
    out: list[dict] = []
    for path in sorted(folder.glob("*_xgb_model.pkl")):
        symbol = path.name.removesuffix("_xgb_model.pkl")
        metadata_path = folder / (symbol + "_xgb_meta.json")
        metadata = _read_json(metadata_path)
        try:
            size = path.stat().st_size
            with path.open("rb") as handle:
                digest = hashlib.file_digest(handle, "sha256").hexdigest()
        except OSError:
            continue
        meta_features = metadata.get("n_features") if isinstance(metadata, dict) else None
        meta_samples = metadata.get("n_samples") if isinstance(metadata, dict) else None
        out.append({
            "underlying": symbol,
            "model_type": "XGBoost candidate artifact",
            "artifact_path": str(path.relative_to(root)).replace("\\", "/"),
            "artifact_size_bytes": size,
            "artifact_sha256": digest,
            "metadata_available": metadata is not None,
            "metadata_reported_features": meta_features,
            "metadata_reported_samples": meta_samples,
            "model_loaded": False,
            "inference_verified": False,
            "model_proof_ready": False,
            "calibration_status": "NOT_VERIFIED",
            "status": (
                "WEIGHTS_PRESENT_UNVERIFIED"
                if size >= MIN_MODEL_BYTES
                else "ARTIFACT_TOO_SMALL"
            ),
        })
    return out


def get_ml_performance_data(root: Optional[Path] = None) -> Dict[str, Any]:
    """Supply only on-disk artifact facts and explicit validation blockers."""
    actual_root = Path(root) if root is not None else ROOT
    models = _artifact_rows(actual_root)
    accuracy_path = actual_root / "reports" / "latest" / "model_accuracy_report.json"
    report = _read_json(accuracy_path)
    summary = report.get("summary") if isinstance(report, dict) else None
    summary = summary if isinstance(summary, dict) else {}
    try:
        reported_proofs = max(0, int(summary.get("proof_pass_count") or 0))
    except (TypeError, ValueError):
        reported_proofs = 0
    return {
        "status": "BLOCKED",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "live_trading_enabled": False,
        "model_proof_ready": False,
        "ready_for_live": False,
        "blocker_reason": "NO_INDEPENDENT_VERIFIED_INFERENCE_AND_MATURED_OUTCOMES",
        "pipeline": {
            "status": "NOT_VERIFIED",
            "total_features": None,
            "reported_feature_count": max(
                (int(m["metadata_reported_features"])
                 for m in models
                 if isinstance(m.get("metadata_reported_features"), int)), default=0
            ) or None,
            "freshness_sec": None,
            "missing_features_count": None,
            "feature_categories": {},
            "reason": "No measured feature-producer heartbeat and schema evidence",
        },
        "feature_importance": [],
        "feature_importance_status": "NO_INDEPENDENT_MODEL_EXPLANATION",
        "active_models": models,
        "models": models,
        "validation_summary": {
            "gate_status": "BLOCKED",
            "spearman_rho_avg_5day": None,
            "total_predictions_logged": 0,
            "proof_pass_count_reported": reported_proofs,
            "accuracy_report_exists": report is not None,
            "accuracy_report_source": (
                "reports/latest/model_accuracy_report.json"
                if report is not None else None
            ),
            "reason": "Metadata and model files are not inference/outcome receipts",
        },
        "predictions": [],
        "prediction_status": "NO_CURRENT_VERIFIED_PREDICTION_LEDGER",
        "candidate_model_count": len(models),
    }


def get_ml_intelligence_data(root: Optional[Path] = None) -> Dict[str, Any]:
    """Read-only compatibility contract for /api/ml/intelligence."""
    data = get_ml_performance_data(root=root)
    data["source"] = "local_serialized_model_artifacts_and_report_metadata"
    data["message"] = (
        "Serialized model candidates found; no independent "
        "prediction-before-move or matured outcome proof is available."
    )
    data["model_registry"] = data["active_models"]
    return data
