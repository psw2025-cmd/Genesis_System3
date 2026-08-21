import pytest
from datetime import datetime, timezone

from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend, FirestoreStateBackend, derive_scheduler_health


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
        if transaction is not None and getattr(transaction, "writes_started", False):
            raise RuntimeError("Firestore requires all reads before writes")
        return FakeSnapshot(self.payload)


class FakeCollection:
    def __init__(self, documents):
        self._documents = documents

    def document(self, name):
        return self._documents.setdefault(name, FakeDocument())


class FakeTransaction:
    def __init__(self): self.writes_started = False
    def set(self, document, payload):
        self.writes_started = True
        document.payload = payload

    def create(self, document, payload):
        self.writes_started = True
        if document.payload is not None:
            raise RuntimeError("already exists")
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


def test_business_artifact_is_hashed_durable_and_idempotent():
    import base64, hashlib, json
    client = FakeClient()
    clock = FakeClock("2026-08-14T01:00:00Z")
    backend = FirestoreSchedulerEvidenceBackend(client=client, transactional=passthrough_transactional, clock=clock)
    payload = {"rows": [{"underlying": "NIFTY", "rank": 1}]}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    artifact = {"schema_version": 1, "lane": "rank", "run_id": "execution-a", "produced_at_utc": "2026-08-14T01:00:00Z", "business_date": "2026-08-14", "status": "PASS", "reason_code": None, "payload": payload, "source_sha256": "a" * 64, "code_sha256": "b" * 64, "output_sha256": digest, "output_bytes_b64": base64.b64encode(raw).decode()}
    first = backend.publish_artifact("rank", artifact)
    again = backend.publish_artifact("rank", artifact)
    assert first == again and first["artifact_version"] == 1
    assert backend.load_artifact("rank") == first
    verified = backend.verify_artifact("rank", now=datetime(2026, 8, 14, 1, 1, tzinfo=timezone.utc))
    assert verified["verified"] is True and verified["output_sha256"] == digest
    with pytest.raises(ValueError, match="hash mismatch"):
        backend.publish_artifact("rank", {**artifact, "output_sha256": "0" * 64})
    client.documents["artifact_rank"].payload = {**first, "output_bytes_b64": "Y29ycnVwdA=="}
    with pytest.raises(ValueError, match="stored bytes hash mismatch"):
        backend.verify_artifact("rank", now=datetime(2026, 8, 14, 1, 1, tzinfo=timezone.utc))
    with pytest.raises(ValueError, match="run_id"):
        backend.publish_artifact("rank", {**artifact, "run_id": "bad/run"})
    with pytest.raises(ValueError, match="date"):
        backend.publish_artifact("rank", {**artifact, "business_date": "14-08-2026"})
    with pytest.raises(ValueError, match="incoherent"):
        backend.publish_artifact("rank", {**artifact, "reason_code": "WEEKEND"})
    with pytest.raises(ValueError, match="incoherent"):
        backend.publish_artifact("rank", {**artifact, "status": "SKIPPED", "reason_code": "UNKNOWN_CALENDAR"})


