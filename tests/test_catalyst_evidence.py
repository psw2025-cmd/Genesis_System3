"""Fixture-only checks for point-in-time catalyst evidence.

These tests verify evidence arithmetic and guards. They are not historical market
validation and contain no claim of predictive skill.
"""
from hashlib import sha256

import pytest

from dashboard.backend.catalyst_evidence import (
    CatalystEvidenceError,
    build_catalyst_record,
    measure_later_return,
)


RAW_FILING = b"NSE fixture announcement; not a real filing"
RAW_HASH = sha256(RAW_FILING).hexdigest()
BASE_METADATA = {
    "symbol": "EXAMPLE",
    "isin": "INE000A01001",
    "source_url": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
    "source_sha256": RAW_HASH,
    "published_at": "2026-09-24T09:00:00+05:30",
    "disseminated_at": "2026-09-24T09:01:00+05:30",
    "first_observed_at": "2026-09-24T09:02:00+05:30",
    "category": "ORDER_CONTRACT",
}
ISSUED_AT = "2026-09-24T09:05:00+05:30"
OUTCOME_BYTES = b"NSE fixture adjusted closes: EXAMPLE,100,110"
OUTCOME_HASH = sha256(OUTCOME_BYTES).hexdigest()


def _record(**metadata_overrides):
    return build_catalyst_record(
        RAW_FILING,
        {**BASE_METADATA, **metadata_overrides},
        prediction_issued_at=ISSUED_AT,
    )


def test_seals_official_pre_issue_filing_as_eligible_without_causal_claim():
    record = _record()

    assert record["source_sha256"] == RAW_HASH
    assert record["known_by_prediction_issue_time"] is True
    assert record["feature_eligible"] is True
    assert record["causal_attribution"] == "NOT_CLAIMED"
    assert len(record["record_hash"]) == 64
    assert record["live_trading_enabled"] is False
    assert record["order_placement_allowed"] is False


def test_post_issue_catalyst_is_preserved_but_cannot_enter_prediction():
    record = _record(first_observed_at="2026-09-24T09:06:00+05:30")

    assert record["feature_eligible"] is False
    measured = measure_later_return(record, {})
    assert measured == {
        "status": "NOT_PROVEN",
        "reason": "POST_ISSUE_CATALYST_NOT_ELIGIBLE",
    }


@pytest.mark.parametrize(
    ("override", "reason"),
    [
        ({"source_url": "https://example.com/filing"}, "SOURCE_URL_NOT_OFFICIAL_NSE_BSE"),
        ({"source_sha256": "0" * 64}, "SOURCE_HASH_MISMATCH"),
    ],
)
def test_rejects_unofficial_or_hash_mismatched_source(override, reason):
    with pytest.raises(CatalystEvidenceError, match=reason):
        _record(**override)


def test_tampered_catalyst_is_not_scoreable():
    record = _record()
    record["category"] = "EARNINGS"

    assert measure_later_return(record, {}) == {
        "status": "NOT_PROVEN",
        "reason": "CATALYST_RECORD_TAMPERED",
    }


def test_measures_later_adjusted_return_as_correlation_only():
    result = measure_later_return(
        _record(),
        {
            "symbol": "EXAMPLE",
            "source": "NSE",
            "source_snapshot": OUTCOME_BYTES,
            "source_sha256": OUTCOME_HASH,
            "entry_observed_at": "2026-09-24T03:30:00+00:00",
            "exit_observed_at": "2026-10-01T03:40:00+00:00",
            "entry_adjusted_close": 100,
            "exit_adjusted_close": 110,
        },
    )

    assert result["status"] == "MEASURED_CORRELATION_ONLY"
    assert result["adjusted_return_pct"] == 10.0
    assert result["causal_attribution"] == "NOT_CLAIMED"
    assert result["outcome_source_sha256"] == OUTCOME_HASH
    assert result["live_trading_enabled"] is False
    assert result["order_placement_allowed"] is False
