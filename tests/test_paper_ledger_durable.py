from datetime import datetime, timezone

import pytest

from dashboard.backend.paper_ledger_backend import FirestorePaperLedgerBackend


class FakeSnapshot:
    def __init__(self, payload):
        self._payload = payload
        self.exists = payload is not None

    def to_dict(self):
        import copy
        return copy.deepcopy(self._payload or {})


class FakeDocument:
    def __init__(self, payload=None):
        self.payload = payload

    def get(self, transaction=None):
        if transaction is not None and getattr(transaction, "writes_started", False):
            raise RuntimeError("Firestore requires reads before writes")
        return FakeSnapshot(self.payload)


class FakeCollection:
    def __init__(self, documents):
        self.documents = documents

    def document(self, name):
        return self.documents.setdefault(name, FakeDocument())


class FakeTransaction:
    def __init__(self):
        self.writes_started = False

    def set(self, document, payload):
        import copy
        self.writes_started = True
        document.payload = copy.deepcopy(payload)

    def create(self, document, payload):
        import copy
        self.writes_started = True
        if document.payload is not None:
            raise RuntimeError("already exists")
        document.payload = copy.deepcopy(payload)


class FakeClient:
    def __init__(self):
        self.documents = {}

    def collection(self, name):
        assert name == "system3_paper_ledger"
        return FakeCollection(self.documents)

    def transaction(self):
        return FakeTransaction()


def passthrough(fn):
    return fn


class Clock:
    def __init__(self, iso="2026-08-14T07:00:00Z"):
        self.value = datetime.fromisoformat(iso.replace("Z", "+00:00"))

    def __call__(self):
        return self.value


def sample_state():
    return {
        "session_date": "2026-08-14",
        "seq": 7,
        "open_positions": [
            {
                "position_id": "POS_0007",
                "action": "OPEN",
                "underlying": "NIFTY",
                "option_type": "CE",
                "strike": 25000,
                "entry_price": 100.0,
                "current_price": 105.0,
                "unrealized_pnl": 300.0,
                "timestamp": "2026-08-14T12:30:00+05:30",
                "time_ist": "2026-08-14 12:30:00 IST",
            }
        ],
        "closed_positions": [],
        "recent_events": [],
        "data_source": "DHAN_LIVE_MARK_TO_MARKET",
        "updated_at_utc": "2026-08-14T07:00:00Z",
        # Malicious/drifted inputs must be forced safe.
        "mode": "LIVE",
        "live_trading_enabled": True,
        "broker_order_endpoints_called": True,
    }


def test_paper_state_survives_new_backend_instance_and_forces_live_off():
    client = FakeClient()
    clock = Clock()
    first = FirestorePaperLedgerBackend(client=client, transactional=passthrough, clock=clock)
    lease = first.acquire_lease("execution-a", 55)
    stored = first.publish(sample_state(), owner="execution-a", fence=lease["fence"])

    assert stored["ledger_version"] == 1
    assert stored["mode"] == "PAPER"
    assert stored["live_trading_enabled"] is False
    assert stored["broker_order_endpoints_called"] is False
    assert stored["ledger_source"] == "FIRESTORE_PAPER_LEDGER"

    # Simulates a new Cloud Run instance/revision: no process memory or local
    # file is shared, only Firestore client state.
    restarted = FirestorePaperLedgerBackend(client=client, transactional=passthrough, clock=clock)
    loaded = restarted.load_current()
    assert loaded["seq"] == 7
    assert loaded["open_positions"][0]["position_id"] == "POS_0007"
    public = restarted.public_snapshot()
    assert public["status"] == "ok"
    assert public["positions_source"] == "FIRESTORE_PAPER_LEDGER"
    assert public["paper_truth"]["durable"] is True
    assert public["paper_truth"]["ledger_version"] == 1
    assert public["live_trading_enabled"] is False


def test_paper_event_history_is_immutable_and_exact_retry_is_idempotent():
    client = FakeClient()
    backend = FirestorePaperLedgerBackend(client=client, transactional=passthrough, clock=Clock())
    lease = backend.acquire_lease("execution-a", 55)
    event = {
        "position_id": "POS_0007",
        "action": "OPEN",
        "timestamp": "2026-08-14T12:30:00+05:30",
        "time_ist": "2026-08-14 12:30:00 IST",
        "underlying": "NIFTY",
    }
    state = sample_state()
    state["recent_events"] = [event]
    first = backend.publish(state, owner="execution-a", fence=lease["fence"], events=[event])
    assert first["ledger_version"] == 1

    # A second transaction with the same content is safe. The current version
    # advances, while the immutable event document is not duplicated/changed.
    second = backend.publish({**state, "updated_at_utc": "2026-08-14T07:00:00Z"}, owner="execution-a", fence=lease["fence"], events=[event])
    assert second["ledger_version"] == 2
    event_docs = [name for name in client.documents if name.startswith("event_")]
    assert len(event_docs) == 1

    conflict = {**event, "underlying": "BANKNIFTY"}
    with pytest.raises(ValueError, match="immutable paper event conflict"):
        backend.publish(state, owner="execution-a", fence=lease["fence"], events=[conflict])


def test_paper_writer_lease_prevents_overlapping_cloud_jobs():
    client = FakeClient()
    backend = FirestorePaperLedgerBackend(client=client, transactional=passthrough, clock=Clock())
    a = backend.acquire_lease("execution-a", 55)
    b = backend.acquire_lease("execution-b", 55)
    assert a["acquired"] is True
    assert b["acquired"] is False
    with pytest.raises(PermissionError, match="owner/fence mismatch"):
        backend.publish(sample_state(), owner="execution-b", fence=a["fence"])


def test_empty_firestore_is_truthful_ready_empty_not_fake_zero_history():
    backend = FirestorePaperLedgerBackend(client=FakeClient(), transactional=passthrough, clock=Clock())
    public = backend.public_snapshot()
    assert public["status"] == "EMPTY"
    assert public["positions_source"] == "FIRESTORE_PAPER_LEDGER"
    assert public["paper_truth"]["durable"] is True
    assert public["paper_truth"]["ledger_version"] == 0
    assert public["paper_truth"]["order_endpoints_label"] == "INTENTIONALLY_NOT_CALLED_PAPER_SAFE"
    assert public["broker_order_endpoints_called"] is False
