from hashlib import sha256
import pytest

from scripts.equity_instrument_scope import capture, EQUITY_URL, ETF_URL

COMPANY = b"SYMBOL, ISIN NUMBER, SERIES\nABC,INE000000001,EQ\nB,INE000000002,BE\n"
ETF = b"Symbol,ISINNumber\nGOLD,INF000000001\n"


def receipt(raw, url, at="2026-09-26T12:00:00Z"):
    return dict(url=url, raw_sha256=sha256(raw).hexdigest(), first_observed_at=at)


def snapshot():
    return capture(COMPANY, ETF, equity_receipt=receipt(COMPANY, EQUITY_URL),
                   etf_receipt=receipt(ETF, ETF_URL, "2026-09-26T12:01:00Z"))


def test_exact_identity_and_instrument_type_control_eligibility():
    s = snapshot()
    at = "2026-09-26T12:02:00Z"
    assert s.classify("ABC", "INE000000001", issued_at=at) == "COMPANY_EQ_IDENTITY_MATCHED"
    assert s.classify("GOLD", "INF000000001", issued_at=at) == "ETF_EXCLUDED"
    assert s.classify("B", "INE000000002", issued_at=at) == "COMPANY_NON_EQ_SERIES_EXCLUDED"
    assert s.classify("ABC", "INE000000009", issued_at=at) == "NOT_PROVEN_UNKNOWN_IDENTITY"


def test_later_or_stale_capture_cannot_qualify_prediction():
    s = snapshot()
    assert s.classify("ABC", "INE000000001", issued_at="2026-09-26T12:00:30Z") == "NOT_PROVEN_SOURCE_NOT_YET_OBSERVED"
    assert s.classify("ABC", "INE000000001", issued_at="2026-09-27T12:00:01Z") == "NOT_PROVEN_REFRESH_REQUIRED"
    with pytest.raises(ValueError, match="timezone"):
        s.classify("ABC", "INE000000001", issued_at="2026-09-26T12:02:00")


def test_tampered_raw_or_unofficial_source_rejected():
    with pytest.raises(ValueError, match="hash mismatch"):
        capture(COMPANY + b"C,INE000000003,EQ\n", ETF,
                equity_receipt=receipt(COMPANY, EQUITY_URL), etf_receipt=receipt(ETF, ETF_URL))
    with pytest.raises(ValueError, match="source URL"):
        capture(COMPANY, ETF, equity_receipt=receipt(COMPANY, "https://example.com/data"),
                etf_receipt=receipt(ETF, ETF_URL))


def test_conflicting_classification_rejected_and_receipt_time_bound():
    conflicting = b"Symbol,ISINNumber\nABC,INE000000001\n"
    with pytest.raises(ValueError, match="conflicting"):
        capture(COMPANY, conflicting, equity_receipt=receipt(COMPANY, EQUITY_URL),
                etf_receipt=receipt(conflicting, ETF_URL))
    different = capture(COMPANY, ETF, equity_receipt=receipt(COMPANY, EQUITY_URL),
                        etf_receipt=receipt(ETF, ETF_URL, "2026-09-26T12:02:00Z"))
    assert snapshot().receipt_sha256 != different.receipt_sha256
