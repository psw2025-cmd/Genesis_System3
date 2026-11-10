from core.data.lake.backoff import BackoffPolicy


def test_delay_never_exceeds_cap():
    policy = BackoffPolicy(base_seconds=1.0, cap_seconds=5.0, max_attempts=20)
    for attempt in range(20):
        for _ in range(50):
            assert 0 <= policy.delay_seconds(attempt) <= 5.0


def test_delay_grows_with_attempt_on_average():
    policy = BackoffPolicy(base_seconds=0.1, cap_seconds=100.0, max_attempts=None)
    samples_low = [policy.delay_seconds(0) for _ in range(200)]
    samples_high = [policy.delay_seconds(5) for _ in range(200)]
    assert sum(samples_high) / len(samples_high) > sum(samples_low) / len(samples_low)


def test_retry_after_hint_is_a_floor_not_a_ceiling():
    policy = BackoffPolicy(base_seconds=0.01, cap_seconds=0.01, max_attempts=None)
    for _ in range(20):
        assert policy.delay_seconds(0, retry_after=10.0) >= 10.0


def test_negative_attempt_rejected():
    policy = BackoffPolicy()
    try:
        policy.delay_seconds(-1)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_exhausted_respects_max_attempts():
    policy = BackoffPolicy(max_attempts=3)
    assert not policy.exhausted(0)
    assert not policy.exhausted(2)
    assert policy.exhausted(3)
    assert BackoffPolicy(max_attempts=None).exhausted(10_000) is False
