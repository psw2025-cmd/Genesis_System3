"""EQ-DURABILITY-041: Commit-pinned equity publication bundles and durability gate.

Enforces:
prepare exact validated bytes
-> commit/push exact prediction/projection/manifest bytes
-> independently retrieve all three from remote immutable commit
-> verify repository, paths, lengths, hashes and semantic bindings
-> only then permit canonical publication
-> refetch/validate exact remote comment
-> retain separate durable valid receipt
-> only then enable publication-dependent eligibility.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RETIRED_ORPHAN_PREDICTION_ID = "EQ7D-2026-10-14-MVELECTRO-V1"
PUBLICATION_V2_BODY_PREFIX = "GENESIS_SYSTEM3_EQUITY_PUBLICATION_V2\n"
PUBLICATION_V2_ATTESTATION_SCHEMA = "genesis-equity-publication-attestation-v2"
PUBLICATION_RECEIPT_V2_SCHEMA = "genesis-equity-publication-receipt-v2"
PUBLICATION_RECEIPT_GENESIS_HASH = "0" * 64

_COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_PREDICTION_ID_DATE_RE = re.compile(r"^EQ\d+D-(\d{4}-\d{2}-\d{2})-[A-Za-z0-9_.-]+$")

_PUBLICATION_REPOSITORY = "psw2025-cmd/Genesis_System3"
_PUBLICATION_PULL_REQUEST = 471
_PUBLICATION_AUTHOR_LOGIN = "psw2025-cmd"

_PUBLICATION_V2_ATTESTATION_FIELDS = frozenset({
    "schema_version",
    "execution_mode",
    "market_validation_claimed",
    "live_trading_enabled",
    "order_placement_allowed",
    "artifact_commit_sha",
    "prediction_id",
    "registered_at",
    "due_at",
    "issuance_manifest_event_hash",
    "prediction_event_hash",
    "projection_hash",
    "prediction_file_sha256",
    "prediction_size_bytes",
    "projection_file_sha256",
    "projection_size_bytes",
})


class MaturityObservationError(ValueError):
    """Raised when publication or maturity evidence violates contracts."""


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")


def _strict_json_object(raw: bytes | str, label: str = "JSON") -> dict[str, Any]:
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    try:
        val = json.loads(raw)
    except Exception as exc:
        raise MaturityObservationError(f"{label}_INVALID_JSON") from exc
    if not isinstance(val, dict):
        raise MaturityObservationError(f"{label}_OBJECT_REQUIRED")
    return val


def _time(val: Any, label: str = "TIME") -> datetime:
    if not isinstance(val, str) or not val:
        raise MaturityObservationError(f"{label}_INVALID")
    try:
        dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
    except Exception as exc:
        raise MaturityObservationError(f"{label}_PARSE_FAILED") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise MaturityObservationError(f"{label}_TIMEZONE_REQUIRED")
    return dt.astimezone(timezone.utc)


@contextmanager
def _ledger_lock(path: Path, exclusive: bool = True):
    """File lock implementation supporting cross-platform process isolation."""
    lock_path = path.parent / f".{path.name}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0)
    descriptor = os.open(lock_path, flags, 0o600)
    try:
        if os.name == "nt":
            import msvcrt
            pos = 0
            nbytes = 1
            op = msvcrt.LK_NBLCK if exclusive else msvcrt.LK_NBRLCK
            msvcrt.locking(descriptor, op, nbytes)
        else:
            import fcntl
            op = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(descriptor, op)
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt
                try:
                    msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
            else:
                import fcntl
                try:
                    fcntl.flock(descriptor, fcntl.LOCK_UN)
                except OSError:
                    pass
        finally:
            os.close(descriptor)


def validate_prediction_identity_durability(
    prediction_id: str,
    session_date: date | str,
) -> None:
    """Permanently reject the orphaned identity and reject session date mismatch."""
    if not isinstance(prediction_id, str) or not prediction_id or prediction_id != prediction_id.strip():
        raise MaturityObservationError("PREDICTION_ID_INVALID")
    if prediction_id == RETIRED_ORPHAN_PREDICTION_ID:
        raise MaturityObservationError("ORPHAN_PREDICTION_ID_REJECTED")

    if isinstance(session_date, date):
        session_str = session_date.isoformat()
    elif isinstance(session_date, str) and re.fullmatch(r"^\d{4}-\d{2}-\d{2}$", session_date):
        session_str = session_date
    else:
        raise MaturityObservationError("SESSION_DATE_REQUIRED")

    match = _PREDICTION_ID_DATE_RE.match(prediction_id)
    if not match:
        raise MaturityObservationError("PREDICTION_ID_STRUCTURE_INVALID")
    embedded_date = match.group(1)
    if embedded_date != session_str:
        raise MaturityObservationError(
            f"PREDICTION_ID_SESSION_DATE_MISMATCH: embedded {embedded_date} != session {session_str}"
        )


def verify_artifact_commit_sha(commit_sha: str) -> str:
    """Verify commit SHA is an immutable 40-character hex string."""
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
    fetch_fn: Callable[[str, str, str], bytes] | None = None,
) -> bytes:
    """Fetch and verify exact bytes from an immutable commit. Fails closed if no fetcher."""
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

    if fetch_fn is None:
        raise MaturityObservationError("REMOTE_ARTIFACT_FETCHER_REQUIRED")

    remote_bytes = fetch_fn(repository, commit_sha, normalized)
    if not isinstance(remote_bytes, bytes):
        raise MaturityObservationError("REMOTE_FETCH_INVALID_TYPE")
    if len(remote_bytes) != expected_size:
        raise MaturityObservationError("ARTIFACT_SIZE_MISMATCH")
    if remote_bytes != expected_bytes:
        raise MaturityObservationError("REMOTE_BYTE_MISMATCH")
    if sha256(remote_bytes).hexdigest() != expected_sha256:
        raise MaturityObservationError("REMOTE_HASH_MISMATCH")
    return remote_bytes


def build_publication_v2_attestation(
    manifest_event: Mapping[str, Any],
    *,
    artifact_commit_sha: str,
    prediction_raw: bytes,
    projection_raw: bytes,
) -> dict[str, Any]:
    """Build canonical v2 attestation dictionary."""
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
    """Return exact machine-readable v2 comment body."""
    attestation = build_publication_v2_attestation(
        manifest_event,
        artifact_commit_sha=artifact_commit_sha,
        prediction_raw=prediction_raw,
        projection_raw=projection_raw,
    )
    return PUBLICATION_V2_BODY_PREFIX + _canonical(attestation).decode("ascii")


def parse_publication_v2_attestation(body: Any) -> dict[str, Any]:
    """Parse and validate canonical v2 attestation with strict schema enforcement."""
    if not isinstance(body, str) or not body.startswith(PUBLICATION_V2_BODY_PREFIX):
        raise MaturityObservationError("PUBLICATION_V2_BODY_PREFIX_INVALID")
    raw_json = body[len(PUBLICATION_V2_BODY_PREFIX):].encode("utf-8")
    try:
        attestation = json.loads(raw_json)
    except Exception as exc:
        raise MaturityObservationError("PUBLICATION_V2_JSON_INVALID") from exc

    if not isinstance(attestation, dict):
        raise MaturityObservationError("PUBLICATION_V2_OBJECT_REQUIRED")
    if set(attestation) != _PUBLICATION_V2_ATTESTATION_FIELDS:
        raise MaturityObservationError("PUBLICATION_V2_FIELDS_INVALID")
    if attestation.get("schema_version") != PUBLICATION_V2_ATTESTATION_SCHEMA:
        raise MaturityObservationError("PUBLICATION_V2_SCHEMA_INVALID")
    if attestation.get("execution_mode") != "ANALYZE_PAPER":
        raise MaturityObservationError("PUBLICATION_V2_EXECUTION_MODE_INVALID")
    for flag in ("market_validation_claimed", "live_trading_enabled", "order_placement_allowed"):
        if attestation.get(flag) is not False:
            raise MaturityObservationError(f"PUBLICATION_V2_{flag.upper()}_INVALID")

    verify_artifact_commit_sha(attestation["artifact_commit_sha"])

    pred_id = attestation["prediction_id"]
    if not isinstance(pred_id, str) or not pred_id or pred_id != pred_id.strip() or len(pred_id) > 128:
        raise MaturityObservationError("PUBLICATION_V2_PREDICTION_ID_INVALID")
    if pred_id == RETIRED_ORPHAN_PREDICTION_ID:
        raise MaturityObservationError("ORPHAN_PREDICTION_ID_REJECTED")

    for hash_field in (
        "issuance_manifest_event_hash",
        "prediction_event_hash",
        "projection_hash",
        "prediction_file_sha256",
        "projection_file_sha256",
    ):
        val = attestation[hash_field]
        if not isinstance(val, str) or not _SHA256_RE.fullmatch(val):
            raise MaturityObservationError(f"PUBLICATION_V2_{hash_field.upper()}_INVALID")

    _time(attestation["registered_at"], "PUBLICATION_V2_REGISTERED_AT")
    _time(attestation["due_at"], "PUBLICATION_V2_DUE_AT")

    for size_field in ("prediction_size_bytes", "projection_size_bytes"):
        val = attestation[size_field]
        if isinstance(val, bool) or not isinstance(val, int) or val <= 0:
            raise MaturityObservationError(f"PUBLICATION_V2_{size_field.upper()}_INVALID")

    return attestation


def verify_prepared_publication_bundle(
    *,
    repository: str,
    artifact_commit_sha: str,
    manifest_event: Mapping[str, Any],
    manifest_uri: str,
    manifest_raw: bytes,
    prediction_raw: bytes,
    projection_raw: bytes,
    session_date: date | str,
    evidence_root: Path,
    fetch_fn: Callable[[str, str, str], bytes] | None = None,
) -> dict[str, Any]:
    """Verify prediction, projection, and manifest from immutable commit with semantic replay."""
    if fetch_fn is None:
        raise MaturityObservationError("REMOTE_ARTIFACT_FETCHER_REQUIRED")
    verify_artifact_commit_sha(artifact_commit_sha)

    # 1. Identity and authentic session date check (no hardcoded fallback!)
    validate_prediction_identity_durability(
        manifest_event["prediction_id"],
        session_date,
    )

    # 2. Fetch and verify exact manifest bytes from commit
    manifest_bytes = verify_remote_artifact_bytes(
        repository=repository,
        commit_sha=artifact_commit_sha,
        relative_path=manifest_uri,
        expected_bytes=manifest_raw,
        expected_sha256=sha256(manifest_raw).hexdigest(),
        expected_size=len(manifest_raw),
        fetch_fn=fetch_fn,
    )

    # 3. Fetch and verify prediction bytes from commit
    pred_bytes = verify_remote_artifact_bytes(
        repository=repository,
        commit_sha=artifact_commit_sha,
        relative_path=manifest_event["prediction_uri"],
        expected_bytes=prediction_raw,
        expected_sha256=manifest_event["prediction_file_sha256"],
        expected_size=manifest_event["prediction_size_bytes"],
        fetch_fn=fetch_fn,
    )

    # 4. Fetch and verify projection bytes from commit
    proj_bytes = verify_remote_artifact_bytes(
        repository=repository,
        commit_sha=artifact_commit_sha,
        relative_path=manifest_event["projection_uri"],
        expected_bytes=projection_raw,
        expected_sha256=manifest_event["projection_file_sha256"],
        expected_size=manifest_event["projection_size_bytes"],
        fetch_fn=fetch_fn,
    )

    # 5. Semantic replay
    if not manifest_bytes.endswith(b"\n"):
        raise MaturityObservationError("MANIFEST_RAW_TRUNCATED")
    manifest_rows = [
        _strict_json_object(line, "MANIFEST_ROW")
        for line in manifest_bytes.splitlines()
        if line.strip()
    ]
    matching_events = [
        ev for ev in manifest_rows
        if ev.get("prediction_id") == manifest_event["prediction_id"]
    ]
    if len(matching_events) != 1 or matching_events[0] != dict(manifest_event):
        raise MaturityObservationError("MANIFEST_EVENT_SEMANTIC_MISMATCH")

    pred_obj = _strict_json_object(pred_bytes, "PREDICTION_OBJECT")
    if pred_obj.get("prediction_id") != manifest_event["prediction_id"]:
        raise MaturityObservationError("PREDICTION_SEMANTIC_ID_MISMATCH")
    if pred_obj.get("event_hash") != manifest_event["prediction_event_hash"]:
        raise MaturityObservationError("PREDICTION_SEMANTIC_HASH_MISMATCH")

    proj_obj = _strict_json_object(proj_bytes, "PROJECTION_OBJECT")
    if proj_obj.get("prediction_id") != manifest_event["prediction_id"]:
        raise MaturityObservationError("PROJECTION_SEMANTIC_ID_MISMATCH")
    if proj_obj.get("projection_hash") != manifest_event["projection_hash"]:
        raise MaturityObservationError("PROJECTION_SEMANTIC_HASH_MISMATCH")

    return {
        "repository": repository,
        "artifact_commit_sha": artifact_commit_sha,
        "prediction_id": manifest_event["prediction_id"],
        "manifest_uri": manifest_uri,
        "prediction_size_bytes": len(pred_bytes),
        "prediction_file_sha256": sha256(pred_bytes).hexdigest(),
        "projection_size_bytes": len(proj_bytes),
        "projection_file_sha256": sha256(proj_bytes).hexdigest(),
        "semantic_replay_passed": True,
    }


def publish_durable_equity_attestation(
    manifest_event: Mapping[str, Any],
    *,
    manifest_uri: str,
    manifest_raw: bytes,
    artifact_commit_sha: str,
    prediction_raw: bytes,
    projection_raw: bytes,
    session_date: date | str,
    evidence_root: Path,
    receipt_ledger_path: Path,
    github_token: str | None = None,
    fetch_fn: Callable[[str, str, str], bytes] | None = None,
    post_fn: Callable[[str], dict[str, Any]] | None = None,
    get_fn: Callable[[str], list[dict[str, Any]]] | None = None,
    first_observed_at: datetime | None = None,
) -> dict[str, Any]:
    """Serialized, idempotent, crash-resilient publication with receipt persistence."""
    if fetch_fn is None:
        raise MaturityObservationError("REMOTE_ARTIFACT_FETCHER_REQUIRED")
    if post_fn is None:
        raise MaturityObservationError("PUBLICATION_POST_ADAPTER_REQUIRED")
    if get_fn is None:
        raise MaturityObservationError("PUBLICATION_GET_ADAPTER_REQUIRED")

    bundle = verify_prepared_publication_bundle(
        repository=_PUBLICATION_REPOSITORY,
        artifact_commit_sha=artifact_commit_sha,
        manifest_event=manifest_event,
        manifest_uri=manifest_uri,
        manifest_raw=manifest_raw,
        prediction_raw=prediction_raw,
        projection_raw=projection_raw,
        session_date=session_date,
        evidence_root=evidence_root,
        fetch_fn=fetch_fn,
    )

    body = publication_v2_comment_body(
        manifest_event,
        artifact_commit_sha=artifact_commit_sha,
        prediction_raw=prediction_raw,
        projection_raw=projection_raw,
    )

    receipt_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with _ledger_lock(receipt_ledger_path, exclusive=True):
        previous_hash = PUBLICATION_RECEIPT_GENESIS_HASH
        existing_events = []
        if receipt_ledger_path.is_dir():
            raise MaturityObservationError("RECEIPT_PATH_CANNOT_BE_DIRECTORY")
        if receipt_ledger_path.is_file():
            with open(receipt_ledger_path, "rb") as rf:
                raw_ledger = rf.read()
            if raw_ledger and not raw_ledger.endswith(b"\n"):
                raise MaturityObservationError("PUBLICATION_RECEIPT_LEDGER_TRUNCATED")
            for line in raw_ledger.splitlines():
                if line.strip():
                    ev = _strict_json_object(line, "RECEIPT_ROW")
                    existing_events.append(ev)
                    previous_hash = ev["event_hash"]

        for ev in existing_events:
            if ev.get("prediction_id") == manifest_event["prediction_id"]:
                return ev

        # Durable pending journal before remote POST
        pending_path = receipt_ledger_path.parent / f".pending_{manifest_event['prediction_id']}.json"
        pending_data = {
            "prediction_id": manifest_event["prediction_id"],
            "artifact_commit_sha": artifact_commit_sha,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_BINARY", 0)
        desc = os.open(pending_path, flags, 0o600)
        with os.fdopen(desc, "wb") as pf:
            pf.write(_canonical(pending_data))
            pf.flush()
            os.fsync(pf.fileno())

        try:
            # Preflight check: query remote comments for this prediction_id
            existing_comment = None
            remote_comments = get_fn(manifest_event["prediction_id"])
            for c in remote_comments:
                c_body = c.get("body", "")
                if c_body.startswith(PUBLICATION_V2_BODY_PREFIX):
                    parsed = parse_publication_v2_attestation(c_body)
                    if parsed["prediction_id"] == manifest_event["prediction_id"]:
                        if c_body == body:
                            existing_comment = c
                            break
                        else:
                            raise MaturityObservationError("GITHUB_PUBLICATION_REMOTE_IDENTITY_COLLISION")

            # Post or reconcile
            if existing_comment is not None:
                comment_record = existing_comment
            else:
                try:
                    comment_record = post_fn(body)
                except Exception as exc:
                    rechecked = get_fn(manifest_event["prediction_id"])
                    for c in rechecked:
                        if c.get("body") == body:
                            comment_record = c
                            break
                    else:
                        raise MaturityObservationError("PUBLICATION_POST_FAILED") from exc

            # Refetch exact comment from remote to verify remote persistence
            refetched = None
            rechecked = get_fn(manifest_event["prediction_id"])
            for c in rechecked:
                if c.get("id") == comment_record.get("id"):
                    refetched = c
                    break
            if refetched is None:
                raise MaturityObservationError("PUBLICATION_REFETCH_NOT_FOUND")
            if refetched.get("body") != body:
                raise MaturityObservationError("PUBLICATION_ATTESTATION_NOT_CANONICAL")
            if refetched.get("created_at") != refetched.get("updated_at"):
                raise MaturityObservationError("PUBLICATION_EDITED_COMMENT_FORBIDDEN")

            comment_id = refetched["id"]
            now = first_observed_at or datetime.now(timezone.utc)
            due_dt = _time(manifest_event["due_at"], "DUE_AT")
            pub_dt = _time(refetched["created_at"], "PUBLISHED_AT")

            eligible = manifest_event.get("pre_maturity_registered", True) and (pub_dt < due_dt)

            source_raw = _canonical(refetched)
            receipt_event = {
                "schema_version": PUBLICATION_RECEIPT_V2_SCHEMA,
                "event_type": "genesis_equity_publication_receipt_v2",
                "prediction_id": manifest_event["prediction_id"],
                "artifact_commit_sha": artifact_commit_sha,
                "issuance_manifest_event_hash": manifest_event["event_hash"],
                "prediction_event_hash": manifest_event["prediction_event_hash"],
                "projection_hash": manifest_event["projection_hash"],
                "comment_id": comment_id,
                "author_login": refetched.get("user", {}).get("login", _PUBLICATION_AUTHOR_LOGIN),
                "published_at": refetched["created_at"],
                "first_observed_at": now.isoformat(),
                "source_url": f"https://api.github.com/repos/{_PUBLICATION_REPOSITORY}/issues/comments/{comment_id}",
                "source_html_url": f"https://github.com/{_PUBLICATION_REPOSITORY}/pull/{_PUBLICATION_PULL_REQUEST}#issuecomment-{comment_id}",
                "source_sha256": sha256(source_raw).hexdigest(),
                "source_size_bytes": len(source_raw),
                "attestation_sha256": sha256(body.encode("utf-8")).hexdigest(),
                "publication_status": (
                    "INDEPENDENT_GITHUB_PUBLICATION_BEFORE_HORIZON"
                    if eligible
                    else "HISTORICAL_PUBLICATION_NOT_FORWARD_OOS"
                ),
                "forward_oos_eligible": eligible,
                "previous_hash": previous_hash,
                "market_validation_claimed": False,
                "live_trading_enabled": False,
                "order_placement_allowed": False,
            }
            receipt_event["event_hash"] = sha256(_canonical(receipt_event)).hexdigest()

            try:
                flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0)
                desc = os.open(receipt_ledger_path, flags, 0o600)
                with os.fdopen(desc, "ab") as rf:
                    rf.write(_canonical(receipt_event) + b"\n")
                    rf.flush()
                    os.fsync(rf.fileno())
            except Exception as exc:
                receipt_event["forward_oos_eligible"] = False
                raise MaturityObservationError("RECEIPT_PERSISTENCE_FAILED") from exc

        finally:
            pending_path.unlink(missing_ok=True)

    return receipt_event
