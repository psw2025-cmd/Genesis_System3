"""Firestore persistence for the dashboard runtime state.

The dependency is imported lazily so local development and unit tests continue
working without Google credentials.  One Firestore transaction merges each
write with the current remote document, preserving fields produced by bounded
worker jobs while maintaining a monotonic state version.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional


def _json_clone(value: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(json.dumps(value, default=str))


def _deep_merge(base: Dict[str, Any], updates: Dict[str, Any]) -> None:
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = copy.deepcopy(value)


class FirestoreStateBackend:
    """Transactional shared state document used by Cloud Run services/jobs."""

    def __init__(
        self,
        project: Optional[str] = None,
        collection: Optional[str] = None,
        document: Optional[str] = None,
        *,
        client: Any = None,
        transactional: Optional[Callable] = None,
    ) -> None:
        project = project or os.environ.get("SYSTEM3_FIRESTORE_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
        collection = collection or os.environ.get("SYSTEM3_FIRESTORE_COLLECTION", "system3_runtime")
        document = document or os.environ.get("SYSTEM3_FIRESTORE_DOCUMENT", "state")
        if "/" in collection or "/" in document:
            raise ValueError("Firestore collection/document names must not contain '/'")

        if client is None:
            from google.cloud import firestore  # Imported only in Firestore mode.

            client = firestore.Client(project=project)
            transactional = transactional or firestore.transactional
        if transactional is None:
            raise ValueError("transactional wrapper is required with an injected Firestore client")

        self.client = client
        self.document_ref = client.collection(collection).document(document)
        self._transactional = transactional

    def load(self) -> Optional[Dict[str, Any]]:
        snapshot = self.document_ref.get()
        if not getattr(snapshot, "exists", False):
            return None
        data = snapshot.to_dict() or {}
        return _json_clone(data)

    def save(self, state: Dict[str, Any]) -> Dict[str, Any]:
        incoming = _json_clone(state)

        @self._transactional
        def _persist(transaction):
            snapshot = self.document_ref.get(transaction=transaction)
            existing = snapshot.to_dict() if getattr(snapshot, "exists", False) else {}
            existing = _json_clone(existing or {})
            merged = copy.deepcopy(existing)
            _deep_merge(merged, incoming)

            existing_version = int(existing.get("state_version", 0) or 0)
            incoming_version = int(incoming.get("state_version", 0) or 0)
            merged["state_version"] = (
                incoming_version if incoming_version > existing_version else existing_version + 1
            )
            merged["firestore_updated_at_utc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            transaction.set(self.document_ref, merged)
            return merged

        return _persist(self.client.transaction())


class FirestoreSchedulerEvidenceBackend:
    """Narrow scheduler evidence/lease documents, separate from runtime state."""

    ALLOWED_KEYS = {"schema_version", "observed_at_utc", "resources", "jobs", "artifacts", "summary"}
    MAX_BYTES = 200_000
    MAX_FUTURE_SKEW_SECONDS = 60

    def __init__(self, project: Optional[str] = None, collection: str = "system3_scheduler_evidence", *, client: Any = None, transactional: Optional[Callable] = None, clock: Optional[Callable[[], datetime]] = None) -> None:
        if "/" in collection:
            raise ValueError("Firestore collection name must not contain '/'")
        project = project or os.environ.get("SYSTEM3_FIRESTORE_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if client is None:
            from google.cloud import firestore
            client = firestore.Client(project=project)
            transactional = transactional or firestore.transactional
        if transactional is None:
            raise ValueError("transactional wrapper is required with an injected Firestore client")
        self.client = client
        self.collection = client.collection(collection)
        self._transactional = transactional
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _now(self) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise ValueError("scheduler evidence clock must return an aware datetime")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _parse_utc(value: str) -> datetime:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return parsed.astimezone(timezone.utc)

    def load_current(self) -> Optional[Dict[str, Any]]:
        snapshot = self.collection.document("current").get()
        return _json_clone(snapshot.to_dict() or {}) if getattr(snapshot, "exists", False) else None

    def publish(self, evidence: Dict[str, Any], *, owner: str, fence: int) -> Dict[str, Any]:
        incoming = _json_clone(evidence)
        if incoming.get("schema_version") != 1 or set(incoming) - self.ALLOWED_KEYS:
            raise ValueError("invalid scheduler evidence schema")
        observed = self._parse_utc(incoming.get("observed_at_utc", ""))
        canonical = json.dumps(incoming, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if len(canonical) > self.MAX_BYTES:
            raise ValueError("scheduler evidence exceeds size limit")
        validation_now = self._now()
        if observed.timestamp() > validation_now.timestamp() + self.MAX_FUTURE_SKEW_SECONDS:
            raise ValueError("scheduler evidence observation is too far in the future")
        incoming["evidence_sha256"] = hashlib.sha256(canonical).hexdigest()
        ref = self.collection.document("current")
        lease_ref = self.collection.document("collector_lease")

        @self._transactional
        def _persist(transaction):
            commit_now = self._now()
            lease_snapshot = lease_ref.get(transaction=transaction)
            lease = lease_snapshot.to_dict() if getattr(lease_snapshot, "exists", False) else {}
            if lease.get("owner") != owner or int(lease.get("fence", 0)) != int(fence):
                raise PermissionError("scheduler collector lease owner/fence mismatch")
            if self._parse_utc(lease["expires_at_utc"]) <= commit_now:
                raise PermissionError("scheduler collector lease expired")
            snapshot = ref.get(transaction=transaction)
            existing = snapshot.to_dict() if getattr(snapshot, "exists", False) else {}
            if existing:
                previous = self._parse_utc(existing["observed_at_utc"])
                if observed < previous:
                    raise ValueError("scheduler evidence observation regressed")
                if observed == previous:
                    if existing.get("evidence_sha256") != incoming["evidence_sha256"]:
                        raise ValueError("conflicting scheduler evidence for identical observation")
                    return _json_clone(existing)
            stored = {**incoming, "evidence_version": int(existing.get("evidence_version", 0) or 0) + 1}
            transaction.set(ref, stored)
            return _json_clone(stored)

        return _persist(self.client.transaction())

    def acquire_lease(self, owner: str, ttl_seconds: int) -> Dict[str, Any]:
        if not owner or not (1 <= int(ttl_seconds) <= 900):
            raise ValueError("invalid scheduler collector lease")
        # owner must be the unique Cloud Run execution name, never a static job name.
        ref = self.collection.document("collector_lease")

        @self._transactional
        def _acquire(transaction):
            commit_now = self._now()
            snapshot = ref.get(transaction=transaction)
            current = snapshot.to_dict() if getattr(snapshot, "exists", False) else {}
            active = bool(current and self._parse_utc(current["expires_at_utc"]) > commit_now)
            if active and current.get("owner") != owner:
                return {"acquired": False, "owner": current.get("owner"), "fence": int(current.get("fence", 0)), "expires_at_utc": current.get("expires_at_utc")}
            fence = int(current.get("fence", 0))
            if not active or current.get("owner") != owner:
                fence += 1
            expires = commit_now.timestamp() + int(ttl_seconds)
            value = {"owner": owner, "fence": fence, "acquired_at_utc": commit_now.isoformat().replace("+00:00", "Z"), "expires_at_utc": datetime.fromtimestamp(expires, timezone.utc).isoformat().replace("+00:00", "Z")}
            transaction.set(ref, value)
            return {"acquired": True, **value}

        return _acquire(self.client.transaction())
