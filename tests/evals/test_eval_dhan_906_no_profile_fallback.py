"""Eval: DH-906 permits one bounded read-only header reconciliation, never token recovery."""

from core.brokers.dhan.cloud_status_probe import _PROFILE_FALLBACK_ERRORS


def test_eval_906_allows_only_safe_profile_header_fallback():
    assert "DHAN_REQUEST_REJECTED_906" in _PROFILE_FALLBACK_ERRORS
    assert "DHAN_RATE_LIMITED" not in _PROFILE_FALLBACK_ERRORS
    assert "TOKEN_EXPIRED_OR_INVALID" not in _PROFILE_FALLBACK_ERRORS
