from datetime import date
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts.cepe_next_open_proof import compare


REPO_ROOT = Path(__file__).resolve().parents[1]


def _only_member(path: Path) -> bytes:
    with ZipFile(path) as archive:
        names = archive.namelist()
        assert len(names) == 1
        return archive.read(names[0])


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
    assert result["top_moves"][0]["instrument_id"] == "1"
    assert result["top_moves"][0]["instrument_id_match_proven"] is True
    assert result["instrument_id_proven_matches"] == 2
    assert result["instrument_identity_status"] == (
        "PROVEN_FOR_ALL_MATCHED_CONTRACTS"
    )
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


def test_modern_contract_requires_same_nse_instrument_id_across_sessions():
    substituted = FOLLOWING.replace(
        b"IDO,1,F1,NIFTY",
        b"IDO,999,F1,NIFTY",
        1,
    )
    with pytest.raises(ValueError, match="instrument identifier changed"):
        compare(
            PREVIOUS,
            substituted,
            date(2026, 9, 22),
            date(2026, 9, 23),
        )


def test_mixed_modern_and_legacy_identity_fails_closed():
    legacy = (
        b"SYMBOL,EXPIRY_DT,OPTION_TYP,STRIKE_PR,OPEN,CLOSE,TIMESTAMP,CONTRACTS\n"
        b"NIFTY,30-Sep-2026,CE,25000,110,80,23-Sep-2026,200\n"
    )
    with pytest.raises(ValueError, match="Cannot prove NSE instrument identity"):
        compare(
            PREVIOUS,
            legacy,
            date(2026, 9, 22),
            date(2026, 9, 23),
        )


def test_october_7_to_8_official_full_distribution_replays_exactly():
    previous_path = (
        REPO_ROOT / "research/evidence/cepe/raw/fo_20261007.zip"
    )
    following_path = (
        REPO_ROOT / "research/evidence/cepe/raw/fo_20261008.zip"
    )
    previous_zip = previous_path.read_bytes()
    following_zip = following_path.read_bytes()
    assert sha256(previous_zip).hexdigest() == (
        "676932c7a62c953cd1a82c277a4bb040ace5cd593c661dac4b9030a49c1801df"
    )
    assert sha256(following_zip).hexdigest() == (
        "7223a223f12a5789a33e3018eeeb9f8dc7b5122129902eed23b329241b6bad7d"
    )

    result = compare(
        _only_member(previous_path),
        _only_member(following_path),
        date(2026, 10, 7),
        date(2026, 10, 8),
    )
    assert result["previous_sha256"] == (
        "54774919d0962f213ed6ac3b482c9e4321af3815a421544ed162e26a96d1e2dd"
    )
    assert result["following_sha256"] == (
        "dc3b9a245085b6453dda6f26f5e6027ac71aee11ecbe249e02606197fc3b0cf0"
    )
    assert result["matched_contracts"] == 4613
    assert result["instrument_id_proven_matches"] == 4613
    assert result["excluded_illiquid_contracts"] == 29940
    assert result["highest_multiple"] == 3.657143
    assert result["example_threshold_counts"] == {
        "3": 2,
        "10": 0,
        "20": 0,
        "30": 0,
    }
    assert result["top_moves"][0] == {
        "symbol": "PAYTM",
        "expiry": "2026-10-27",
        "strike": "1560.0000",
        "type": "PE",
        "instrument_id": "100707",
        "instrument_id_match_proven": True,
        "previous_close": 8.75,
        "next_open": 32.0,
        "observed_open": 32.0,
        "multiple": 3.657143,
        "gross_reference_multiple": 3.657143,
        "opening_fill_proven": False,
        "cost_adjusted": False,
    }
    assert result["distribution_scope"] == (
        "FULL_MATCHED_CONTRACT_SET_UNCAPPED"
    )
    assert result["fees_slippage_status"] == "NOT_APPLIED"
    assert result["opening_fill_proven"] is False
    assert result["prediction_accuracy_proven"] is False
    assert result["orders_allowed"] is False
