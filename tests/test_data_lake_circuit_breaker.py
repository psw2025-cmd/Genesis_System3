import time

from core.data.lake.circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState


def test_starts_closed_and_stays_closed_on_success():
    cb = CircuitBreaker(failure_threshold=3)
    cb.record_success()
    assert cb.state is CircuitState.CLOSED
    cb.guard()  # must not raise


def test_opens_after_threshold_failures():
    cb = CircuitBreaker(failure_threshold=3, reset_timeout_s=10)
    cb.record_failure()
    cb.record_failure()
    assert cb.state is CircuitState.CLOSED
    cb.record_failure()
    assert cb.state is CircuitState.OPEN
    try:
        cb.guard()
        assert False, "expected CircuitOpenError"
    except CircuitOpenError:
        pass


def test_transitions_to_half_open_after_reset_timeout_and_recloses_on_success():
    cb = CircuitBreaker(failure_threshold=1, reset_timeout_s=0.05)
    cb.record_failure()
    assert cb.state is CircuitState.OPEN
    time.sleep(0.08)
    assert cb.state is CircuitState.HALF_OPEN
    cb.guard()  # HALF_OPEN must allow a trial call through
    cb.record_success()
    assert cb.state is CircuitState.CLOSED


def test_half_open_failure_reopens_immediately():
    cb = CircuitBreaker(failure_threshold=1, reset_timeout_s=0.05)
    cb.record_failure()
    time.sleep(0.08)
    assert cb.state is CircuitState.HALF_OPEN
    cb.record_failure()
    assert cb.state is CircuitState.OPEN
