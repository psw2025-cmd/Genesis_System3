"""Append-only, hash-chained equity forecast ledger.

The ledger records what the model issued before an outcome existed. It does not
fetch market data, evaluate alpha, or place broker orders.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
from math import isfinite
import os
from pathlib import Path
import re
import stat
from typing import Any, Iterable, Iterator


SCHEMA_VERSION = "equity-forecast-ledger-v2"
GENESIS_HASH = "0" * 64
_APPROVED_SOURCES = {"NSE", "BSE", "DHAN"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SNAPSHOT_REF_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
_SNAPSHOT_PREFIXES = ("snapshots/", "research/evidence/")


class LedgerError(ValueError):
    """Raised when a record cannot be trusted as an issued forecast."""


def _timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise LedgerError(f"{field}_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LedgerError(f"{field}_INVALID") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LedgerError(f"{field}_TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _sha256(value: Any, field: str) -> str:
    digest = str(value).strip().lower()
    if not _SHA256_RE.fullmatch(digest):
        raise LedgerError(f"{field}_INVALID_SHA256")
    return digest


def _verified_snapshot_bytes(value: Any, digest: str, field: str) -> bytes:
    if not isinstance(value, bytes) or not value:
        raise LedgerError(f"{field}_SNAPSHOT_REQUIRED")
    if sha256(value).hexdigest() != digest:
        raise LedgerError(f"{field}_SNAPSHOT_HASH_MISMATCH")
    return value


def _snapshot_reference(value: Any, field: str) -> str:
    """Accept only repository-style references to retained immutable bytes."""
    if not isinstance(value, str) or not value:
        raise LedgerError(f"{field}_REQUIRED")
    if value != value.strip():
        raise LedgerError(f"{field}_INVALID")
    if len(value) > 512 or not _SNAPSHOT_REF_RE.fullmatch(value):
        raise LedgerError(f"{field}_INVALID")
    segments = value.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise LedgerError(f"{field}_INVALID")
    if not value.startswith(_SNAPSHOT_PREFIXES):
        raise LedgerError(f"{field}_UNAPPROVED_PREFIX")
    return value


def _finite_number(value: Any, field: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise LedgerError(f"{field}_INVALID")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise LedgerError(f"{field}_INVALID") from exc
    if not isfinite(number) or (positive and number <= 0):
        raise LedgerError(f"{field}_INVALID")
    return number


def _canonical(record: dict[str, Any]) -> bytes:
    payload = {key: value for key, value in record.items() if key != "event_hash"}
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def build_issued_forecast(
    forecast: dict[str, Any],
    *,
    previous_hash: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build an unpersisted event against an explicit trusted chain anchor.

    ``append_issued_forecast`` derives that anchor while holding the ledger lock.
    Direct callers must make the genesis decision explicit instead of silently
    starting a second valid-looking chain when predecessor state is unavailable.
    """
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise LedgerError("NOW_TIMEZONE_REQUIRED")
    current = current.astimezone(timezone.utc)

    issued = _timestamp(forecast.get("issued_at"), "ISSUED_AT")
    due = _timestamp(forecast.get("due_at"), "DUE_AT")
    observed = _timestamp(forecast.get("entry_observed_at"), "ENTRY_OBSERVED_AT")
    adjustment_observed = _timestamp(
        forecast.get("adjustment_observed_at"),
        "ADJUSTMENT_OBSERVED_AT",
    )
    if not observed <= issued <= current < due:
        raise LedgerError("INVALID_FORECAST_TIME_ORDER")
    if adjustment_observed > issued:
        raise LedgerError("ADJUSTMENT_LOOKAHEAD_FORBIDDEN")

    prediction_id = str(forecast.get("prediction_id", "")).strip()
    symbol = str(forecast.get("symbol", "")).strip().upper()
    model_name = str(forecast.get("model_name", "")).strip()
    model_version = str(forecast.get("model_version", "")).strip()
    snapshot_uri = _snapshot_reference(
        forecast.get("entry_snapshot_uri"),
        "ENTRY_SNAPSHOT_URI",
    )
    adjustment_basis = str(forecast.get("adjustment_basis", "")).strip()
    adjustment_snapshot_uri = _snapshot_reference(
        forecast.get("adjustment_snapshot_uri"),
        "ADJUSTMENT_SNAPSHOT_URI",
    )
    if not prediction_id:
        raise LedgerError("PREDICTION_ID_REQUIRED")
    if not symbol:
        raise LedgerError("SYMBOL_REQUIRED")
    if not model_name or not model_version:
        raise LedgerError("MODEL_IDENTITY_REQUIRED")
    if not adjustment_basis:
        raise LedgerError("ADJUSTMENT_BASIS_REQUIRED")

    source = str(forecast.get("entry_source", "")).strip().upper()
    if source not in _APPROVED_SOURCES:
        raise LedgerError("ENTRY_SOURCE_UNVERIFIED")
    adjustment_source = str(
        forecast.get("adjustment_source", "")
    ).strip().upper()
    if adjustment_source not in _APPROVED_SOURCES:
        raise LedgerError("ADJUSTMENT_SOURCE_UNVERIFIED")

    horizon_days = forecast.get("horizon_days")
    if isinstance(horizon_days, bool) or not isinstance(horizon_days, int):
        raise LedgerError("HORIZON_DAYS_INVALID")
    if horizon_days <= 0 or horizon_days > 730:
        raise LedgerError("HORIZON_DAYS_INVALID")
    elapsed_days = (due - issued).total_seconds() / 86400
    if abs(elapsed_days - horizon_days) > 1:
        raise LedgerError("HORIZON_DUE_MISMATCH")

    entry_source_hash = _sha256(
        forecast.get("entry_source_hash"),
        "ENTRY_SOURCE_HASH",
    )
    entry_source_snapshot = _verified_snapshot_bytes(
        forecast.get("entry_source_snapshot"),
        entry_source_hash,
        "ENTRY_SOURCE",
    )
    adjustment_source_hash = _sha256(
        forecast.get("adjustment_source_hash"),
        "ADJUSTMENT_SOURCE_HASH",
    )
    adjustment_source_snapshot = _verified_snapshot_bytes(
        forecast.get("adjustment_source_snapshot"),
        adjustment_source_hash,
        "ADJUSTMENT_SOURCE",
    )

    sealed = {
        "schema_version": SCHEMA_VERSION,
        "event_type": "EQUITY_FORECAST_ISSUED",
        "prediction_id": prediction_id,
        "symbol": symbol,
        "horizon_days": horizon_days,
        "issued_at": issued.isoformat(),
        "due_at": due.isoformat(),
        "entry_observed_at": observed.isoformat(),
        "adjustment_observed_at": adjustment_observed.isoformat(),
        "entry_adjusted_close": _finite_number(
            forecast.get("entry_adjusted_close"),
            "ENTRY_ADJUSTED_CLOSE",
            positive=True,
        ),
        "predicted_return_pct": _finite_number(
            forecast.get("predicted_return_pct"),
            "PREDICTED_RETURN_PCT",
        ),
        "model_name": model_name,
        "model_version": model_version,
        "feature_hash": _sha256(forecast.get("feature_hash"), "FEATURE_HASH"),
        "entry_source": source,
        "entry_source_hash": entry_source_hash,
        "entry_source_size_bytes": len(entry_source_snapshot),
        "entry_snapshot_uri": snapshot_uri,
        "adjustment_basis": adjustment_basis,
        "adjustment_source": adjustment_source,
        "adjustment_source_hash": adjustment_source_hash,
        "adjustment_source_size_bytes": len(adjustment_source_snapshot),
        "adjustment_snapshot_uri": adjustment_snapshot_uri,
        "previous_hash": _sha256(previous_hash, "PREVIOUS_HASH"),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    sealed["event_hash"] = sha256(_canonical(sealed)).hexdigest()
    return sealed


def verify_chain(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Verify ordering, uniqueness and every content hash in a ledger."""
    previous = GENESIS_HASH
    seen: set[str] = set()
    count = 0
    for index, record in enumerate(records):
        if record.get("schema_version") != SCHEMA_VERSION:
            raise LedgerError(f"ROW_{index}_SCHEMA_INVALID")
        if record.get("event_type") != "EQUITY_FORECAST_ISSUED":
            raise LedgerError(f"ROW_{index}_EVENT_TYPE_INVALID")
        prediction_id = str(record.get("prediction_id", "")).strip()
        if not prediction_id or prediction_id in seen:
            raise LedgerError(f"ROW_{index}_PREDICTION_ID_DUPLICATE")
        if record.get("previous_hash") != previous:
            raise LedgerError(f"ROW_{index}_CHAIN_BROKEN")
        expected = sha256(_canonical(record)).hexdigest()
        if record.get("event_hash") != expected:
            raise LedgerError(f"ROW_{index}_HASH_MISMATCH")
        if record.get("live_trading_enabled") is not False:
            raise LedgerError(f"ROW_{index}_LIVE_FLAG_INVALID")
        if record.get("order_placement_allowed") is not False:
            raise LedgerError(f"ROW_{index}_ORDER_FLAG_INVALID")
        seen.add(prediction_id)
        previous = expected
        count += 1
    return {
        "status": "VERIFIED" if count else "EMPTY",
        "verification_scope": "HASH_CHAIN_ONLY",
        "record_count": count,
        "head_hash": previous,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }


def _retained_snapshot_digest(root: Path, reference: str, field: str) -> tuple[str, int]:
    """Hash a regular retained file, rejecting links and replacement during read."""
    parts = _snapshot_reference(reference, f"{field}_SNAPSHOT_URI").split("/")

    def checked_path() -> Path:
        candidate = root
        for part in parts:
            candidate = candidate / part
            info = candidate.lstat()
            reparse = getattr(info, "st_file_attributes", 0) & getattr(
                stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0
            )
            if stat.S_ISLNK(info.st_mode) or reparse:
                raise LedgerError(f"{field}_RETAINED_LINK_FORBIDDEN")
        candidate.resolve(strict=True).relative_to(root)
        return candidate

    try:
        path = checked_path()
        before = path.stat()
        if not stat.S_ISREG(before.st_mode):
            raise LedgerError(f"{field}_RETAINED_NOT_REGULAR")
        flags = (
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
        )
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (
                opened.st_dev, opened.st_ino
            ):
                raise LedgerError(f"{field}_RETAINED_CHANGED_DURING_READ")
            digest = sha256()
            size = 0
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
                size += len(chunk)
            after = os.fstat(handle.fileno())
            retained = checked_path().stat()
            def identity(info: os.stat_result) -> tuple[int, ...]:
                return (
                    info.st_dev, info.st_ino, info.st_size,
                    info.st_mtime_ns, info.st_ctime_ns,
                )
            if identity(opened) != identity(after) or identity(after) != identity(retained):
                raise LedgerError(f"{field}_RETAINED_CHANGED_DURING_READ")
        return digest.hexdigest(), size
    except LedgerError:
        raise
    except (OSError, ValueError) as exc:
        raise LedgerError(f"{field}_RETAINED_UNAVAILABLE") from exc


def verify_retained_evidence(record: dict[str, Any], *, evidence_root: Path) -> None:
    """Recheck both source files under the caller's explicitly approved archive root.

    This proves byte retention at verification time, not exchange authenticity,
    publication timing, or permanent immutability of the underlying filesystem.
    """
    try:
        root = Path(evidence_root).resolve(strict=True)
        if not root.is_dir():
            raise LedgerError("EVIDENCE_ROOT_NOT_DIRECTORY")
    except (OSError, TypeError, ValueError) as exc:
        raise LedgerError("EVIDENCE_ROOT_UNAVAILABLE") from exc
    for source in ("entry", "adjustment"):
        field = source.upper()
        expected_hash = _sha256(record.get(f"{source}_source_hash"), f"{field}_SOURCE_HASH")
        expected_size = record.get(f"{source}_source_size_bytes")
        if isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size <= 0:
            raise LedgerError(f"{field}_RETAINED_SIZE_INVALID")
        digest, size = _retained_snapshot_digest(root, record.get(f"{source}_snapshot_uri"), field)
        if digest != expected_hash or size != expected_size:
            raise LedgerError(f"{field}_RETAINED_HASH_OR_SIZE_MISMATCH")


@contextmanager
def _ledger_lock(path: Path, *, exclusive: bool) -> Iterator[None]:
    """Hold a process-safe lock without deleting its stable lock inode.

    POSIX readers share the lock; Windows readers use the same exclusive byte
    lock as writers because the standard library exposes no shared equivalent.
    Keeping the lock file avoids an unlink/recreate race between processes.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    with lock_path.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt

            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            operation = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(handle.fileno(), operation)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _read_ledger_unlocked(path: Path, *, evidence_root: Path) -> list[dict[str, Any]]:
    """Load and verify NDJSON while the caller holds the ledger lock."""
    if not path.exists():
        return []
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise LedgerError("LEDGER_TRUNCATED")
    try:
        records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LedgerError("LEDGER_INVALID_JSON") from exc
    verify_chain(records)
    for record in records:
        verify_retained_evidence(record, evidence_root=evidence_root)
    return records


def read_ledger(path: Path, *, evidence_root: Path) -> list[dict[str, Any]]:
    """Verify the chain and retained bytes while excluding concurrent writers."""
    with _ledger_lock(path, exclusive=False):
        return _read_ledger_unlocked(path, evidence_root=evidence_root)


def append_issued_forecast(
    path: Path,
    forecast: dict[str, Any],
    *,
    evidence_root: Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Append one fsync'd forecast in a serialized read-build-write section."""
    with _ledger_lock(path, exclusive=True):
        records = _read_ledger_unlocked(path, evidence_root=evidence_root)
        prediction_id = str(forecast.get("prediction_id", "")).strip()
        if any(row["prediction_id"] == prediction_id for row in records):
            raise LedgerError("PREDICTION_ID_DUPLICATE")
        previous_hash = records[-1]["event_hash"] if records else GENESIS_HASH
        sealed = build_issued_forecast(
            forecast,
            previous_hash=previous_hash,
            now=now,
        )
        verify_retained_evidence(sealed, evidence_root=evidence_root)
        payload = json.dumps(
            sealed,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(payload + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        verify_chain([*records, sealed])
        return sealed
