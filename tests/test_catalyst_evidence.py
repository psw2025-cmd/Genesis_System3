from hashlib import sha256

from dashboard.backend.catalyst_evidence import validate_catalyst


RAW = b"Official dated filing snapshot"
EVENT = {
    "symbol": "TEST",
    "event_id": "exchange-announcement-1",
    "published_at": "2026-09-17T10:00:00+05:30",
    "first_observed_at": "2026-09-17T10:01:00+05:30",
    "source_url": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
    "source_sha256": sha256(RAW).hexdigest(),
}


def test_available_catalyst_has_source_integrity_without_causation_claim():
    result = validate_catalyst(EVENT, "2026-09-17T10:02:00+05:30", RAW)
    assert result["status"] == "KNOWN_AT_ISSUE"
    assert result["causal_effect_proven"] is False
    assert result["order_placement_allowed"] is False


def test_rejects_future_observation_tampering_and_unapproved_domain():
    issued = "2026-09-17T10:02:00+05:30"
    assert validate_catalyst(
        {**EVENT, "first_observed_at": "2026-09-17T10:03:00+05:30"}, issued, RAW
    )["reason"] == "CATALYST_NOT_KNOWN_AT_ISSUE"
    assert validate_catalyst(EVENT, issued, b"changed")["reason"] == "SOURCE_HASH_MISMATCH"
    assert validate_catalyst(
        {**EVENT, "source_url": "https://www.nseindia.com.bad.example/post"}, issued, RAW
    )["reason"] == "SOURCE_NOT_OFFICIAL"
