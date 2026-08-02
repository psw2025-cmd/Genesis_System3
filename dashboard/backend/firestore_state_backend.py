"""Firestore persistence for the dashboard runtime state.

The dependency is imported lazily so local development and unit tests continue
working without Google credentials.  One Firestore transaction merges each
write with the current remote document, preserving fields produced by bounded
worker jobs while maintaining a monotonic state version.
"""

from __future__ import annotations

import copy
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
