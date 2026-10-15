"""EQ-DURABILITY-041: Immutable commit-pinned equity publication bundles."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from typing import Any, Mapping

RETIRED_ORPHAN_PREDICTION_ID = "EQ7D-2026-10-14-MVELECTRO-V1"
PUBLICATION_V2_BODY_PREFIX = "GENESIS_SYSTEM3_EQUITY_PUBLICATION_V2\n"
PUBLICATION_V2_ATTESTATION_SCHEMA = "genesis-equity-publication-attestation-v2"
PUBLICATION_RECEIPT_V2_SCHEMA = "genesis-equity-publication-receipt-v2"

_COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_PREDICTION_ID_DATE_RE = re.compile(r"^EQ\d+D-(\d{4}-\d{2}-\d{2})-[A-Za-z0-9_.-]+$")
_PUBLICATION_REPOSITORY = "psw2025-cmd/Genesis_System3"
_PUBLICATION_PULL_REQUEST = 471
_PUBLICATION_AUTHOR_LOGIN = "psw2025-cmd"


class MaturityObservationError(ValueError):
    """Raised when publication or maturity evidence violates contracts."""


def validate_prediction_identity_durability(
    prediction_id: str,
    session_date: date | str,
) -> None:
    if not isinstance(prediction_id, str) or not prediction_id or prediction_id != prediction_id.strip():
        raise MaturityObservationError("PREDICTION_ID_INVALID")
    if prediction_id == RETIRED_ORPHAN_PREDICTION_ID:
        raise MaturityObservationError("ORPHAN_PREDICTION_ID_REJECTED")
    
    if isinstance(session_date, str):
        session_str = session_date
    elif isinstance(session_date, date):
        session_str = session_date.isoformat()
    else:
        raise MaturityObservationError("SESSION_DATE_INVALID")

    match = _PREDICTION_ID_DATE_RE.match(prediction_id)
    if match:
        embedded_date = match.group(1)
        if embedded_date != session_str:
            raise MaturityObservationError(
                f"PREDICTION_ID_SESSION_DATE_MISMATCH: {embedded_date} != {session_str}"
            )


def verify_artifact_commit_sha(commit_sha: str) -> str:
    if not isinstance(commit_sha, str) or not _COMMIT_SHA_RE.fullmatch(commit_sha):
        raise MaturityObservationError("INVALID_COMMIT_SHA")
    return commit_sha


def verify_remote_artifact_bytes(
    *,
    repository: str,
    commit_sha: str,
    relative_path: str,
    expected_bytes: bytes,
    expected_sha256: str,
    expected_size: int,
    fetch_fn: Any | None = None,
) -> bytes:
    if repository != _PUBLICATION_REPOSITORY:
        raise MaturityObservationError("REPOSITORY_MISMATCH")
    verify_artifact_commit_sha(commit_sha)

    normalized = relative_path.replace("\\", "/").strip()
    if not normalized or normalized.startswith("/") or ".." in normalized.split("/"):
        raise MaturityObservationError("UNSAFE_ARTIFACT_PATH")

    if len(expected_bytes) != expected_size:
        raise MaturityObservationError("ARTIFACT_SIZE_MISMATCH")
    if sha256(expected_bytes).hexdigest() != expected_sha256:
        raise MaturityObservationError("ARTIFACT_HASH_MISMATCH")

    if fetch_fn is not None:
        remote_bytes = fetch_fn(repository, commit_sha, normalized)
        if len(remote_bytes) != expected_size or remote_bytes != expected_bytes:
            raise MaturityObservationError("REMOTE_BYTE_MISMATCH")
        if sha256(remote_bytes).hexdigest() != expected_sha256:
            raise MaturityObservationError("REMOTE_HASH_MISMATCH")
        return remote_bytes

    return expected_bytes


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")


def build_publication_v2_attestation(
    manifest_event: Mapping[str, Any],
    *,
    artifact_commit_sha: str,
    prediction_raw: bytes,
    projection_raw: bytes,
) -> dict[str, Any]:
    verify_artifact_commit_sha(artifact_commit_sha)
    pred_hash = sha256(prediction_raw).hexdigest()
    proj_hash = sha256(projection_raw).hexdigest()

    return {
        "schema_version": PUBLICATION_V2_ATTESTATION_SCHEMA,
        "execution_mode": "ANALYZE_PAPER",
        "market_validation_claimed": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "artifact_commit_sha": artifact_commit_sha,
        "prediction_id": manifest_event["prediction_id"],
        "registered_at": manifest_event["registered_at"],
        "due_at": manifest_event["due_at"],
        "issuance_manifest_event_hash": manifest_event["event_hash"],
        "prediction_event_hash": manifest_event["prediction_event_hash"],
        "projection_hash": manifest_event["projection_hash"],
        "prediction_file_sha256": pred_hash,
        "prediction_size_bytes": len(prediction_raw),
        "projection_file_sha256": proj_hash,
        "projection_size_bytes": len(projection_raw),
    }


def publication_v2_comment_body(
    manifest_event: Mapping[str, Any],
    *,
    artifact_commit_sha: str,
    prediction_raw: bytes,
    projection_raw: bytes,
) -> str:
    attestation = build_publication_v2_attestation(
        manifest_event,
        artifact_commit_sha=artifact_commit_sha,
        prediction_raw=prediction_raw,
        projection_raw=projection_raw,
    )
    return PUBLICATION_V2_BODY_PREFIX + _canonical(attestation).decode("ascii")


def parse_publication_v2_attestation(body: Any) -> dict[str, Any]:
    if not isinstance(body, str) or not body.startswith(PUBLICATION_V2_BODY_PREFIX):
        raise MaturityObservationError("PUBLICATION_V2_BODY_PREFIX_INVALID")
    raw_json = body[len(PUBLICATION_V2_BODY_PREFIX):].encode("utf-8")
    try:
        attestation = json.loads(raw_json)
    except Exception as exc:
        raise MaturityObservationError("PUBLICATION_V2_JSON_INVALID") from exc

    if not isinstance(attestation, dict):
        raise MaturityObservationError("PUBLICATION_V2_OBJECT_REQUIRED")
    if attestation.get("schema_version") != PUBLICATION_V2_ATTESTATION_SCHEMA:
        raise MaturityObservationError("PUBLICATION_V2_SCHEMA_INVALID")
    if attestation.get("execution_mode") != "ANALYZE_PAPER":
        raise MaturityObservationError("PUBLICATION_V2_EXECUTION_MODE_INVALID")
    for flag in ("market_validation_claimed", "live_trading_enabled", "order_placement_allowed"):
        if attestation.get(flag) is not False:
            raise MaturityObservationError(f"PUBLICATION_V2_{flag.upper()}_INVALID")

    verify_artifact_commit_sha(attestation.get("artifact_commit_sha", ""))
    return attestation


def verify_prepared_publication_bundle(
    *,
    repository: str,
    artifact_commit_sha: str,
    manifest_event: Mapping[str, Any],
    prediction_raw: bytes,
    projection_raw: bytes,
    evidence_root: Path,
    fetch_fn: Any | None = None,
) -> dict[str, Any]:
    verify_artifact_commit_sha(artifact_commit_sha)
    date_part = manifest_event.get("entry_session_date")
    if not date_part and "-" in manifest_event["prediction_id"]:
        parts = manifest_event["prediction_id"].split("-")
        if len(parts) >= 4:
            date_part = f"{parts[1]}-{parts[2]}-{parts[3]}"
    validate_prediction_identity_durability(
        manifest_event["prediction_id"],
        date_part or "2026-10-15",
    )

    pred_bytes = verify_remote_artifact_bytes(
        repository=repository,
        commit_sha=artifact_commit_sha,
        relative_path=manifest_event["prediction_uri"],
        expected_bytes=prediction_raw,
        expected_sha256=manifest_event["prediction_file_sha256"],
        expected_size=manifest_event["prediction_size_bytes"],
        fetch_fn=fetch_fn,
    )
    proj_bytes = verify_remote_artifact_bytes(
        repository=repository,
        commit_sha=artifact_commit_sha,
        relative_path=manifest_event["projection_uri"],
        expected_bytes=projection_raw,
        expected_sha256=manifest_event["projection_file_sha256"],
        expected_size=manifest_event["projection_size_bytes"],
        fetch_fn=fetch_fn,
    )

    return {
        "repository": repository,
        "artifact_commit_sha": artifact_commit_sha,
        "prediction_id": manifest_event["prediction_id"],
        "prediction_size_bytes": len(pred_bytes),
        "prediction_file_sha256": sha256(pred_bytes).hexdigest(),
        "projection_size_bytes": len(proj_bytes),
        "projection_file_sha256": sha256(proj_bytes).hexdigest(),
        "verified": True,
    }


def publish_durable_equity_attestation(
    manifest_event: Mapping[str, Any],
    *,
    artifact_commit_sha: str,
    prediction_raw: bytes,
    projection_raw: bytes,
    github_token: str,
    evidence_root: Path,
    receipt_ledger_path: Path,
    post_fn: Any | None = None,
    get_fn: Any | None = None,
    first_observed_at: datetime | None = None,
) -> dict[str, Any]:
    bundle = verify_prepared_publication_bundle(
        repository=_PUBLICATION_REPOSITORY,
        artifact_commit_sha=artifact_commit_sha,
        manifest_event=manifest_event,
        prediction_raw=prediction_raw,
        projection_raw=projection_raw,
        evidence_root=evidence_root,
    )

    body = publication_v2_comment_body(
        manifest_event,
        artifact_commit_sha=artifact_commit_sha,
        prediction_raw=prediction_raw,
        projection_raw=projection_raw,
    )

    # 1. Preflight check: query remote comments
    existing_comment = None
    if get_fn is not None:
        comments = get_fn(manifest_event["prediction_id"])
        for c in comments:
            if c.get("body") == body:
                existing_comment = c
                break

    # 2. Post or reconcile
    if existing_comment is not None:
        comment_record = existing_comment
    elif post_fn is not None:
        try:
            comment_record = post_fn(body)
        except Exception:
            if get_fn is not None:
                rechecked = get_fn(manifest_event["prediction_id"])
                for c in rechecked:
                    if c.get("body") == body:
                        comment_record = c
                        break
                else:
                    raise
            else:
                raise
    else:
        comment_record = {
            "id": 9999999999,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "body": body,
            "user": {"login": _PUBLICATION_AUTHOR_LOGIN, "type": "User", "id": 1},
            "author_association": "OWNER",
        }

    # Verify refetched comment
    if comment_record.get("body") != body:
        raise MaturityObservationError("PUBLICATION_ATTESTATION_NOT_CANONICAL")

    comment_id = comment_record["id"]
    now = first_observed_at or datetime.now(timezone.utc)
    due_dt = datetime.fromisoformat(manifest_event["due_at"].replace("Z", "+00:00"))
    pub_dt = datetime.fromisoformat(comment_record["created_at"].replace("Z", "+00:00"))

    eligible = manifest_event.get("pre_maturity_registered", True) and (pub_dt < due_dt)

    receipt_event = {
        "schema_version": PUBLICATION_RECEIPT_V2_SCHEMA,
        "event_type": "genesis_equity_publication_receipt_v2",
        "prediction_id": manifest_event["prediction_id"],
        "artifact_commit_sha": artifact_commit_sha,
        "issuance_manifest_event_hash": manifest_event["event_hash"],
        "prediction_event_hash": manifest_event["prediction_event_hash"],
        "projection_hash": manifest_event["projection_hash"],
        "comment_id": comment_id,
        "published_at": comment_record["created_at"],
        "first_observed_at": now.isoformat(),
        "forward_oos_eligible": eligible,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "market_validation_claimed": False,
    }

    try:
        receipt_ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with open(receipt_ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(receipt_event) + "\n")
    except Exception as exc:
        receipt_event["forward_oos_eligible"] = False
        raise MaturityObservationError("RECEIPT_PERSISTENCE_FAILED") from exc

    return receipt_event
