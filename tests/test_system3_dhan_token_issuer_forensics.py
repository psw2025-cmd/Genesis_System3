from scripts.system3_dhan_token_issuer_forensics import EXPECTED_WRITER, correlate


def _version():
    return {"createTime": "2026-08-21T02:00:16Z"}


def test_canonical_writer_is_proven_from_audit_principal():
    event = {"timestamp": "2026-08-21T02:00:17Z", "protoPayload": {
        "authenticationInfo": {"principalEmail": EXPECTED_WRITER}}}
    assert correlate(_version(), [], [event])["verdict"] == "CANONICAL_WRITER_PROVEN"


def test_unexpected_writer_is_not_mislabeled_canonical():
    event = {"timestamp": "2026-08-21T02:00:17Z", "protoPayload": {
        "authenticationInfo": {"principalEmail": "person@example.com"}}}
    assert correlate(_version(), [], [event])["verdict"] == "UNEXPECTED_GCP_WRITER_PROVEN"


def test_execution_timestamp_without_audit_is_only_a_time_match():
    execution = {"metadata": {"name": "rotate-abc"}, "status": {
        "startTime": "2026-08-21T02:00:00Z", "completionTime": "2026-08-21T02:00:30Z"}}
    assert correlate(_version(), [execution], [])["verdict"] == "CANONICAL_EXECUTION_TIME_MATCH_ONLY"


def test_missing_evidence_stays_unattributed():
    assert correlate(_version(), [], [])["verdict"] == "UNATTRIBUTED_GCP_VERSION"
