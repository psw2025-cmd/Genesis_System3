from datetime import date
from hashlib import sha256

import pytest

from scripts.cepe_next_open_proof import compare


PREVIOUS = (
    b"BizDt,Sgmt,Src,FinInstrmTp,FinInstrmId,SsnId,TckrSymb,XpryDt,OptnTp,"
    b"StrkPric,OpnPric,ClsPric,TradDt,TtlTradgVol\n"
    b"2026-09-22,FO,NSE,IDO,1,F1,NIFTY,2026-09-30,CE,25000,8,10,2026-09-22,200\n"
    b"2026-09-22,FO,NSE,IDO,2,F1,NIFTY,2026-09-30,PE,25000,20,15,2026-09-22,200\n"
)
FOLLOWING = (
    b"BizDt,Sgmt,Src,FinInstrmTp,FinInstrmId,SsnId,TckrSymb,XpryDt,OptnTp,"
    b"StrkPric,OpnPric,ClsPric,TradDt,TtlTradgVol\n"
    b"2026-09-23,FO,NSE,IDO,1,F1,NIFTY,2026-09-30,CE,25000,110,80,2026-09-23,200\n"
    b"2026-09-23,FO,NSE,IDO,2,F1,NIFTY,2026-09-30,PE,25000,3,7,2026-09-23,200\n"
)


def test_contract_identity_and_opening_multiplier():
    result = compare(
        PREVIOUS,
        FOLLOWING,
        date(2026, 9, 22),
        date(2026, 9, 23),
    )
    assert result["example_threshold_counts"] == {
        "3": 1,
        "10": 1,
        "20": 0,
        "30": 0,
    }
    assert result["matched_contracts"] == 2
    assert result["highest_multiple"] == 11.0
    assert result["top_moves"][0]["type"] == "CE"
    assert result["following_sha256"] == sha256(FOLLOWING).hexdigest()
    assert result["distribution_scope"] == "FULL_MATCHED_CONTRACT_SET_UNCAPPED"
    assert result["fees_slippage_status"] == "NOT_APPLIED"
    assert result["opening_fill_proven"] is False
    assert result["prediction_accuracy_proven"] is False


def test_wrong_date_and_duplicate_contract_fail_closed():
    with pytest.raises(ValueError, match="Trade date"):
        compare(
            PREVIOUS,
            FOLLOWING,
            date(2026, 9, 21),
            date(2026, 9, 23),
        )
    duplicated = PREVIOUS + PREVIOUS.split(b"\n")[1] + b"\n"
    with pytest.raises(ValueError, match="Duplicate"):
        compare(
            duplicated,
            FOLLOWING,
            date(2026, 9, 22),
            date(2026, 9, 23),
        )


def test_illiquid_previous_close_is_excluded():
    stale = PREVIOUS.replace(
        b"25000,8,10,2026-09-22,200",
        b"25000,8,10,2026-09-22,0",
    )
    result = compare(
        stale,
        FOLLOWING,
        date(2026, 9, 22),
        date(2026, 9, 23),
    )
    assert result["matched_contracts"] == 1
    assert result["excluded_illiquid_contracts"] == 1
    assert result["highest_multiple"] == 0.2


@pytest.mark.parametrize(
    ("bad_value", "field"),
    [
        (b"nan", "opening price"),
        (b"inf", "opening price"),
        (b"-1", "opening price"),
    ],
)
def test_non_finite_or_negative_market_values_fail_closed(bad_value, field):
    invalid = FOLLOWING.replace(
        b"25000,110,80,2026-09-23,200",
        b"25000," + bad_value + b",80,2026-09-23,200",
    )
    with pytest.raises(ValueError, match=field):
        compare(
            PREVIOUS,
            invalid,
            date(2026, 9, 22),
            date(2026, 9, 23),
        )


def test_invalid_liquidity_thresholds_fail_closed():
    with pytest.raises(ValueError, match="minimum volume"):
        compare(
            PREVIOUS,
            FOLLOWING,
            date(2026, 9, 22),
            date(2026, 9, 23),
            min_volume=float("nan"),
        )


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        (b"FO", b"CM"),
        (b"NSE", b"BSE"),
        (b"IDO", b"STK"),
        (b"F1", b"F2"),
    ],
)
def test_modern_source_identity_mismatch_fails_closed(field, bad_value):
    invalid = PREVIOUS.replace(field, bad_value, 1)
    with pytest.raises(ValueError, match="NSE F&O regular-session option"):
        compare(
            invalid,
            FOLLOWING,
            date(2026, 9, 22),
            date(2026, 9, 23),
        )


def test_modern_schema_requires_provenance_and_business_date():
    minimal = (
        b"TckrSymb,XpryDt,OptnTp,StrkPric,OpnPric,ClsPric,TradDt,TtlTradgVol\n"
        b"NIFTY,2026-09-30,CE,25000,8,10,2026-09-22,200\n"
    )
    with pytest.raises(ValueError, match="missing NSE F&O provenance"):
        compare(
            minimal,
            FOLLOWING,
            date(2026, 9, 22),
            date(2026, 9, 23),
        )

    invalid_business_date = PREVIOUS.replace(b"2026-09-22", b"2026-09-21", 1)
    with pytest.raises(ValueError, match="Business date"):
        compare(
            invalid_business_date,
            FOLLOWING,
            date(2026, 9, 22),
            date(2026, 9, 23),
        )
