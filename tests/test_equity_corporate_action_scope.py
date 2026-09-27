from datetime import date
from hashlib import sha256
import json
import pytest
from scripts.equity_corporate_action_scope import capture,review


def source():
    row=dict(symbol="ABC",isin="NEWISIN",exDate="02-Jan-2026",subject="Face Value Split")
    raw=json.dumps([row,row]).encode()
    receipt=dict(source_url="https://www.nseindia.com/api/corporates-corporateActions?index=equities&from_date=01-01-2026&to_date=31-01-2026",raw_sha256=sha256(raw).hexdigest(),first_observed_at="2026-09-27T00:00:00Z")
    return raw,receipt


def test_changed_isin_is_flagged_without_dropping_or_adjusting_outcome():
    raw,receipt=source();scope=capture(raw,receipt)
    result=review(scope,"ABC","OLDISIN",date(2026,1,1),date(2026,1,2))
    assert result["action_count"] == 1 and scope["unique_records"] == 1
    assert result["identity_link_review_required"] is True
    assert result["adjusted_return_proven"] is False
    assert result["use_as_historical_prediction_feature_allowed"] is False


def test_ex_date_boundary_and_absence_never_prove_complete_coverage():
    raw,receipt=source();scope=capture(raw,receipt)
    result=review(scope,"ABC","NEWISIN",date(2026,1,2),date(2026,1,3))
    assert result["action_count"] == 0
    assert "NOT_PROVEN" in result["status"]
    assert not review(scope,"ABC","NEWISIN",date(2026,1,2),date(2026,2,2))["requested_interval_covered"]


def test_source_hash_and_timezone_required():
    raw,receipt=source()
    with pytest.raises(ValueError): capture(raw+b" ",receipt)
    receipt["first_observed_at"]="2026-09-27T00:00:00"
    with pytest.raises(ValueError,match="timezone"): capture(raw,receipt)


def test_replay_flags_changed_isin_even_when_outcome_is_unmatched():
    from scripts.equity_horizon_replay import replay
    raw,receipt=source();scope=capture(raw,receipt)
    header=b"TradDt,ISIN,TckrSymb,SctySrs,ClsPric,TtlTradgVol\n"
    snapshots=[(date(2026,1,1),header+b"2026-01-01,OLDISIN,ABC,EQ,100,20000\n"),
               (date(2026,1,8),header+b"2026-01-08,NEWISIN,ABC,EQ,50,20000\n")]
    plain=replay(snapshots)
    guarded=replay(snapshots,corporate_action_scope=scope)
    assert plain["decisions"][0]["selected_keys_sha256"] == guarded["decisions"][0]["selected_keys_sha256"]
    outcome=guarded["decisions"][0]["horizons"]["7"]
    assert outcome["matched"] == 0 and outcome["delisted_or_missing"] == 1
    assert outcome["corporate_action_review"]["unmatched_with_events"] == 1
    assert outcome["corporate_action_review"]["identity_links_requiring_review"] == 1
