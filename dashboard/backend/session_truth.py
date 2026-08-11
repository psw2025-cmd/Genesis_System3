"""Authoritative dashboard session and login-throttle truth.

Security goals:
- session identifiers are cryptographically random and opaque;
- only SHA-256 token hashes are stored server-side;
- expiry and revocation are authoritative server decisions;
- Cloud Run uses a shared Firestore authority and fails closed if unavailable;
- local/unit-test runtimes use an in-memory authority unless explicitly overridden;
- failed-login throttling uses the same shared backend in Cloud Run;
- no broker, order, position, or live-trading authority exists in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import os
import secrets
import threading
import time
from typing import Any, Dict, Optional, Tuple


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _epoch(dt: datetime) -> float:
    return dt.timestamp()


def _from_epoch(value: Any) -> datetime:
    return datetime.fromtimestamp(float(value), tz=timezone.utc)


@dataclass(frozen=True)
class SessionTruth:
    session_id_hash: str
    principal: str
    issued_at: datetime
    expires_at: datetime
    revoked_at: Optional[datetime] = None

    @property
    def active(self) -> bool:
        return self.revoked_at is None and _utc_now() < self.expires_at

    def public_dict(self) -> dict:
        return {
            "principal": self.principal,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "revoked": self.revoked_at is not None,
            "state": "ACTIVE" if self.active else "INACTIVE",
        }

    def storage_dict(self) -> dict:
        return {
            "schema_version": 1,
            "principal": self.principal,
            "issued_at_epoch": _epoch(self.issued_at),
            "expires_at_epoch": _epoch(self.expires_at),
            "revoked_at_epoch": _epoch(self.revoked_at) if self.revoked_at else None,
        }

    @classmethod
    def from_storage(cls, session_id_hash: str, data: Dict[str, Any]) -> "SessionTruth":
        revoked = data.get("revoked_at_epoch")
        return cls(
            session_id_hash=session_id_hash,
            principal=str(data.get("principal") or "dashboard"),
            issued_at=_from_epoch(data["issued_at_epoch"]),
            expires_at=_from_epoch(data["expires_at_epoch"]),
            revoked_at=_from_epoch(revoked) if revoked is not None else None,
        )


class SessionTruthStore:
    """Session + login-throttle authority with memory and Firestore backends.

    Cloud Run must use Firestore.  We deliberately do not silently fall back to
    process memory in cloud mode because that would make authentication depend
    on which instance receives the next request.
    """

    def __init__(
        self,
        *,
        backend: Optional[str] = None,
        firestore_client: Any = None,
        transactional: Any = None,
    ) -> None:
        cloud_runtime = _truthy(os.environ.get("CLOUD_MODE")) or bool(os.environ.get("K_SERVICE"))
        selected = (backend or os.environ.get("SYSTEM3_SESSION_BACKEND") or ("firestore" if cloud_runtime else "memory")).strip().lower()
        if selected not in {"memory", "firestore"}:
            raise ValueError(f"Unsupported SYSTEM3_SESSION_BACKEND={selected!r}")
        if cloud_runtime and selected != "firestore":
            raise RuntimeError("Cloud Run SessionTruth requires SYSTEM3_SESSION_BACKEND=firestore")

        self.backend_name = selected
        self._lock = threading.Lock()
        self._sessions: Dict[str, SessionTruth] = {}
        self._login_attempts: Dict[str, Dict[str, float]] = {}
        self._client = None
        self._transactional = None
        self._session_collection = None
        self._throttle_collection = None

        if selected == "firestore":
            project = os.environ.get("SYSTEM3_FIRESTORE_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
            if firestore_client is None:
                from google.cloud import firestore

                firestore_client = firestore.Client(project=project)
                transactional = transactional or firestore.transactional
            if transactional is None:
                raise RuntimeError("Firestore SessionTruth requires a transactional wrapper")
            self._client = firestore_client
            self._transactional = transactional
            session_collection = os.environ.get(
                "SYSTEM3_SESSION_COLLECTION", "system3_dashboard_sessions"
            )
            throttle_collection = os.environ.get(
                "SYSTEM3_LOGIN_THROTTLE_COLLECTION", "system3_dashboard_login_throttle"
            )
            for value in (session_collection, throttle_collection):
                if not value or "/" in value:
                    raise ValueError("Firestore SessionTruth collection names must be non-empty and contain no '/'")
            self._session_collection = self._client.collection(session_collection)
            self._throttle_collection = self._client.collection(throttle_collection)

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _hash_client_key(client_key: str) -> str:
        # Never persist raw client IP / forwarded address in the throttle store.
        return hashlib.sha256((client_key or "unknown").encode("utf-8")).hexdigest()

    def _purge_expired_memory_locked(self, now: datetime) -> None:
        expired = [key for key, record in self._sessions.items() if record.expires_at <= now]
        for key in expired:
            self._sessions.pop(key, None)

    def issue(self, *, max_age_seconds: int, principal: str = "dashboard") -> Tuple[str, SessionTruth]:
        if max_age_seconds <= 0:
            raise ValueError("max_age_seconds must be positive")
        token = secrets.token_urlsafe(48)
        now = _utc_now()
        record = SessionTruth(
            session_id_hash=self._hash_token(token),
            principal=principal,
            issued_at=now,
            expires_at=now + timedelta(seconds=max_age_seconds),
        )
        if self.backend_name == "memory":
            with self._lock:
                self._purge_expired_memory_locked(now)
                self._sessions[record.session_id_hash] = record
        else:
            self._session_collection.document(record.session_id_hash).set(record.storage_dict())
        return token, record

    def validate(self, token: str) -> Optional[SessionTruth]:
        if not token:
            return None
        now = _utc_now()
        key = self._hash_token(token)
        if self.backend_name == "memory":
            with self._lock:
                self._purge_expired_memory_locked(now)
                record = self._sessions.get(key)
                if record is None or record.revoked_at is not None or record.expires_at <= now:
                    return None
                return record

        ref = self._session_collection.document(key)
        snapshot = ref.get()
        if not getattr(snapshot, "exists", False):
            return None
        data = snapshot.to_dict() or {}
        try:
            record = SessionTruth.from_storage(key, data)
        except Exception:
            # Malformed auth state is never accepted.
            return None
        if record.expires_at <= now:
            try:
                ref.delete()
            except Exception:
                pass
            return None
        if record.revoked_at is not None:
            return None
        return record

    def revoke(self, token: str) -> bool:
        if not token:
            return False
        key = self._hash_token(token)
        now = _utc_now()
        if self.backend_name == "memory":
            with self._lock:
                self._purge_expired_memory_locked(now)
                record = self._sessions.get(key)
                if record is None or record.revoked_at is not None:
                    return False
                self._sessions[key] = SessionTruth(
                    session_id_hash=record.session_id_hash,
                    principal=record.principal,
                    issued_at=record.issued_at,
                    expires_at=record.expires_at,
                    revoked_at=now,
                )
                return True

        ref = self._session_collection.document(key)

        @self._transactional
        def _revoke(transaction):
            snapshot = ref.get(transaction=transaction)
            if not getattr(snapshot, "exists", False):
                return False
            data = snapshot.to_dict() or {}
            if data.get("revoked_at_epoch") is not None:
                return False
            expires_at = float(data.get("expires_at_epoch") or 0)
            if expires_at <= time.time():
                transaction.delete(ref)
                return False
            transaction.update(ref, {"revoked_at_epoch": time.time()})
            return True

        return bool(_revoke(self._client.transaction()))

    def login_allowed(self, client_key: str, *, window_seconds: int, max_failures: int) -> Tuple[bool, int]:
        if window_seconds <= 0 or max_failures <= 0:
            raise ValueError("login throttle limits must be positive")
        now = time.time()
        key = self._hash_client_key(client_key)
        if self.backend_name == "memory":
            with self._lock:
                state = self._login_attempts.get(key)
                if not state or now - state["window_started_at"] >= window_seconds:
                    return True, 0
                count = int(state.get("failure_count", 0))
                if count < max_failures:
                    return True, 0
                retry_after = max(1, int(window_seconds - (now - state["window_started_at"])))
                return False, retry_after

        snapshot = self._throttle_collection.document(key).get()
        if not getattr(snapshot, "exists", False):
            return True, 0
        state = snapshot.to_dict() or {}
        started = float(state.get("window_started_at_epoch") or 0)
        count = int(state.get("failure_count") or 0)
        if now - started >= window_seconds or count < max_failures:
            return True, 0
        return False, max(1, int(window_seconds - (now - started)))

    def record_login_failure(self, client_key: str, *, window_seconds: int) -> int:
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        now = time.time()
        key = self._hash_client_key(client_key)
        if self.backend_name == "memory":
            with self._lock:
                state = self._login_attempts.get(key)
                if not state or now - state["window_started_at"] >= window_seconds:
                    state = {"window_started_at": now, "failure_count": 0}
                    self._login_attempts[key] = state
                state["failure_count"] += 1
                return int(state["failure_count"])

        ref = self._throttle_collection.document(key)

        @self._transactional
        def _record(transaction):
            snapshot = ref.get(transaction=transaction)
            data = snapshot.to_dict() if getattr(snapshot, "exists", False) else {}
            data = data or {}
            started = float(data.get("window_started_at_epoch") or 0)
            count = int(data.get("failure_count") or 0)
            if not started or now - started >= window_seconds:
                started = now
                count = 0
            count += 1
            transaction.set(
                ref,
                {
                    "schema_version": 1,
                    "window_started_at_epoch": started,
                    "failure_count": count,
                    "updated_at_epoch": now,
                },
            )
            return count

        return int(_record(self._client.transaction()))

    def clear_login_failures(self, client_key: str) -> None:
        key = self._hash_client_key(client_key)
        if self.backend_name == "memory":
            with self._lock:
                self._login_attempts.pop(key, None)
            return
        self._throttle_collection.document(key).delete()

    def active_count(self) -> int:
        now = _utc_now()
        if self.backend_name == "memory":
            with self._lock:
                self._purge_expired_memory_locked(now)
                return sum(1 for record in self._sessions.values() if record.revoked_at is None)
        count = 0
        for snapshot in self._session_collection.stream():
            data = snapshot.to_dict() or {}
            try:
                record = SessionTruth.from_storage(snapshot.id, data)
            except Exception:
                continue
            if record.revoked_at is None and record.expires_at > now:
                count += 1
        return count

    def revoked_count(self) -> int:
        now = _utc_now()
        if self.backend_name == "memory":
            with self._lock:
                self._purge_expired_memory_locked(now)
                return sum(1 for record in self._sessions.values() if record.revoked_at is not None)
        count = 0
        for snapshot in self._session_collection.stream():
            data = snapshot.to_dict() or {}
            try:
                record = SessionTruth.from_storage(snapshot.id, data)
            except Exception:
                continue
            if record.revoked_at is not None and record.expires_at > now:
                count += 1
        return count


_SESSION_TRUTH_STORE = SessionTruthStore()


def get_session_truth_store() -> SessionTruthStore:
    return _SESSION_TRUTH_STORE