def test_derived_scheduler_health_fails_enabled_job_failure_and_coverage():
    now = datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc)
    contracts = [
        ("genesis-system3-forecast-daily", "ENABLED", "genesis-system3-forecast", "0 4 * * MON-FRI", "UTC"),
        ("genesis-system3-rank-daily", "ENABLED", "genesis-system3-rank", "45 3 * * MON-FRI", "UTC"),
        ("genesis-system3-validate-daily", "ENABLED", "genesis-system3-validate", "5 10 * * MON-FRI", "UTC"),
        ("genesis-system3-signals-daily", "ENABLED", "genesis-system3-signals", "15 13 * * MON-FRI", "UTC"),
        ("genesis-system3-dhan-token-rotate-daily", "ENABLED", "genesis-system3-dhan-token-rotate", "30 * * * *", "Asia/Kolkata"),
        ("genesis-system3-forecast-schedule", "PAUSED", "genesis-system3-forecast", "0 4,5,6,7,8,9 * * 1-5", "UTC"),
        ("genesis-system3-rank-schedule", "PAUSED", "genesis-system3-rank", "50 3 * * 1-5", "UTC"),
        ("genesis-system3-signals-schedule", "PAUSED", "genesis-system3-signals", "0 10 * * 1-5", "UTC"),
        ("genesis-system3-scheduler-collector-every-minute", "ENABLED", "genesis-system3-scheduler-collector", "* * * * *", "UTC"),
    ]
    resources = [{"name": n, "state": s, "target_job": t if s == "ENABLED" else None, "schedule": schedule, "time_zone": zone, "target_type": "http", "target_uri_valid": True, "delivery_status_code": 0, "last_attempt_time": "2026-08-14T00:58:00Z"} for n, s, t, schedule, zone in contracts]
    jobs = [{"name": t, "completion_status": "EXECUTION_SUCCEEDED", "create_time": "2026-08-14T00:58:01Z", "completion_time": "2026-08-14T00:59:00Z"} for t in sorted({row[2] for row in contracts if row[1] == "ENABLED"})]
    good = derive_scheduler_health({"observed_at_utc": "2026-08-14T01:00:00Z", "resources": resources, "jobs": jobs}, now=now)
    assert good["healthy"] is True
    assert good["coverage"]["expected_total"] == 9
    rank_job = next(row for row in jobs if row["name"] == "genesis-system3-rank")
    rank_res = next(row for row in resources if row["name"] == "genesis-system3-rank-daily")
    rank_job["completion_status"] = "EXECUTION_FAILED"
    bad = derive_scheduler_health({"observed_at_utc": "2026-08-14T01:00:00Z", "resources": resources, "jobs": jobs}, now=now)
    assert bad["healthy"] is False and "failed" in " ".join(bad["unhealthy_reasons"])
    rank_job["completion_status"] = "EXECUTION_SUCCEEDED"; rank_job["create_time"] = None
    missing_time = derive_scheduler_health({"observed_at_utc": "2026-08-14T01:00:00Z", "resources": resources, "jobs": jobs}, now=now)
    assert missing_time["healthy"] is False and "timestamps invalid" in " ".join(missing_time["unhealthy_reasons"])

    rank_job["create_time"] = "2026-08-14T01:02:00Z"; rank_job["completion_time"] = "2026-08-14T01:03:00Z"
    future = derive_scheduler_health({"observed_at_utc": "2026-08-14T01:00:00Z", "resources": resources, "jobs": jobs}, now=now)
    assert "materially future" in " ".join(future["unhealthy_reasons"])
    rank_job["create_time"] = "2026-08-09T00:58:01Z"; rank_job["completion_time"] = "2026-08-09T00:59:00Z"; rank_res["last_attempt_time"] = "2026-08-09T00:58:00Z"
    stale = derive_scheduler_health({"observed_at_utc": "2026-08-14T01:00:00Z", "resources": resources, "jobs": jobs}, now=now)
    assert "stale beyond cadence" in " ".join(stale["unhealthy_reasons"])


