from core.brokers.dhan.first_rejection_trace import (
    _reset_for_tests,
    record_auth_rejection,
    snapshot,
)


def setup_function():
    _reset_for_tests()


def test_first_rejection_is_latched_and_not_overwritten():
    first = record_auth_rejection(
        secret_version="260",
        auth_classification="DHAN_TOKEN_REJECTED",
        http_status=401,
        upstream_code=808,
    )
    second = record_auth_rejection(
        secret_version="261",
        auth_classification="TOKEN_CLOCK_EXPIRED",
        http_status=400,
        upstream_code=906,
    )

    assert first["secret_version"] == "260"
    assert second["secret_version"] == "260"
    assert second["auth_classification"] == "DHAN_TOKEN_REJECTED"
    assert second["http_status"] == 401
    assert second["upstream_code"] == 808
    assert second["rejection_count"] == 2
    assert second["first_rejected_at_utc"]
    assert second["last_rejected_at_utc"]
    assert second["raw_token_exposed"] is False
    assert second["client_id_exposed"] is False


def test_snapshot_is_empty_before_rejection():
    proof = snapshot()
    assert proof["rejection_count"] == 0
    assert proof["first_rejected_at_utc"] is None
    assert proof["secret_version"] is None
