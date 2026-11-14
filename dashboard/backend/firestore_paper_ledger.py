"""Durable Firestore event store for the PAPER-only lifecycle ledger.

Firestore is the Cloud Run authority; SQLite remains a local-only backend.
Every event is immutable and hash chained. A transactional head document
serializes append batches and makes each order/fill/position transition atomic.
"""
from __future__ import annotations

import json
import os
from datetime import timezone
from typing import Any, Mapping

from dashboard.backend.autonomous_paper_core import (
    GENESIS,
    MasterPaperLedger,
    PaperEvidenceError,
    _canonical,
    _stamp,
)


class FirestorePaperLedger(MasterPaperLedger):
    """MasterPaperLedger-compatible durable append-only Firestore backend."""

    def __init__(self, project: str | None = None, collection: str | None = None,
                 *, client: Any = None, transactional: Any = None) -> None:
        if client is None:
            from google.cloud import firestore

            client = firestore.Client(project=project or os.environ.get("GOOGLE_CLOUD_PROJECT"))
            transactional = transactional or firestore.transactional
        if transactional is None:
            raise ValueError("Firestore transactional wrapper is required")
        name = collection or os.environ.get("SYSTEM3_PAPER_LEDGER_COLLECTION", "system3_paper_ledger")
        if "/" in name:
            raise ValueError("Firestore collection name must not contain slash")
        self.client = client
        self.collection = client.collection(name)
        self.head_ref = self.collection.document("HEAD")
        self._transactional = transactional

    @staticmethod
    def _event_doc_id(seq: int) -> str:
        return f"event-{seq:020d}"

    def _verified_events(self) -> list[dict]:
        rows = []
        for snap in self.collection.stream():
            if snap.id == "HEAD":
                continue
            doc = snap.to_dict() or {}
            rows.append(doc)
        rows.sort(key=lambda row: int(row.get("seq", 0)))
        previous = GENESIS
        result = []
        for expected_seq, row in enumerate(rows, start=1):
            try:
                seq = int(row["seq"])
                event_id = str(row["event_id"])
                trade_id = str(row["trade_id"])
                kind = str(row["type"])
                timestamp = _stamp(str(row["at"])).astimezone(timezone.utc).isoformat()
                payload = _canonical(row["data"])
                prior = str(row["previous_hash"])
                digest = str(row["event_hash"])
            except (KeyError, TypeError, ValueError) as exc:
                raise PaperEvidenceError("CORRUPT_PAPER_LEDGER") from exc
            if seq != expected_seq or prior != previous or digest != self._digest(
                event_id, trade_id, kind, timestamp, payload, prior
            ):
                raise PaperEvidenceError("PAPER_LEDGER_HASH_MISMATCH")
            result.append({"seq": seq, "event_id": event_id, "trade_id": trade_id,
                           "type": kind, "at": timestamp, "data": json.loads(payload),
                           "event_hash": digest})
            previous = digest
        head_snap = self.head_ref.get()
        head = head_snap.to_dict() or {} if getattr(head_snap, "exists", False) else {}
        if int(head.get("seq", 0) or 0) != len(result) or head.get("event_hash", GENESIS) != previous:
            raise PaperEvidenceError("PAPER_LEDGER_HEAD_MISMATCH")
        return result

    def snapshot(self) -> dict:
        return self._project(self._verified_events())

    def append_batch(self, records: list[tuple[str, str, str, str, Mapping[str, Any]]]) -> bool:
        events = self._verified_events()
        self._project(events)
        seen = {event["event_id"]: event for event in events}
        pending = []
        for event_id, trade_id, kind, timestamp, data in records:
            timestamp = _stamp(timestamp).astimezone(timezone.utc).isoformat()
            if not event_id or not trade_id or not kind:
                raise PaperEvidenceError("MISSING_EVENT_IDENTITY")
            encoded = _canonical(dict(data))
            old = seen.get(event_id)
            if old:
                if (old["trade_id"], old["type"], old["at"], _canonical(old["data"])) != (
                    trade_id, kind, timestamp, encoded
                ):
                    raise PaperEvidenceError("CONFLICTING_DUPLICATE_PAPER_EVENT")
                continue
            if any(row["event_id"] == event_id for row in pending):
                raise PaperEvidenceError("DUPLICATE_EVENT_WITHIN_BATCH")
            pending.append({"event_id": event_id, "trade_id": trade_id, "type": kind,
                            "at": timestamp, "data": json.loads(encoded), "payload": encoded})
        if not pending:
            return False
        if len(pending) > 450:
            raise PaperEvidenceError("PAPER_LEDGER_BATCH_LIMIT_EXCEEDED")
        if len(pending) != len(records):
            raise PaperEvidenceError("PARTIAL_PAPER_TRANSITION")
        previous = events[-1]["event_hash"] if events else GENESIS
        docs = []
        for seq, row in enumerate(pending, start=len(events) + 1):
            digest = self._digest(row["event_id"], row["trade_id"], row["type"],
                                  row["at"], row["payload"], previous)
            docs.append({"seq": seq, "event_id": row["event_id"], "trade_id": row["trade_id"],
                         "type": row["type"], "at": row["at"], "data": row["data"],
                         "previous_hash": previous, "event_hash": digest})
            previous = digest
        projected = events + [{k: doc[k] for k in ("seq", "event_id", "trade_id", "type", "at", "data", "event_hash")} for doc in docs]
        self._project(projected)
        expected_seq = len(events)
        expected_hash = events[-1]["event_hash"] if events else GENESIS

        @self._transactional
        def _persist(transaction):
            snapshot = self.head_ref.get(transaction=transaction)
            head = snapshot.to_dict() or {} if getattr(snapshot, "exists", False) else {}
            if int(head.get("seq", 0) or 0) != expected_seq or head.get("event_hash", GENESIS) != expected_hash:
                raise PaperEvidenceError("PAPER_LEDGER_CONCURRENT_APPEND_RETRY_REQUIRED")
            for doc in docs:
                transaction.create(self.collection.document(self._event_doc_id(doc["seq"])), doc)
            transaction.set(self.head_ref, {"seq": docs[-1]["seq"], "event_hash": docs[-1]["event_hash"]})
            return True

        _persist(self.client.transaction())
        # Read back and verify the committed chain before reporting success.
        self._project(self._verified_events())
        return True
