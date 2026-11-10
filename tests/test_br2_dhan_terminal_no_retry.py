from core.data import datasource_manager as dsm_mod
from core.data.datasource_manager import DataSourceManager, _dhan_non_success_codes


class _FakeDhan:
    def __init__(self, responses):
        self.responses = list(responses)
        self.option_chain_calls = 0

    def option_chain(self, **_kwargs):
        self.option_chain_calls += 1
        if self.responses:
            return self.responses.pop(0)
        return {"status": "failure", "remarks": "unexpected extra call"}


def _manager(fake):
    manager = DataSourceManager()
    manager._client = fake
    manager._resolve_underlying = lambda _sym: (13, "IDX_I")
    return manager


def test_extracts_nested_rate_limit_and_auth_codes_without_market_number_false_positive():
    assert _dhan_non_success_codes(
        {"status": "failure", "data": {"errorCode": "DH-805", "price": 429.0}}
    ) == {805}
    assert _dhan_non_success_codes(
        {"status": "failure", "error": {"error_code": "906"}, "ltp": 805.0}
    ) == {906}
    assert _dhan_non_success_codes(
        {"status": "failure", "http_status": 429, "data": {"ltp": 805.0}}
    ) == {429}


def test_too_many_requests_prose_is_terminal():
    codes = _dhan_non_success_codes(
        {"status": "failure", "remarks": "Too many requests from market data API"}
    )
    assert 429 in codes
    assert 805 in codes


def test_rate_limit_805_gets_zero_immediate_option_chain_retry(monkeypatch):
    fake = _FakeDhan(
        [{"status": "failure", "remarks": {"error_code": "805", "message": "Too many requests"}}]
    )
    manager = _manager(fake)
    monkeypatch.setattr(dsm_mod, "_pace_dhan_option_chain_call", lambda: None)

    result = manager._fetch_dhan_real("NIFTY", "2026-08-24")

    assert result is None
    assert fake.option_chain_calls == 1


def test_auth_rejection_906_gets_zero_immediate_option_chain_retry(monkeypatch):
    fake = _FakeDhan(
        [{"status": "failure", "data": {"errorCode": "DH-906", "message": "request rejected"}}]
    )
    manager = _manager(fake)
    monkeypatch.setattr(dsm_mod, "_pace_dhan_option_chain_call", lambda: None)

    result = manager._fetch_dhan_real("NIFTY", "2026-08-24")

    assert result is None
    assert fake.option_chain_calls == 1


def test_unknown_non_success_preserves_existing_single_bounded_retry(monkeypatch):
    fake = _FakeDhan(
        [
            {"status": "failure", "remarks": "temporary provider response with no classified code"},
            {"status": "failure", "remarks": "still unavailable"},
        ]
    )
    manager = _manager(fake)
    monkeypatch.setattr(dsm_mod, "_pace_dhan_option_chain_call", lambda: None)

    result = manager._fetch_dhan_real("NIFTY", "2026-08-24")

    assert result is None
    assert fake.option_chain_calls == 2
