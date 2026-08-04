"""
State store backend abstraction — provides a pluggable storage layer for
state/config artifacts used by live-readiness and gate logic.

Design goals
------------
* Code that reads/writes state files must NOT call ``open()`` / ``Path.write_text()``
  directly — use the StateStoreBackend interface instead.
* Local development uses the LocalFileBackend (identical behaviour to the
  previous direct-file approach — no behavioural change).
* Cloud Run deployments with ephemeral filesystems can swap in GCSBackend
  (or any other backend) by setting ``STATE_BACKEND=gcs`` and
  ``GCS_STATE_BUCKET=<bucket>`` in Cloud Run Variables & Secrets.
* The backend is selected once at import time and cached as a module-level
  singleton (``_backend``).  Call ``get_backend()`` to obtain it.

Thread safety: each backend implementation is responsible for its own
thread safety.  LocalFileBackend uses atomic write-then-rename so concurrent
reads are safe.

Usage example
-------------
    from dashboard.backend.state_store_backend import get_backend

    backend = get_backend()
    raw = backend.read("state/paper_trades.json")
    if raw is not None:
        data = json.loads(raw)
    backend.write("state/paper_trades.json", json.dumps(data, indent=2))
    exists = backend.exists("config/kill_switch.json")
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------


class StateStoreBackend(ABC):
    """Minimal key-value store interface for state/config blobs."""

    @abstractmethod
    def read(self, key: str) -> Optional[str]:
        """Return the UTF-8 text content for *key*, or ``None`` if missing."""

    @abstractmethod
    def write(self, key: str, content: str) -> None:
        """Persist *content* (UTF-8 text) under *key*."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Return True if *key* has stored content."""

    def read_json(self, key: str, default=None):
        """Convenience: read and JSON-parse *key*, returning *default* on miss/error."""
        raw = self.read(key)
        if raw is None:
            return default
        try:
            return json.loads(raw)
        except Exception:
            return default

    def write_json(self, key: str, obj) -> None:
        """Convenience: JSON-serialise *obj* and write to *key*."""
        self.write(key, json.dumps(obj, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Local-file backend (default — matches existing direct-file behaviour)
# ---------------------------------------------------------------------------


class LocalFileBackend(StateStoreBackend):
    """
    Stores blobs as files under *root_dir*.
    Keys are relative paths (e.g. ``"state/paper_trades.json"``).
    Writes are atomic: content is written to a temp file, then renamed.
    """

    def __init__(self, root_dir: Path) -> None:
        self._root = root_dir

    def _path(self, key: str) -> Path:
        # Normalise separators and prevent path traversal.
        parts = Path(key).parts
        safe_parts = [p for p in parts if p not in ("", "..", ".")]
        return self._root.joinpath(*safe_parts)

    def read(self, key: str) -> Optional[str]:
        p = self._path(key)
        if not p.exists():
            return None
        try:
            return p.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            logger.warning("LocalFileBackend.read(%s) failed: %s", key, exc)
            return None

    def write(self, key: str, content: str) -> None:
        p = self._path(key)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            # Atomic write via temp file in the same directory.
            fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".tmp_")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(content)
                os.replace(tmp, p)
            except Exception:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
                raise
        except Exception as exc:
            logger.error("LocalFileBackend.write(%s) failed: %s", key, exc)
            raise

    def exists(self, key: str) -> bool:
        return self._path(key).exists()


# ---------------------------------------------------------------------------
# GCS backend stub — swap in when STATE_BACKEND=gcs is set
# ---------------------------------------------------------------------------


class GCSBackend(StateStoreBackend):
    """
    Google Cloud Storage backend for Cloud Run deployments with ephemeral
    filesystems.

    Required env vars
    -----------------
    GCS_STATE_BUCKET  — GCS bucket name (e.g. ``genesis-system3-state``)

    Optional env vars
    -----------------
    GCS_STATE_PREFIX  — key prefix to prepend (default: ``"state/"``).
                        Useful when sharing a bucket across environments.

    Authentication is handled automatically via Application Default
    Credentials (ADC) — no explicit service-account JSON needed on Cloud Run.

    NOTE: ``google-cloud-storage`` is an *optional* dependency.  If it is not
    installed, importing this module succeeds but instantiating GCSBackend
    raises ``ImportError`` with a clear message.
    """

    def __init__(self) -> None:
        try:
            from google.cloud import storage  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "GCSBackend requires 'google-cloud-storage'. "
                "Install it with: pip install google-cloud-storage"
            ) from exc

        bucket_name = os.environ.get("GCS_STATE_BUCKET", "").strip()
        if not bucket_name:
            raise ValueError(
                "GCS_STATE_BUCKET env var is required when STATE_BACKEND=gcs"
            )
        self._prefix = os.environ.get("GCS_STATE_PREFIX", "state/").rstrip("/") + "/"
        client = storage.Client()
        self._bucket = client.bucket(bucket_name)
        logger.info("GCSBackend initialised: gs://%s/%s", bucket_name, self._prefix)

    def _blob_name(self, key: str) -> str:
        # Normalise key — strip leading slashes, prepend prefix.
        return self._prefix + key.lstrip("/")

    def read(self, key: str) -> Optional[str]:
        blob = self._bucket.blob(self._blob_name(key))
        try:
            return blob.download_as_text(encoding="utf-8")
        except Exception as exc:
            # 404 is expected (missing key); other errors are warnings.
            logger.debug("GCSBackend.read(%s): %s", key, exc)
            return None

    def write(self, key: str, content: str) -> None:
        blob = self._bucket.blob(self._blob_name(key))
        try:
            blob.upload_from_string(content, content_type="application/json")
        except Exception as exc:
            logger.error("GCSBackend.write(%s) failed: %s", key, exc)
            raise

    def exists(self, key: str) -> bool:
        blob = self._bucket.blob(self._blob_name(key))
        try:
            return blob.exists()
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Factory / singleton
# ---------------------------------------------------------------------------

_backend: Optional[StateStoreBackend] = None


def get_backend(root_dir: Optional[Path] = None) -> StateStoreBackend:
    """
    Return the process-level singleton StateStoreBackend.

    Backend selection (controlled by ``STATE_BACKEND`` env var):
    * ``"local"`` (default) — LocalFileBackend rooted at *root_dir* (or the
      repository root derived from this file's location when not supplied).
    * ``"gcs"`` — GCSBackend; requires ``GCS_STATE_BUCKET`` env var.

    Subsequent calls return the cached singleton regardless of arguments.
    """
    global _backend
    if _backend is not None:
        return _backend

    backend_type = os.environ.get("STATE_BACKEND", "local").strip().lower()

    if backend_type == "gcs":
        try:
            _backend = GCSBackend()
            logger.info("StateStoreBackend: using GCSBackend")
        except Exception as exc:
            logger.error(
                "GCSBackend initialisation failed (%s); falling back to LocalFileBackend", exc
            )
            _backend = _make_local(root_dir)
    else:
        _backend = _make_local(root_dir)
        logger.debug("StateStoreBackend: using LocalFileBackend at %s", _backend._root)

    return _backend


def _make_local(root_dir: Optional[Path]) -> LocalFileBackend:
    if root_dir is None:
        # Derive repo root: dashboard/backend/state_store_backend.py → ../../..
        root_dir = Path(__file__).resolve().parents[2]
    return LocalFileBackend(root_dir)
