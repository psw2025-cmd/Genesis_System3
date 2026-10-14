#!/usr/bin/env python3
"""Capture official NSE evidence and issue one same-session PAPER forecast.

The command is deliberately narrow: it may run only after the requested cash
session has closed, captures exact official bytes, and atomically registers the
prediction/projection pair before its future horizon.  It never calls a broker.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from hashlib import sha256
from http.cookiejar import CookieJar
import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import (
    HTTPCookieProcessor,
    Request,
    build_opener,
)

from dashboard.backend.multibagger_outcome import (
    build_directional_outcome_projection,
)
from scripts.equity_directional_maturity import (
    _validated_github_publication_comment,
    publish_prospective_issuance,
    read_issuance_artifact_manifest,
)
from scripts.equity_forward_prediction import (
    HOLIDAY_URL,
    INDEX_API_URL,
    INDEX_URL_PREFIX,
    IST,
    _due_session,
    build_prediction,
)
from scripts.equity_instrument_scope import EQUITY_URL, ETF_URL
from scripts.equity_observation_packet import CM_URL


TASK_ID = "EQ-FORWARD-040"
SOURCE_ATTEMPT_TASK_ID = "EQ-SOURCE-039"
SOURCE_ATTEMPT_SCHEMA = "nse-equity-source-availability-attempt-v1"
REMOTE_NAMESPACE_TASK_ID = "EQ-RECOVERY-040"
REMOTE_NAMESPACE_SCHEMA = "equity-remote-namespace-attempt-v1"
_PUBLICATION_BODY_PREFIX = "GENESIS_SYSTEM3_EQUITY_PUBLICATION_V1\n"
_PUBLICATION_REPOSITORY = "psw2025-cmd/Genesis_System3"
_PUBLICATION_PULL_REQUEST = 471
_PUBLICATION_PAGE_SIZE = 100
_PUBLICATION_MAX_PAGES = 20
_PUBLICATION_MAX_MATCHES = 32
_MAX_PUBLICATION_RESPONSE_BYTES = 2 * 1024 * 1024
SOURCE_ROLES = frozenset(
    {"cash", "company", "etf", "actions", "holiday_calendar", "index"}
)
MAX_SOURCE_BYTES = 32 * 1024 * 1024
MODEL_SPEC_URI = (
    "research/evidence/equity/raw/2026-10-01-forward/"
    "equity_forward_rank_v1.json"
)
ISSUANCE_MANIFEST_URI = (
    "research/forward/equity/2026-10-01/"
    "equity_issuance_artifact_manifest.ndjson"
)
_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"
)


@dataclass(frozen=True)
class Capture:
    raw: bytes
    receipt: dict[str, Any]


class OfficialSourceUnavailable(ValueError):
    """Carry the exact failed official response to the durable boundary."""

    def __init__(self, role: str, capture: Capture):
        super().__init__(
            "Official source was not captured exactly: "
            f"{capture.receipt.get('url')}"
        )
        self.role = role
        self.capture = capture


class RemotePredictionIdentityOccupied(ValueError):
    """The immutable GitHub namespace already contains this prediction ID."""

    def __init__(self, record: dict[str, Any]):
        super().__init__(
            "Remote prediction identity already exists; no forecast issued: "
            f"{record.get('prediction_id')}"
        )
        self.record = record


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _bounded_read(handle: Any) -> bytes:
    raw = handle.read(MAX_SOURCE_BYTES + 1)
    if len(raw) > MAX_SOURCE_BYTES:
        raise ValueError("Official source exceeds the capture bound")
    return raw


def _source_opener() -> Any:
    return build_opener(HTTPCookieProcessor(CookieJar()))


def _fetch(url: str, *, opener: Any | None = None) -> Capture:
    """Return exact response bytes and a bounded timestamped receipt."""
    client = opener or _source_opener()
    started = _utc_now()
    request = Request(
        url,
        headers={
            "Accept": "application/json,text/csv,application/zip,*/*;q=0.8",
            "Referer": "https://www.nseindia.com/",
            "User-Agent": _USER_AGENT,
        },
    )
    try:
        with client.open(request, timeout=45) as response:
            raw = _bounded_read(response)
            observed = _utc_now()
            receipt = {
                "url": url,
                "request_started_at": started.isoformat(),
                "http_status": response.status,
                "final_url": response.geturl(),
                "content_type": response.headers.get("Content-Type"),
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
                "first_observed_at": observed.isoformat(),
                "raw_sha256": sha256(raw).hexdigest(),
                "bytes": len(raw),
            }
    except HTTPError as exc:
        raw = _bounded_read(exc)
        observed = _utc_now()
        receipt = {
            "url": url,
            "request_started_at": started.isoformat(),
            "http_status": exc.code,
            "final_url": exc.geturl(),
            "content_type": exc.headers.get("Content-Type"),
            "etag": exc.headers.get("ETag"),
            "last_modified": exc.headers.get("Last-Modified"),
            "first_observed_at": observed.isoformat(),
            "raw_sha256": sha256(raw).hexdigest(),
            "bytes": len(raw),
        }
    except (URLError, TimeoutError, OSError) as exc:
        raise ValueError(f"Official source request failed: {url}") from exc
    return Capture(raw=raw, receipt=receipt)


def _require_success(
    capture: Capture, *, url: str, role: str = "unknown"
) -> None:
    receipt = capture.receipt
    if (
        receipt["url"] != url
        or receipt["final_url"] != url
        or receipt["http_status"] != 200
        or receipt["raw_sha256"] != sha256(capture.raw).hexdigest()
        or receipt["bytes"] != len(capture.raw)
        or not capture.raw
    ):
        raise OfficialSourceUnavailable(role, capture)


def _safe_path(root: Path, relative_uri: str) -> Path:
    if not relative_uri or relative_uri.startswith(("/", "\\")):
        raise ValueError("Evidence path must be repository-relative")
    destination = (root / relative_uri).resolve(strict=False)
    try:
        destination.relative_to(root)
    except ValueError as exc:
        raise ValueError("Evidence path escapes the repository") from exc
    return destination


def _write_exclusive(root: Path, relative_uri: str, raw: bytes) -> None:
    destination = _safe_path(root, relative_uri)
    destination.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            destination.unlink()
        except OSError:
            pass
        raise


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _retain_source_unavailability(
    root: Path, entry: date, failure: OfficialSourceUnavailable
) -> dict[str, Any]:
    """Retain one immutable failed response without creating a forecast.

    The attempt is intentionally separate from the resumable successful-source
    packet.  A later successful capture cannot rewrite or silently promote it.
    """
    capture = failure.capture
    receipt = capture.receipt
    observed = datetime.fromisoformat(
        str(receipt.get("first_observed_at", "")).replace("Z", "+00:00")
    )
    if observed.tzinfo is None or observed.utcoffset() is None:
        raise ValueError("Failed-source observation requires a timezone")
    observed = observed.astimezone(timezone.utc)
    digest = sha256(capture.raw).hexdigest()
    if (
        failure.role not in SOURCE_ROLES
        or receipt.get("raw_sha256") != digest
        or receipt.get("bytes") != len(capture.raw)
        or not isinstance(receipt.get("http_status"), int)
    ):
        raise ValueError("Failed-source response or receipt is invalid")
    stamp = observed.strftime("%Y%m%dT%H%M%S%fZ")
    stem = f"{stamp}_{failure.role}_{digest[:16]}"
    attempt_dir = (
        f"research/evidence/equity/raw/{entry.isoformat()}-forward/"
        "availability_attempts"
    )
    response_uri = f"{attempt_dir}/{stem}.response"
    record_uri = f"{attempt_dir}/{stem}.json"
    record = {
        "schema_version": SOURCE_ATTEMPT_SCHEMA,
        "task_id": SOURCE_ATTEMPT_TASK_ID,
        "entry_date": entry.isoformat(),
        "source_role": failure.role,
        "availability_status": "OFFICIAL_SOURCE_UNAVAILABLE_NOT_ISSUED",
        "response_uri": response_uri,
        "response_sha256": digest,
        "response_bytes": len(capture.raw),
        "receipt": receipt,
        "forecast_issued": False,
        "market_validation_claimed": False,
        "live_trading_enabled": False,
        "orders_allowed": False,
    }
    record["record_hash"] = sha256(
        json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    response_path = _safe_path(root, response_uri)
    record_path = _safe_path(root, record_uri)
    try:
        _write_exclusive(root, response_uri, capture.raw)
        _write_exclusive(root, record_uri, _json_bytes(record))
    except Exception:
        for path in (record_path, response_path):
            try:
                path.unlink()
            except OSError:
                pass
        raise
    return record


def _strict_json(raw: bytes, *, label: str) -> Any:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"{label} contains duplicate JSON keys")
            value[key] = item
        return value

    try:
        return json.loads(raw, object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid JSON") from exc


def _fetch_publication_json(
    url: str, *, opener: Any | None = None
) -> Capture:
    """Fetch one bounded public GitHub JSON response without credentials."""
    client = opener or _source_opener()
    started = _utc_now()
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Genesis-System3-equity-namespace-v1",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with client.open(request, timeout=30) as response:
            raw = response.read(_MAX_PUBLICATION_RESPONSE_BYTES + 1)
            observed = _utc_now()
            receipt = {
                "url": url,
                "request_started_at": started.isoformat(),
                "http_status": response.status,
                "final_url": response.geturl(),
                "content_type": response.headers.get("Content-Type"),
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
                "first_observed_at": observed.isoformat(),
                "raw_sha256": sha256(raw).hexdigest(),
                "bytes": len(raw),
            }
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise ValueError("GitHub publication namespace request failed") from exc
    media_type = str(receipt["content_type"] or "").split(";", 1)[0]
    if (
        receipt["http_status"] != 200
        or receipt["final_url"] != url
        or media_type.strip().lower() != "application/json"
        or not raw
        or len(raw) > _MAX_PUBLICATION_RESPONSE_BYTES
    ):
        raise ValueError("GitHub publication namespace response is invalid")
    _strict_json(raw, label="GitHub publication namespace response")
    return Capture(raw=raw, receipt=receipt)


def _publication_comment_page_url(page: int) -> str:
    if page <= 0 or page > _PUBLICATION_MAX_PAGES:
        raise ValueError("GitHub publication page is outside the bound")
    return (
        "https://api.github.com/repos/"
        f"{_PUBLICATION_REPOSITORY}/issues/"
        f"{_PUBLICATION_PULL_REQUEST}/comments"
        f"?per_page={_PUBLICATION_PAGE_SIZE}&page={page}"
    )


def _scan_remote_prediction_identity(
    prediction_id: str, *, opener: Any | None = None
) -> list[Capture]:
    """Return exact authoritative comments already using prediction_id."""
    matches: list[tuple[int, dict[str, Any]]] = []
    seen_ids: set[int] = set()
    for page in range(1, _PUBLICATION_MAX_PAGES + 1):
        capture = _fetch_publication_json(
            _publication_comment_page_url(page), opener=opener
        )
        rows = _strict_json(
            capture.raw, label="GitHub publication comment page"
        )
        if not isinstance(rows, list) or len(rows) > _PUBLICATION_PAGE_SIZE:
            raise ValueError("GitHub publication comment page is invalid")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("GitHub publication comment is invalid")
            user = row.get("user")
            body = row.get("body")
            if (
                not isinstance(user, dict)
                or user.get("login") != "psw2025-cmd"
                or row.get("author_association") != "OWNER"
                or not isinstance(body, str)
                or not body.startswith(_PUBLICATION_BODY_PREFIX)
            ):
                continue
            comment_id, _, attestation = (
                _validated_github_publication_comment(row)
            )
            if comment_id in seen_ids:
                raise ValueError("GitHub publication comment is duplicated")
            seen_ids.add(comment_id)
            if attestation["prediction_id"] == prediction_id:
                matches.append((comment_id, attestation))
        if len(rows) < _PUBLICATION_PAGE_SIZE:
            break
    else:
        raise ValueError("GitHub publication namespace scan is incomplete")
    if len(matches) > _PUBLICATION_MAX_MATCHES:
        raise ValueError("GitHub publication identity match bound exceeded")
    exact: list[Capture] = []
    for comment_id, expected_attestation in matches:
        url = (
            "https://api.github.com/repos/"
            f"{_PUBLICATION_REPOSITORY}/issues/comments/{comment_id}"
        )
        capture = _fetch_publication_json(url, opener=opener)
        source = _strict_json(
            capture.raw, label="GitHub publication comment"
        )
        if not isinstance(source, dict):
            raise ValueError("GitHub publication comment is invalid")
        fetched_id, _, fetched_attestation = (
            _validated_github_publication_comment(source)
        )
        if (
            fetched_id != comment_id
            or fetched_attestation != expected_attestation
        ):
            raise ValueError("GitHub publication comment changed during scan")
        exact.append(capture)
    return exact


def _retain_remote_namespace_attempt(
    root: Path,
    entry: date,
    prediction: dict[str, Any],
    projection: dict[str, Any],
    captures: list[Capture],
) -> dict[str, Any]:
    if not captures:
        raise ValueError("Remote namespace attempt requires a match")
    comments = []
    snapshot_rows = []
    for capture in captures:
        source = _strict_json(
            capture.raw, label="GitHub publication comment"
        )
        if not isinstance(source, dict):
            raise ValueError("GitHub publication comment is invalid")
        comment_id, published, attestation = (
            _validated_github_publication_comment(source)
        )
        if attestation["prediction_id"] != prediction["prediction_id"]:
            raise ValueError("Remote prediction identity does not match")
        comments.append(
            {
                "comment_id": comment_id,
                "published_at": published.isoformat(),
                "source_url": capture.receipt["url"],
                "source_sha256": capture.receipt["raw_sha256"],
                "source_bytes": capture.receipt["bytes"],
                "receipt": capture.receipt,
                "attestation": attestation,
            }
        )
        snapshot_rows.append((comment_id, capture))
    comments.sort(key=lambda row: row["comment_id"])
    exact_artifact_match = all(
        row["attestation"]["prediction_event_hash"]
        == prediction["event_hash"]
        and row["attestation"]["projection_hash"]
        == projection["projection_hash"]
        for row in comments
    )
    observed = max(
        datetime.fromisoformat(
            str(row["receipt"]["first_observed_at"]).replace("Z", "+00:00")
        ).astimezone(timezone.utc)
        for row in comments
    )
    stamp = observed.strftime("%Y%m%dT%H%M%S%fZ")
    base_uri = (
        f"research/evidence/equity/raw/{entry.isoformat()}-forward/"
        "remote_namespace_attempts"
    )
    written: list[Path] = []
    snapshot_uris: dict[int, str] = {}
    try:
        for comment_id, capture in snapshot_rows:
            digest = sha256(capture.raw).hexdigest()
            uri = (
                f"{base_uri}/{stamp}_comment_{comment_id}_"
                f"{digest[:16]}.json"
            )
            _write_exclusive(root, uri, capture.raw)
            written.append(_safe_path(root, uri))
            snapshot_uris[comment_id] = uri
        for row in comments:
            row["snapshot_uri"] = snapshot_uris[row["comment_id"]]
        status = (
            "REMOTE_PREDICTION_ID_EXISTS_NOT_REISSUED"
            if exact_artifact_match and len(comments) == 1
            else "REMOTE_PREDICTION_ID_COLLISION_NOT_ISSUED"
        )
        record = {
            "schema_version": REMOTE_NAMESPACE_SCHEMA,
            "task_id": REMOTE_NAMESPACE_TASK_ID,
            "entry_date": entry.isoformat(),
            "prediction_id": prediction["prediction_id"],
            "observed_at": observed.isoformat(),
            "remote_identity_status": status,
            "remote_comment_count": len(comments),
            "remote_comments": comments,
            "proposed_prediction_event_hash": prediction["event_hash"],
            "proposed_projection_hash": projection["projection_hash"],
            "proposed_due_at": prediction["due_at"],
            "proposed_counts": prediction["counts"],
            "forecast_issued": False,
            "retained_prediction_count": 0,
            "effective_forward_oos_eligible_count": 0,
            "market_validation_claimed": False,
            "performance_metrics_available": False,
            "real_money_ready": False,
            "live_trading_enabled": False,
            "orders_allowed": False,
        }
        record["record_hash"] = sha256(
            json.dumps(
                record,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        record_uri = (
            f"{base_uri}/{stamp}_{prediction['prediction_id']}_"
            f"{record['record_hash'][:16]}.json"
        )
        _write_exclusive(root, record_uri, _json_bytes(record))
        written.append(_safe_path(root, record_uri))
    except Exception:
        for path in reversed(written):
            try:
                path.unlink()
            except OSError:
                pass
        raise
    return record


def _guard_remote_prediction_identity(
    root: Path,
    entry: date,
    prediction: dict[str, Any],
    projection: dict[str, Any],
    *,
    opener: Any | None = None,
) -> None:
    captures = _scan_remote_prediction_identity(
        prediction["prediction_id"], opener=opener
    )
    if captures:
        record = _retain_remote_namespace_attempt(
            root, entry, prediction, projection, captures
        )
        raise RemotePredictionIdentityOccupied(record)


def _capture_sources(entry: date) -> tuple[
    dict[str, Capture], list[dict[str, Any]], date
]:
    opener = _source_opener()
    holiday = _fetch(HOLIDAY_URL, opener=opener)
    _require_success(
        holiday, url=HOLIDAY_URL, role="holiday_calendar"
    )
    due, _ = _due_session(
        holiday.raw,
        holiday.receipt,
        entry=entry,
        calendar_days=7,
    )
    stamp = entry.strftime("%Y%m%d")
    cash_url = (
        CM_URL + f"BhavCopy_NSE_CM_0_0_0_{stamp}_F_0000.csv.zip"
    )
    action_url = (
        "https://www.nseindia.com/api/corporates-corporateActions"
        f"?index=equities&from_date={entry.strftime('%d-%m-%Y')}"
        f"&to_date={due.strftime('%d-%m-%Y')}"
    )
    captures = {"holiday_calendar": holiday}
    for role, url in (
        ("cash", cash_url),
        ("company", EQUITY_URL),
        ("etf", ETF_URL),
        ("actions", action_url),
    ):
        capture = _fetch(url, opener=opener)
        _require_success(capture, url=url, role=role)
        captures[role] = capture

    archive_index_url = (
        f"{INDEX_URL_PREFIX}{entry.strftime('%d%m%Y')}.csv"
    )
    archive_probe = _fetch(archive_index_url, opener=opener)
    attempts = [
        {
            "role": "index_archive_probe",
            "retained_file": None,
            **archive_probe.receipt,
        }
    ]
    if archive_probe.receipt["http_status"] == 200:
        _require_success(
            archive_probe, url=archive_index_url, role="index"
        )
        captures["index"] = archive_probe
    elif archive_probe.receipt["http_status"] == 404:
        fallback = _fetch(INDEX_API_URL, opener=opener)
        _require_success(fallback, url=INDEX_API_URL, role="index")
        captures["index"] = fallback
    else:
        raise OfficialSourceUnavailable("index", archive_probe)
    return captures, attempts, due


def _load_captured_sources(
    root: Path, entry: date
) -> tuple[dict[str, Capture], list[dict[str, Any]], date] | None:
    """Resume only from a complete, byte-verified prior capture."""
    raw_dir = f"research/evidence/equity/raw/{entry.isoformat()}-forward"
    receipt_path = _safe_path(root, f"{raw_dir}/capture_receipts.json")
    if not receipt_path.exists():
        return None
    try:
        rows = json.loads(receipt_path.read_bytes())
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError("Retained capture receipt is unreadable") from exc
    if not isinstance(rows, list):
        raise ValueError("Retained capture receipt is not a list")
    captures: dict[str, Capture] = {}
    attempts = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Retained capture receipt row is invalid")
        role = row.get("role")
        if role == "index_archive_probe":
            attempts.append(row)
            continue
        retained_file = row.get("retained_file")
        if role not in {
            "cash",
            "company",
            "etf",
            "actions",
            "holiday_calendar",
            "index",
        } or not isinstance(retained_file, str):
            raise ValueError("Retained capture role is invalid")
        receipt = {
            key: value
            for key, value in row.items()
            if key not in {"role", "retained_file"}
        }
        raw = _safe_path(root, f"{raw_dir}/{retained_file}").read_bytes()
        capture = Capture(raw=raw, receipt=receipt)
        _require_success(capture, url=receipt["url"])
        if role in captures:
            raise ValueError("Retained capture role is duplicated")
        captures[role] = capture
    if set(captures) != {
        "cash",
        "company",
        "etf",
        "actions",
        "holiday_calendar",
        "index",
    } or len(attempts) != 1:
        raise ValueError("Retained capture set is incomplete")
    due, _ = _due_session(
        captures["holiday_calendar"].raw,
        captures["holiday_calendar"].receipt,
        entry=entry,
        calendar_days=7,
    )
    return captures, attempts, due


def issue(entry: date, *, evidence_root: Path) -> dict[str, Any]:
    """Capture, seal, and register one future-horizon PAPER prediction."""
    root = evidence_root.resolve(strict=True)
    now = _utc_now()
    local_now = now.astimezone(IST)
    if entry != local_now.date() or local_now.time() < time(15, 30):
        raise ValueError("Issuance requires today's completed NSE cash session")

    raw_dir = f"research/evidence/equity/raw/{entry.isoformat()}-forward"
    retained = _load_captured_sources(root, entry)
    if retained is None:
        try:
            captures, attempts, due = _capture_sources(entry)
        except OfficialSourceUnavailable as failure:
            _retain_source_unavailability(root, entry, failure)
            raise
    else:
        captures, attempts, due = retained
    filenames = {
        "cash": f"cm_{entry.strftime('%Y%m%d')}.zip",
        "company": "EQUITY_L.csv",
        "etf": "eq_etfseclist.csv",
        "actions": "corporate_actions.json",
        "holiday_calendar": "trading_holidays.json",
        "index": (
            f"index_close_{entry.strftime('%Y%m%d')}.csv"
            if captures["index"].receipt["url"] != INDEX_API_URL
            else f"all_indices_{entry.strftime('%Y%m%d')}.json"
        ),
    }
    if retained is None:
        for role, filename in filenames.items():
            _write_exclusive(
                root, f"{raw_dir}/{filename}", captures[role].raw
            )

        receipts = []
        for role in sorted(captures):
            receipts.append(
                {
                    "role": role,
                    "retained_file": filenames[role],
                    **captures[role].receipt,
                }
            )
        receipts.extend(attempts)
        _write_exclusive(
            root,
            f"{raw_dir}/capture_receipts.json",
            _json_bytes(receipts),
        )

    model_raw = _safe_path(root, MODEL_SPEC_URI).read_bytes()
    manifest_path = _safe_path(root, ISSUANCE_MANIFEST_URI)
    prior_events = read_issuance_artifact_manifest(
        ISSUANCE_MANIFEST_URI,
        evidence_root=root,
    )
    previous_event_hash = (
        prior_events[-1]["prediction_event_hash"]
        if prior_events
        else "0" * 64
    )
    issued = _utc_now()
    equity_sources = {
        role: captures[role].raw
        for role in ("cash", "company", "etf", "actions")
    }
    equity_receipts = {
        role: captures[role].receipt
        for role in ("cash", "company", "etf", "actions")
    }
    prediction = build_prediction(
        equity_sources=equity_sources,
        equity_receipts=equity_receipts,
        index_raw=captures["index"].raw,
        index_receipt=captures["index"].receipt,
        holiday_raw=captures["holiday_calendar"].raw,
        holiday_receipt=captures["holiday_calendar"].receipt,
        model_spec_raw=model_raw,
        issued_at=issued.isoformat(),
        previous_event_hash=previous_event_hash,
        now=issued,
    )
    retained_uris = {
        role: f"{raw_dir}/{filenames[role]}"
        for role in filenames
    }
    retained_uris["model_spec"] = MODEL_SPEC_URI
    projection = build_directional_outcome_projection(
        prediction,
        equity_source_bytes=equity_sources,
        index_source_raw=captures["index"].raw,
        holiday_calendar_raw=captures["holiday_calendar"].raw,
        model_spec_raw=model_raw,
        expected_previous_event_hash=previous_event_hash,
        retained_source_uris=retained_uris,
        now=issued,
    )
    _guard_remote_prediction_identity(
        root, entry, prediction, projection
    )
    forecast_dir = f"research/forward/equity/{entry.isoformat()}"
    prediction_uri = (
        f"{forecast_dir}/{entry.isoformat()}_equity_forward_prediction.json"
    )
    projection_uri = (
        f"{forecast_dir}/{due.isoformat()}_equity_directional_projection.json"
    )
    _safe_path(root, forecast_dir).mkdir(parents=True, exist_ok=True)
    manifest_event = publish_prospective_issuance(
        manifest_path,
        prediction_bytes=_json_bytes(prediction),
        projection_bytes=_json_bytes(projection),
        prediction_uri=prediction_uri,
        projection_uri=projection_uri,
        evidence_root=root,
    )
    return {
        "task_id": TASK_ID,
        "execution_mode": "ANALYZE_PAPER",
        "prediction_id": prediction["prediction_id"],
        "issued_at": prediction["issued_at"],
        "source_cutoff_at": prediction["source_cutoff_at"],
        "due_at": prediction["due_at"],
        "symbol": prediction["prediction"]["symbol"],
        "isin": prediction["prediction"]["isin"],
        "entry_reference_close": prediction["prediction"][
            "entry_reference_close"
        ],
        "benchmark_reference_close": prediction["benchmark"][
            "entry_reference_close"
        ],
        "counts": prediction["counts"],
        "prediction_event_hash": prediction["event_hash"],
        "projection_hash": projection["projection_hash"],
        "issuance_manifest_event_hash": manifest_event["event_hash"],
        "index_source_url": captures["index"].receipt["url"],
        "archive_index_probe_status": attempts[0]["http_status"],
        "market_validation_claimed": False,
        "live_trading_enabled": False,
        "orders_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Issue a source-qualified equity PAPER prediction"
    )
    parser.add_argument("--entry-date", required=True)
    parser.add_argument("--evidence-root", default=".")
    args = parser.parse_args()
    result = issue(
        date.fromisoformat(args.entry_date),
        evidence_root=Path(args.evidence_root),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
