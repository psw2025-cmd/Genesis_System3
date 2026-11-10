"""Cloud-first readers for durable ML rank evidence.

Firestore business artifacts are production authority. Repository ``state/``
files are a development scratchpad and are consulted only when Firestore is not
configured as required.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def firestore_rank_configured() -> bool:
    return (
        os.environ.get("SYSTEM3_STATE_BACKEND", "").strip().lower() == "firestore"
        or bool(os.environ.get("SYSTEM3_FIRESTORE_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT"))
    )


def firestore_rank_required() -> bool:
    return firestore_rank_configured() and _truthy(os.environ.get("SYSTEM3_STATE_BACKEND_REQUIRED"))


def _snapshot_from_artifact(artifact: Dict[str, Any]) -> Dict[str, Any] | None:
    if not isinstance(artifact, dict) or str(artifact.get("status") or "").upper() != "PASS":
        return None
    payload = artifact.get("payload") if isinstance(artifact.get("payload"), dict) else {}
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    predictions: List[Dict[str, Any]] = []
    produced = str(artifact.get("produced_at_utc") or "")
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        if not (row.get("underlying") or row.get("symbol")):
            continue
        row.setdefault("prediction_ts", produced)
        row.setdefault("timestamp", produced)
        if row.get("score") is None and row.get("gain_score") is not None:
            row["score"] = row.get("gain_score")
        row.setdefault("source", "firestore:artifact_rank")
        predictions.append(row)
    if not predictions:
        return None
    business_date = str(artifact.get("business_date") or produced[:10])
    return {
        "date": business_date,
        "time": produced[11:19] if len(produced) >= 19 else "",
        "generated_utc": produced,
        "predictions": predictions,
        "rankings": predictions,
        "source": "firestore:artifact_rank",
        "artifact_version": artifact.get("artifact_version"),
        "run_id": artifact.get("run_id"),
    }


def load_rank_history(root: Path) -> Tuple[List[Dict[str, Any]], str, bool]:
    """Return ``(history, source, durable_required)``.

    A required Firestore configuration fails closed. It never promotes an
    ephemeral local file to production truth when the durable artifact is
    missing or unreadable.
    """
    configured = firestore_rank_configured()
    required = firestore_rank_required()
    if configured:
        try:
            from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend

            snapshot = _snapshot_from_artifact(FirestoreSchedulerEvidenceBackend().load_artifact("rank") or {})
            if snapshot:
                return [snapshot], "firestore:artifact_rank", required
            if required:
                return [], "firestore:artifact_rank:missing", True
        except Exception as exc:
            if required:
                return [], f"firestore:artifact_rank:error:{type(exc).__name__}", True

    local_path = Path(root) / "state" / "gain_rank_history.json"
    try:
        data = json.loads(local_path.read_text(encoding="utf-8")) if local_path.exists() else []
        if isinstance(data, list):
            return data, "local_scratch:state/gain_rank_history.json", required
    except Exception:
        pass
    return [], "local_scratch:state/gain_rank_history.json:missing", required
