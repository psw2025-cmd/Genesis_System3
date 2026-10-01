"""Synthetic no-match contract checks; these do not validate market returns."""
from copy import deepcopy
from hashlib import sha256
import json

import pytest

from scripts.catalyst_feed_inspection import (
    URL,
    build_no_match_inspection,
    validate_no_match_inspection,
)


RAW = json.dumps([
    {"symbol": "OTHER", "sm_isin": "INE000A01001", "exchdisstime": "01-Oct-2026 17:00:00"}
]).encode()
RECEIPT = {
    "url": URL,
    "final_url": URL,
    "http_status": 200,
    "raw_sha256": sha256(RAW).hexdigest(),
    "bytes": len(RAW),
    "first_observed_at": "2026-10-01T12:48:59Z",
}


def build(**kwargs):
    return build_no_match_inspection(
        kwargs.pop("raw", RAW),
        kwargs.pop("receipt", RECEIPT),
        symbol=kwargs.pop("symbol", "MOLBIO"),
        isin=kwargs.pop("isin", "INE869T01028"),
        prediction_id="EQ7D-2026-10-01-MOLBIO-V1",
        prediction_event_hash="9" * 64,
        prediction_issued_at=kwargs.pop("issued", "2026-10-01T12:44:51Z"),
    )


def test_seals_post_issue_no_match_without_absence_or_feature_claim():
    result = build()
    assert result["captured_feed_rows"] == 1
    assert result["exact_symbol_or_isin_matches"] == 0
    assert result["published_at"] is result["disseminated_at"] is None
    assert result["known_by_prediction_issue_time"] is False
    assert result["feature_eligible"] is False
    assert result["interpretation"].endswith("NOT_PROOF_OF_ABSENCE")
    assert validate_no_match_inspection(result)["orders_allowed"] is False


def test_exact_match_requires_filing_level_workflow():
    raw = json.dumps([{"symbol": "MOLBIO", "sm_isin": "INE869T01028"}]).encode()
    receipt = dict(RECEIPT, raw_sha256=sha256(raw).hexdigest(), bytes=len(raw))
    with pytest.raises(ValueError, match="filing-level"):
        build(raw=raw, receipt=receipt)


def test_receipt_and_chronology_fail_closed():
    with pytest.raises(ValueError, match="receipt mismatch"):
        build(receipt=dict(RECEIPT, raw_sha256="0" * 64))
    with pytest.raises(ValueError, match="post-issue"):
        build(issued="2026-10-01T12:49:00Z")


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("feature_eligible", True, "prediction feature"),
        ("published_at", "2026-10-01T12:00:00Z", "invent"),
        ("catalyst_contribution", "POSITIVE", "outcome"),
        ("causal_attribution", "CLAIMED", "Causality"),
        ("orders_allowed", True, "Unsafe"),
    ],
)
def test_tampering_cannot_promote_no_match_record(field, value, match):
    result = build()
    result[field] = value
    # Rehash to prove semantic guards, not only content integrity, catch promotion.
    payload = {key: item for key, item in result.items() if key != "record_hash"}
    result["record_hash"] = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    with pytest.raises(ValueError, match=match):
        validate_no_match_inspection(result)


def test_unrehased_mutation_is_detected():
    result = build()
    result["captured_feed_rows"] = 999
    with pytest.raises(ValueError, match="hash mismatch"):
        validate_no_match_inspection(result)
