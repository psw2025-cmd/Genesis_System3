from dashboard.backend.firestore_state_backend import FirestoreStateBackend


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
    def __init__(self, document):
        self._document = document

    def document(self, name):
        assert name == "state"
        return self._document


class FakeTransaction:
    def set(self, document, payload):
        document.payload = payload


class FakeClient:
    def __init__(self, payload=None):
        self.document = FakeDocument(payload)

    def collection(self, name):
        assert name == "system3_runtime"
        return FakeCollection(self.document)

    def transaction(self):
        return FakeTransaction()


def passthrough_transactional(fn):
    return fn


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
