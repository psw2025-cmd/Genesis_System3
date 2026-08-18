"""Eval: DH-906 must not multiply Dhan Profile GETs or authorize token recovery."""

from core.brokers.dhan.cloud_status_probe import _PROFILE_FALLBACK_ERRORS


def test_eval_906_is_not_a_profile_header_fallback():
    assert "DHAN_REQUEST_REJECTED_906" not in _PROFILE_FALLBACK_ERRORS
    assert "DHAN_RATE_LIMITED" not in _PROFILE_FALLBACK_ERRORS
    assert "TOKEN_EXPIRED_OR_INVALID" not in _PROFILE_FALLBACK_ERRORS
