import pytest

from core.data.market_data_failover import (
    MarketDataFailoverRouter,
    MarketDataUnavailable,
    ProviderSpec,
    ProviderTier,
)


def _provider(name, tier, fn, *, broker=True, priority=10, supports=frozenset({"quote"})):
    return ProviderSpec(name=name, tier=tier, fetch=fn, broker_backed=broker, priority=priority, supports=supports)


def test_primary_success_is_authoritative_and_not_degraded():
    router = MarketDataFailoverRouter([
        _provider("dhan_ws", ProviderTier.PRIMARY_BROKER, lambda req: {"ltp": 100.0})
    ], production=True)
    result = router.fetch("quote", {"symbol": "NIFTY"})
    assert result.provider == "dhan_ws"
    assert result.authoritative is True
    assert result.degraded is False
    assert result.stale is False


def test_secondary_broker_is_used_after_primary_failure_and_marked_degraded():
    def fail(_):
        raise TimeoutError("ws stalled")

    router = MarketDataFailoverRouter([
        _provider("dhan_ws", ProviderTier.PRIMARY_BROKER, fail, priority=1),
        _provider("secondary", ProviderTier.SECONDARY_BROKER, lambda req: {"ltp": 101.0}, priority=2),
    ], production=True)
    result = router.fetch("quote", {"symbol": "NIFTY"})
    assert result.provider == "secondary"
    assert result.broker_backed is True
    assert result.authoritative is False
    assert result.degraded is True
    assert result.attempts[0]["status"] == "failed"


def test_exchange_validation_is_not_silently_used_when_broker_required():
    router = MarketDataFailoverRouter([
        _provider("nse", ProviderTier.EXCHANGE_VALIDATION, lambda req: {"ltp": 100}, broker=False)
    ], production=True)
    with pytest.raises(MarketDataUnavailable):
        router.fetch("quote", {"symbol": "NIFTY"}, require_broker=True)


def test_exchange_validation_can_be_explicitly_selected_for_degraded_validation():
    router = MarketDataFailoverRouter([
        _provider("nse", ProviderTier.EXCHANGE_VALIDATION, lambda req: {"ltp": 100}, broker=False)
    ], production=True)
    result = router.fetch("quote", {"symbol": "NIFTY"}, require_broker=False)
    assert result.provider == "nse"
    assert result.authoritative is False
    assert result.degraded is True


def test_last_known_good_is_explicitly_stale():
    router = MarketDataFailoverRouter([
        _provider("dhan_cache", ProviderTier.LAST_KNOWN_GOOD, lambda req: {"ltp": 99}, broker=True)
    ], production=True)
    result = router.fetch("quote", {"symbol": "NIFTY"})
    assert result.stale is True
    assert result.degraded is True
    assert result.authoritative is False


def test_stale_can_be_rejected():
    router = MarketDataFailoverRouter([
        _provider("dhan_cache", ProviderTier.LAST_KNOWN_GOOD, lambda req: {"ltp": 99}, broker=True)
    ], production=True)
    with pytest.raises(MarketDataUnavailable):
        router.fetch("quote", {"symbol": "NIFTY"}, allow_stale=False)


def test_test_only_provider_is_blocked_in_production():
    router = MarketDataFailoverRouter([
        _provider("synthetic", ProviderTier.TEST_ONLY, lambda req: {"ltp": 1}, broker=False)
    ], production=True)
    with pytest.raises(MarketDataUnavailable):
        router.fetch("quote", {"symbol": "NIFTY"}, require_broker=False)


def test_circuit_breaker_skips_repeatedly_failing_provider():
    calls = {"primary": 0}

    def fail(_):
        calls["primary"] += 1
        raise TimeoutError("down")

    router = MarketDataFailoverRouter([
        _provider("dhan_ws", ProviderTier.PRIMARY_BROKER, fail, priority=1),
        _provider("dhan_rest", ProviderTier.PRIMARY_BROKER, lambda req: {"ltp": 100}, priority=2),
    ], production=True, failure_threshold=1, circuit_open_s=60)
    first = router.fetch("quote", {"symbol": "NIFTY"})
    second = router.fetch("quote", {"symbol": "NIFTY"})
    assert first.provider == "dhan_rest"
    assert second.provider == "dhan_rest"
    assert calls["primary"] == 1
    assert second.attempts[0]["status"] == "circuit_open"


def test_empty_payload_falls_through_to_next_provider():
    router = MarketDataFailoverRouter([
        _provider("dhan_ws", ProviderTier.PRIMARY_BROKER, lambda req: {}, priority=1),
        _provider("dhan_rest", ProviderTier.PRIMARY_BROKER, lambda req: {"ltp": 100}, priority=2),
    ], production=True)
    result = router.fetch("quote", {"symbol": "NIFTY"})
    assert result.provider == "dhan_rest"
    assert result.degraded is True


def test_capability_filter_routes_to_matching_provider():
    router = MarketDataFailoverRouter([
        _provider("quotes", ProviderTier.PRIMARY_BROKER, lambda req: {"ltp": 100}, supports=frozenset({"quote"})),
        _provider("chain", ProviderTier.PRIMARY_BROKER, lambda req: {"strikes": [1]}, priority=2, supports=frozenset({"option_chain"})),
    ], production=True)
    result = router.fetch("option_chain", {"symbol": "NIFTY"})
    assert result.provider == "chain"
