def test_tradeable_fo_symbol():
    from core.brokers.dhan.equity_fo_universe import is_tradeable_fo_symbol

    assert is_tradeable_fo_symbol("NIFTY") is True
    assert is_tradeable_fo_symbol("RELIANCE") is True
    assert is_tradeable_fo_symbol("RANDOMCASH") is False
