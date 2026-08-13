import pytest
from datetime import datetime, timezone

from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend, FirestoreStateBackend


class FakeSnapshot:
    def __init__(self, payload):
        self._payload = payload
        self.exists = payload is not None

    def to_dict(self):
        return dict(self._payload or {})


class FakeDocument:
    def __init__(self, payload=None):
        self.payload = payload

    def get(self, transaction=None):
        return FakeSnapshot(self.payload)


class FakeCollection:
    def __init__(self, documents):
        self._documents = documents

    def document(self, name):
        return self._documents.setdefault(name, FakeDocument())


class FakeTransaction:
    def set(self, document, payload):
        document.payload = payload


class FakeClient:
    def __init__(self, payload=None):
        self.documents = {"state": FakeDocument(payload)}
        self.document = self.documents["state"]

    def collection(self, name):
        assert name in ("system3_runtime", "system3_scheduler_evidence")
        return FakeCollection(self.documents)

    def transaction(self):
        return FakeTransaction()


def passthrough_transactional(fn):
    return fn


class FakeClock:
    def __init__(self, value):
        self.value = datetime.fromisoformat(value.replace("Z", "+00:00"))

    def __call__(self):
        return self.value

    def set(self, value):
        self.value = datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_firestore_save_merges_worker_fields_and_monotonic_version():
    client = FakeClient({"state_version": 4, "cloud_job": {"kind": "smoke"}})
    backend = FirestoreStateBackend(client=client, transactional=passthrough_transactional)

    saved = backend.save({"state_version": 2, "mode": "PAPER", "market": {"is_open": False}})

    assert saved["state_version"] == 5
    assert saved["cloud_job"] == {"kind": "smoke"}
    assert saved["market"]["is_open"] is False
    assert saved["firestore_updated_at_utc"].endswith("Z")
    assert backend.load() == saved


def test_firestore_rejects_path_injection():
    client = FakeClient()
    try:
        FirestoreStateBackend(collection="bad/path", client=client, transactional=passthrough_transactional)
    except ValueError as exc:
        assert "must not contain" in str(exc)
    else:
        raise AssertionError("Expected invalid Firestore path to be rejected")


def test_scheduler_evidence_is_monotonic_hashed_and_idempotent():
    client = FakeClient()
    clock = FakeClock("2026-08-14T01:00:00Z")
    backend = FirestoreSchedulerEvidenceBackend(client=client, transactional=passthrough_transactional, clock=clock)
    lease = backend.acquire_lease("execution-a", 120)
    evidence = {"schema_version": 1, "observed_at_utc": "2026-08-14T01:00:00Z", "resources": [{"name": "rank", "state": "ENABLED"}]}
    clock.set("2026-08-14T01:00:01Z")
    args = {"owner": "execution-a", "fence": lease["fence"]}
    first = backend.publish(evidence, **args)
    again = backend.publish(evidence, **args)
    assert first == again
    assert first["evidence_version"] == 1
    assert len(first["evidence_sha256"]) == 64
    assert backend.load_current() == first
    with pytest.raises(ValueError, match="regressed"):
        backend.publish({"schema_version": 1, "observed_at_utc": "2026-08-14T00:59:59Z", "resources": []}, **args)
    with pytest.raises(ValueError, match="conflicting"):
        backend.publish({"schema_version": 1, "observed_at_utc": "2026-08-14T01:00:00Z", "resources": []}, **args)


def test_scheduler_collector_lease_is_idempotent_and_exclusive():
    client = FakeClient()
    clock = FakeClock("2026-08-14T01:00:00Z")
    backend = FirestoreSchedulerEvidenceBackend(client=client, transactional=passthrough_transactional, clock=clock)
    first = backend.acquire_lease("execution-a", 120)
    clock.set("2026-08-14T01:00:30Z"); renewal = backend.acquire_lease("execution-a", 120)
    clock.set("2026-08-14T01:01:00Z"); denied = backend.acquire_lease("execution-b", 120)
    clock.set("2026-08-14T01:03:00Z"); takeover = backend.acquire_lease("execution-b", 120)
    assert first["fence"] == renewal["fence"] == 1
    assert denied["acquired"] is False
    assert takeover["acquired"] is True and takeover["fence"] == 2
    evidence = {"schema_version": 1, "observed_at_utc": "2026-08-14T01:03:00Z", "resources": []}
    with pytest.raises(PermissionError, match="mismatch"):
        backend.publish(evidence, owner="execution-a", fence=1)
    clock.set("2026-08-14T01:05:01Z")
    with pytest.raises(PermissionError, match="expired"):
        backend.publish(evidence, owner="execution-b", fence=2)


def test_scheduler_evidence_rejects_future_unknown_and_oversized_payloads():
    client = FakeClient()
    clock = FakeClock("2026-08-14T01:00:00Z")
    backend = FirestoreSchedulerEvidenceBackend(client=client, transactional=passthrough_transactional, clock=clock)
    lease = backend.acquire_lease("a", 120)
    args = {"owner": "a", "fence": lease["fence"]}
    with pytest.raises(ValueError, match="future"):
        backend.publish({"schema_version": 1, "observed_at_utc": "2026-08-14T01:02:00Z"}, **args)
    with pytest.raises(ValueError, match="schema"):
        backend.publish({"schema_version": 1, "observed_at_utc": "2026-08-14T01:00:00Z", "secret": "x"}, **args)
    with pytest.raises(ValueError, match="size"):
        backend.publish({"schema_version": 1, "observed_at_utc": "2026-08-14T01:00:00Z", "summary": {"text": "x" * 210000}}, **args)


def test_scheduler_evidence_allows_exact_future_skew_boundary_only():
    client = FakeClient()
    clock = FakeClock("2026-08-14T01:00:00Z")
    backend = FirestoreSchedulerEvidenceBackend(client=client, transactional=passthrough_transactional, clock=clock)
    lease = backend.acquire_lease("execution-unique-123", 120)
    accepted = backend.publish(
        {"schema_version": 1, "observed_at_utc": "2026-08-14T01:01:00Z", "resources": []},
        owner="execution-unique-123",
        fence=lease["fence"],
    )
    assert accepted["evidence_version"] == 1


def test_publish_rechecks_trusted_time_inside_transaction_callback():
    client = FakeClient()
    clock = FakeClock("2026-08-14T01:00:00Z")
    backend = FirestoreSchedulerEvidenceBackend(client=client, transactional=passthrough_transactional, clock=clock)
    lease = backend.acquire_lease("execution-a", 30)

    def advance_before_callback(fn):
        def wrapped(transaction):
            clock.set("2026-08-14T01:00:31Z")
            return fn(transaction)
        return wrapped

    backend._transactional = advance_before_callback
    with pytest.raises(PermissionError, match="expired"):
        backend.publish(
            {"schema_version": 1, "observed_at_utc": "2026-08-14T01:00:00Z", "resources": []},
            owner="execution-a",
            fence=lease["fence"],
        )
