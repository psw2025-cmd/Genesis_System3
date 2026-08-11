"""Authoritative in-process dashboard session registry.

Security goals:
- session identifiers are cryptographically random and opaque;
- only SHA-256 token hashes are stored server-side;
- expiry/revocation are authoritative server decisions, not browser timers;
- process restart invalidates all sessions (fail closed);
- no broker/trading imports or mutation authority live here.

This is intentionally in-process for the current single-instance analyzer/paper
runtime. A future multi-instance deployment must replace this storage backend
with a shared transactional store before increasing Cloud Run concurrency or
instance count.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import threading
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class SessionTruth:
    session_id_hash: str
    principal: str
    issued_at: datetime
    expires_at: datetime
    revoked_at: Optional[datetime] = None

    @property
    def active(self) -> bool:
        now = datetime.now(timezone.utc)
        return self.revoked_at is None and now < self.expires_at

    def public_dict(self) -> dict:
        return {
            "principal": self.principal,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "revoked": self.revoked_at is not None,
            "state": "ACTIVE" if self.active else "INACTIVE",
        }


class SessionTruthStore:
    """Thread-safe session registry with opaque bearer cookies."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: Dict[str, SessionTruth] = {}

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _purge_expired_locked(self, now: datetime) -> None:
        expired = [
            key
            for key, record in self._sessions.items()
            if record.expires_at <= now or record.revoked_at is not None
        ]
        for key in expired:
            self._sessions.pop(key, None)

    def issue(self, *, max_age_seconds: int, principal: str = "dashboard") -> Tuple[str, SessionTruth]:
        if max_age_seconds <= 0:
            raise ValueError("max_age_seconds must be positive")
        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        record = SessionTruth(
            session_id_hash=self._hash_token(token),
            principal=principal,
            issued_at=now,
            expires_at=now + timedelta(seconds=max_age_seconds),
        )
        with self._lock:
            self._purge_expired_locked(now)
            self._sessions[record.session_id_hash] = record
        return token, record

    def validate(self, token: str) -> Optional[SessionTruth]:
        if not token:
            return None
        now = datetime.now(timezone.utc)
        key = self._hash_token(token)
        with self._lock:
            record = self._sessions.get(key)
            if record is None:
                return None
            if record.revoked_at is not None or record.expires_at <= now:
                self._sessions.pop(key, None)
                return None
            return record

    def revoke(self, token: str) -> bool:
        if not token:
            return False
        key = self._hash_token(token)
        now = datetime.now(timezone.utc)
        with self._lock:
            record = self._sessions.get(key)
            if record is None:
                return False
            revoked = SessionTruth(
                session_id_hash=record.session_id_hash,
                principal=record.principal,
                issued_at=record.issued_at,
                expires_at=record.expires_at,
                revoked_at=now,
            )
            self._sessions[key] = revoked
            self._purge_expired_locked(now)
            return True

    def active_count(self) -> int:
        now = datetime.now(timezone.utc)
        with self._lock:
            self._purge_expired_locked(now)
            return len(self._sessions)


_SESSION_TRUTH_STORE = SessionTruthStore()


def get_session_truth_store() -> SessionTruthStore:
    return _SESSION_TRUTH_STORE
