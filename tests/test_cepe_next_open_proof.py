from datetime import date
from hashlib import sha256

import pytest

from scripts.cepe_next_open_proof import compare


PREVIOUS = (
    b"TckrSymb,XpryDt,OptnTp,StrkPric,OpnPric,ClsPric,TradDt,TtlTradgVol\n"
    b"NIFTY,2026-09-30,CE,25000,8,10,2026-09-22,200\n"
    b"NIFTY,2026-09-30,PE,25000,20,15,2026-09-22,200\n"
)
FOLLOWING = (
    b"TckrSymb,XpryDt,OptnTp,StrkPric,OpnPric,ClsPric,TradDt,TtlTradgVol\n"
    b"NIFTY,2026-09-30,CE,25000,110,80,2026-09-23,200\n"
    b"NIFTY,2026-09-30,PE,25000,3,7,2026-09-23,200\n"
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
        b"10,2026-09-22,200",
        b"10,2026-09-22,0",
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
        b"110,80,2026-09-23,200",
        bad_value + b",80,2026-09-23,200",
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
