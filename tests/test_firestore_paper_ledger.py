"""Firestore PAPER ledger atomic append and cross-instance readback contract."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
import sys
import types

from dashboard.backend.autonomous_paper_core import PaperEvidenceError, estimate_costed_paper_pnl
from dashboard.backend.firestore_paper_ledger import FirestorePaperLedger


class _Snapshot:
    def __init__(self, ref, data):
        self.id, self._data, self.exists = ref.id, data, data is not None
    def to_dict(self):
        return dict(self._data or {})


class _Ref:
    def __init__(self, store, ident):
        self.store, self.id = store, ident
    def get(self, transaction=None):
        return _Snapshot(self, self.store.get(self.id))


class _Collection:
    def __init__(self, store): self.store = store
    def document(self, ident): return _Ref(self.store, ident)
    def stream(self):
        return [_Snapshot(_Ref(self.store, key), value) for key, value in self.store.items()]


class _Transaction:
    def __init__(self, store): self.store, self.writes = store, []
    def create(self, ref, data):
        if ref.id in self.store: raise PaperEvidenceError("DUPLICATE_EVENT_DOCUMENT")
        self.writes.append(("create", ref.id, dict(data)))
    def set(self, ref, data): self.writes.append(("set", ref.id, dict(data)))
    def commit(self):
        for op, ident, value in self.writes:
            if op == "create" and ident in self.store: raise PaperEvidenceError("DUPLICATE_EVENT_DOCUMENT")
        for _op, ident, value in self.writes: self.store[ident] = value


class _Client:
    def __init__(self): self.docs = {}
    def collection(self, _name): return _Collection(self.docs)
    def transaction(self): return _Transaction(self.docs)


def _transactional(fn):
    def run(tx):
        result = fn(tx)
        tx.commit()
        return result
    return run


def test_firestore_paper_lifecycle_is_durable_across_ledger_instances():
    client = _Client()
    ledger = FirestorePaperLedger(client=client, transactional=_transactional)
    stamp = datetime(2026, 11, 14, 4, 0, tzinfo=timezone.utc).isoformat()
    position = {"position_id": "PAPER-1", "entry_price": 100.0, "qty": 1}
    assert ledger.record_open(position, stamp) is True
    recovered = FirestorePaperLedger(client=client, transactional=_transactional).snapshot()
    assert recovered["event_count"] == 3
    assert recovered["verified_hash_chain"] is True
    assert recovered["open_positions"][0]["position_id"] == "PAPER-1"


def test_firestore_closed_trade_and_pnl_read_back_from_new_instance():
    client = _Client()
    ledger = FirestorePaperLedger(client=client, transactional=_transactional)
    entry_at = datetime(2026, 11, 14, 4, 0, tzinfo=timezone.utc).isoformat()
    exit_at = datetime(2026, 11, 14, 4, 1, tzinfo=timezone.utc).isoformat()
    pnl = estimate_costed_paper_pnl(100.0, 110.0, 1)
    opened = {"position_id": "PAPER-CLOSED-1", "entry_price": 100.0, "qty": 1}
    ledger.record_open(opened, entry_at)
    closed = {**opened, "exit_price": 110.0, "realized_pnl": pnl}
    assert ledger.record_close(closed, exit_at) is True
    recovered = FirestorePaperLedger(client=client, transactional=_transactional).snapshot()
    assert recovered["event_count"] == 6
    assert recovered["open_positions"] == []
    assert recovered["closed_positions"][0]["realized_pnl"] == pnl
    assert recovered["outcomes"]["PAPER-CLOSED-1"]["validation_status"] == "NOT_VERIFIED"


def test_firestore_paper_ledger_idempotency_and_chain_corruption_fail_closed():
    client = _Client()
    ledger = FirestorePaperLedger(client=client, transactional=_transactional)
    stamp = datetime(2026, 11, 14, 4, 0, tzinfo=timezone.utc).isoformat()
    row = ("gap:2026-11-14:NIFTY", "NIFTY", "GAP_OBSERVED", stamp,
           {"session": "2026-11-14", "opened_at": stamp})
    assert ledger.append_batch([row]) is True
    assert ledger.append_batch([row]) is False
    first_event = next(key for key in client.docs if key.startswith("event-"))
    client.docs[first_event]["data"]["session"] = "tampered"
    with pytest.raises(PaperEvidenceError, match="PAPER_LEDGER_HASH_MISMATCH"):
        ledger.snapshot()


def test_cloud_run_paper_engine_selects_firestore_without_sqlite_fallback(tmp_path, monkeypatch):
    class _RemoteLedger:
        def __init__(self): self.opened = True
        def snapshot(self):
            return {"event_count": 0, "open_positions": [], "closed_positions": []}

    module = types.ModuleType("dashboard.backend.firestore_paper_ledger")
    module.FirestorePaperLedger = _RemoteLedger
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setenv("K_SERVICE", "genesis-paper-test")
    from dashboard.backend.cloud_paper_engine import CloudPaperEngine
    engine = CloudPaperEngine(tmp_path)
    assert isinstance(engine.master_ledger, _RemoteLedger)
    assert not (tmp_path / "paper_master_ledger.sqlite3").exists()


def test_cloud_run_paper_engine_fails_closed_if_firestore_unavailable(tmp_path, monkeypatch):
    class _UnavailableLedger:
        def __init__(self): raise RuntimeError("firestore unavailable")

    module = types.ModuleType("dashboard.backend.firestore_paper_ledger")
    module.FirestorePaperLedger = _UnavailableLedger
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setenv("K_SERVICE", "genesis-paper-test")
    from dashboard.backend.cloud_paper_engine import CloudPaperEngine
    with pytest.raises(RuntimeError, match="firestore unavailable"):
        CloudPaperEngine(tmp_path)