def test_derived_health_allows_pending_first_run_and_historical_success():
    now = datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc)
    resources = [
        {"name": "genesis-system3-forecast-daily", "state": "ENABLED", "target_job": "genesis-system3-forecast", "schedule": "0 4 * * MON-FRI", "time_zone": "UTC", "target_type": "http", "target_uri_valid": True, "delivery_status_code": 0, "last_attempt_time": "2026-08-13T04:00:00Z"},
        {"name": "genesis-system3-rank-daily", "state": "ENABLED", "target_job": "genesis-system3-rank", "schedule": "45 3 * * MON-FRI", "time_zone": "UTC", "target_type": "http", "target_uri_valid": True, "delivery_status_code": 0, "last_attempt_time": "2026-08-13T03:45:00Z"},
        {"name": "genesis-system3-validate-daily", "state": "ENABLED", "target_job": "genesis-system3-validate", "schedule": "5 10 * * MON-FRI", "time_zone": "UTC", "target_type": "http", "target_uri_valid": True, "delivery_status_code": -1, "last_attempt_time": None},
        {"name": "genesis-system3-signals-daily", "state": "ENABLED", "target_job": "genesis-system3-signals", "schedule": "15 13 * * MON-FRI", "time_zone": "UTC", "target_type": "http", "target_uri_valid": True, "delivery_status_code": 0, "last_attempt_time": "2026-08-13T13:15:00Z"},
        {"name": "genesis-system3-dhan-token-rotate-daily", "state": "ENABLED", "target_job": "genesis-system3-dhan-token-rotate", "schedule": "30 * * * *", "time_zone": "Asia/Kolkata", "target_type": "http", "target_uri_valid": True, "delivery_status_code": 0, "last_attempt_time": "2026-08-14T00:58:00Z"},
        {"name": "genesis-system3-forecast-schedule", "state": "PAUSED", "target_job": None, "schedule": "0 4,5,6,7,8,9 * * 1-5", "time_zone": "UTC", "target_type": "missing", "target_uri_valid": False},
        {"name": "genesis-system3-rank-schedule", "state": "PAUSED", "target_job": None, "schedule": "50 3 * * 1-5", "time_zone": "UTC", "target_type": "missing", "target_uri_valid": False},
        {"name": "genesis-system3-signals-schedule", "state": "PAUSED", "target_job": None, "schedule": "0 10 * * 1-5", "time_zone": "UTC", "target_type": "missing", "target_uri_valid": False},
        {"name": "genesis-system3-scheduler-collector-every-minute", "state": "ENABLED", "target_job": "genesis-system3-scheduler-collector", "schedule": "* * * * *", "time_zone": "UTC", "target_type": "http", "target_uri_valid": True, "delivery_status_code": 0, "last_attempt_time": "2026-08-14T00:59:00Z"},
    ]
    jobs = [
        {"name": "genesis-system3-forecast", "completion_status": "EXECUTION_SUCCEEDED", "create_time": "2026-08-13T22:00:00Z", "completion_time": "2026-08-13T22:01:00Z", "evidence_role": "last_succeeded_within_history"},
        {"name": "genesis-system3-rank", "completion_status": "EXECUTION_SUCCEEDED", "create_time": "2026-08-13T22:00:00Z", "completion_time": "2026-08-13T22:01:00Z", "evidence_role": "last_succeeded_within_history"},
        {"name": "genesis-system3-validate", "completion_status": "MISSING"},
        {"name": "genesis-system3-signals", "completion_status": "EXECUTION_SUCCEEDED", "create_time": "2026-08-13T22:00:00Z", "completion_time": "2026-08-13T22:01:00Z", "evidence_role": "last_succeeded_within_history"},
        {"name": "genesis-system3-dhan-token-rotate", "completion_status": "EXECUTION_SUCCEEDED", "create_time": "2026-08-14T00:58:01Z", "completion_time": "2026-08-14T00:59:00Z"},
        {"name": "genesis-system3-scheduler-collector", "completion_status": "EXECUTION_SUCCEEDED", "create_time": "2026-08-14T00:58:01Z", "completion_time": "2026-08-14T00:59:00Z"},
    ]
    result = derive_scheduler_health({"observed_at_utc": "2026-08-14T01:00:00Z", "resources": resources, "jobs": jobs}, now=now)
    assert result["healthy"] is True
    assert result["coverage"]["total"] == 9

    # Manual/bootstrap validate success before first scheduler delivery must not fail.
    jobs_boot = [dict(row) for row in jobs]
    for row in jobs_boot:
        if row["name"] == "genesis-system3-validate":
            row.update({
                "completion_status": "EXECUTION_SUCCEEDED",
                "create_time": "2026-08-13T22:00:00Z",
                "completion_time": "2026-08-13T22:01:00Z",
                "evidence_role": "latest_created_execution",
            })
    boot = derive_scheduler_health({"observed_at_utc": "2026-08-14T01:00:00Z", "resources": resources, "jobs": jobs_boot}, now=now)
    assert boot["healthy"] is True


def test_derived_health_rejects_duplicate_and_swapped_target():
    now = datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc)
    resources = [
        {"name": "genesis-system3-forecast-daily", "state": "ENABLED", "target_job": "genesis-system3-rank", "target_type": "http", "target_uri_valid": True, "delivery_status_code": 0},
        {"name": "genesis-system3-forecast-daily", "state": "ENABLED", "target_job": "genesis-system3-forecast", "target_type": "http", "target_uri_valid": True, "delivery_status_code": 0},
    ]
    result = derive_scheduler_health({"observed_at_utc": "2026-08-14T01:00:00Z", "resources": resources, "jobs": []}, now=now)
    assert result["healthy"] is False
    assert "duplicate" in " ".join(result["unhealthy_reasons"])
    assert "contract mismatch" in " ".join(result["unhealthy_reasons"])


def test_paused_legacy_schedulers_do_not_require_runtime_target_uri():
    now = datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc)
    # A paused legacy scheduler's API omits httpTarget; this is N/A, not broken.
    row = {"name": "genesis-system3-forecast-schedule", "state": "PAUSED", "target_job": None, "target_type": "missing", "target_uri_valid": False, "schedule": "0 4,5,6,7,8,9 * * 1-5", "time_zone": "UTC"}
    evidence = {"observed_at_utc": "2026-08-14T01:00:00Z", "resources": [row], "jobs": []}
    result = derive_scheduler_health(evidence, now=now)
    joined = " ".join(result["unhealthy_reasons"])
    assert "target type invalid: genesis-system3-forecast-schedule" not in joined
    assert "target URI invalid: genesis-system3-forecast-schedule" not in joined
