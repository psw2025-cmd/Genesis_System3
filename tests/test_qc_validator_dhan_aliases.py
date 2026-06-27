import pandas as pd

from src.validation.qc_validator import QCValidator


def _base_rows(**overrides):
    rows = []
    for i in range(50):
        row = {
            "ltp": 100.0,
            "strike": 22000 + i * 50,
            "option_type": "CE" if i % 2 == 0 else "PE",
            "spot_price": 23000.0,
            "iv": 0.2,
            "bidPrice": 99.0,
            "offerPrice": 101.0,
        }
        row.update(overrides)
        rows.append(row)
    return pd.DataFrame(rows)


def _has_ask_bid_failure(reasons):
    return any("ask < bid" in reason for reason in reasons)


def test_paper_sanity_mode_initializes_without_exception():
    validator = QCValidator(paper_sanity_mode=True)

    assert validator.paper_sanity_mode is True


def test_paper_sanity_mode_reduces_underlying_thresholds_after_initialization():
    validator = QCValidator(paper_sanity_mode=True)

    assert validator.underlying_min_contracts["NIFTY"] == 40
    assert validator.underlying_min_contracts["SENSEX"] == 24
    assert validator.min_data_completeness == 0.6


def test_legacy_bid_offer_ask_below_bid_is_detected():
    df = _base_rows(bidPrice=101.0, offerPrice=100.0)
    passed, reasons = QCValidator().validate_snapshot(df, "NIFTY")

    assert not passed
    assert _has_ask_bid_failure(reasons)


def test_dhan_top_bid_ask_ask_below_bid_is_detected():
    df = _base_rows()
    df = df.drop(columns=["bidPrice", "offerPrice"])
    df["top_bid_price"] = 101.0
    df["top_ask_price"] = 100.0

    passed, reasons = QCValidator().validate_snapshot(df, "NIFTY")

    assert not passed
    assert _has_ask_bid_failure(reasons)


def test_simple_bid_ask_ask_below_bid_is_detected():
    df = _base_rows()
    df = df.drop(columns=["bidPrice", "offerPrice"])
    df["bid"] = 101.0
    df["ask"] = 100.0

    passed, reasons = QCValidator().validate_snapshot(df, "NIFTY")

    assert not passed
    assert _has_ask_bid_failure(reasons)


def test_valid_dhan_top_bid_ask_does_not_create_bid_ask_failure():
    df = _base_rows()
    df = df.drop(columns=["bidPrice", "offerPrice"])
    df["top_bid_price"] = 99.0
    df["top_ask_price"] = 101.0

    passed, reasons = QCValidator().validate_snapshot(df, "NIFTY")

    assert passed
    assert not _has_ask_bid_failure(reasons)


def test_missing_bid_ask_does_not_crash_or_create_bid_ask_failure():
    df = _base_rows().drop(columns=["bidPrice", "offerPrice"])

    passed, reasons = QCValidator().validate_snapshot(df, "NIFTY")

    assert passed
    assert not _has_ask_bid_failure(reasons)


def test_oi_aliases_are_normalized_without_crash():
    validator = QCValidator()

    for alias in ["dOI", "oi_change", "change_in_oi"]:
        df = pd.DataFrame({alias: [1, -2, 3]})
        normalized = validator.normalize_oi_change_alias(df)
        assert normalized.tolist() == [1, -2, 3]
