from datetime import date
from hashlib import sha256

import pytest

from scripts.cepe_next_open_proof import compare


PREVIOUS = (
    b"TckrSymb,XpryDt,OptnTp,StrkPric,OpnPric,ClsPric,TradDt\n"
    b"NIFTY,2026-09-30,CE,25000,8,10,2026-09-22\n"
    b"NIFTY,2026-09-30,PE,25000,20,15,2026-09-22\n"
)
FOLLOWING = (
    b"TckrSymb,XpryDt,OptnTp,StrkPric,OpnPric,ClsPric,TradDt\n"
    b"NIFTY,2026-09-30,CE,25000,110,80,2026-09-23\n"
    b"NIFTY,2026-09-30,PE,25000,3,7,2026-09-23\n"
)


def test_contract_identity_and_opening_multiplier():
    result = compare(PREVIOUS, FOLLOWING, date(2026, 9, 22), date(2026, 9, 23))
    assert result["example_threshold_counts"] == {"3": 1, "10": 1, "20": 0, "30": 0}
    assert result["matched_contracts"] == 2
    assert result["highest_multiple"] == 11.0
    assert result["top_moves"][0]["type"] == "CE"
    assert result["following_sha256"] == sha256(FOLLOWING).hexdigest()
    assert result["prediction_accuracy_proven"] is False


def test_wrong_date_and_duplicate_contract_fail_closed():
    with pytest.raises(ValueError, match="Trade date"):
        compare(PREVIOUS, FOLLOWING, date(2026, 9, 21), date(2026, 9, 23))
    duplicated = PREVIOUS + PREVIOUS.split(b"\n")[1] + b"\n"
    with pytest.raises(ValueError, match="Duplicate"):
        compare(duplicated, FOLLOWING, date(2026, 9, 22), date(2026, 9, 23))
