from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import pytest

from scripts.catalyst_horizon_filing import validate


REPO_ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = (
    REPO_ROOT
    / "research/evidence/catalyst/2026-10-11_MOLBIO_horizon_filing.json"
)


def _record():
    return json.loads(RECORD_PATH.read_text(encoding="utf-8"))


def _rehash(record):
    payload = {key: value for key, value in record.items() if key != "record_hash"}
    record["record_hash"] = sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def test_real_post_issue_horizon_filing_replays_without_backfill():
    result = validate(_record(), repo_root=REPO_ROOT)
    assert result == {
        "task_id": "CAT-LINK-013",
        "status": "POST_ISSUE_HORIZON_FILING_RETAINED_NOT_BACKFILLED",
        "exact_horizon_filings": 1,
        "eligible_catalyst_features_at_issue": 0,
        "matured_adjusted_outcomes": 0,
        "catalyst_contribution": "NOT_PROVEN",
        "orders_allowed": False,
    }


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("known_by_prediction_issue_time", True, "backfilled or promoted"),
        ("feature_eligible", True, "backfilled or promoted"),
        ("source_backfilled_into_prediction", True, "backfilled or promoted"),
    ],
)
def test_rehashed_hindsight_feature_claim_fails_closed(field, value, message):
    record = _record()
    record["feature_eligibility"][field] = value
    _rehash(record)
    with pytest.raises(ValueError, match=message):
        validate(record, repo_root=REPO_ROOT)


def test_rehashed_causal_claim_fails_closed():
    record = _record()
    record["ablation"]["causal_attribution"] = "CAUSED_RETURN"
    _rehash(record)
    with pytest.raises(ValueError, match="attribution was overstated"):
        validate(record, repo_root=REPO_ROOT)


def test_rehashed_adjusted_outcome_claim_fails_closed():
    record = _record()
    record["later_horizon_reference"]["adjusted_outcome_proven"] = True
    _rehash(record)
    with pytest.raises(ValueError, match="horizon reference changed"):
        validate(record, repo_root=REPO_ROOT)


def test_record_hash_covers_nested_evidence():
    record = deepcopy(_record())
    record["attachment"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="record hash mismatch"):
        validate(record, repo_root=REPO_ROOT)
