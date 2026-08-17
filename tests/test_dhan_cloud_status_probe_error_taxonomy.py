import unittest

from core.brokers.dhan.cloud_status_probe import (
    _http_auth_failure,
    _non_auth_upstream_classification,
    get_cloud_status,
)
from core.brokers.dhan.first_rejection_trace import _reset_for_tests, snapshot


class _Response:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


class _ProbeError(RuntimeError):
    def __init__(self, status_code, text):
        super().__init__(f"upstream HTTP {status_code}")
        self.response = _Response(status_code, text)


class _Module:
    _STATUS_RESULT_CACHE = None
    _STATUS_RESULT_CACHE_AT = 0.0
    _STATUS_RESULT_TTL_S = 25.0
    _DHAN_SDK_OK = False
    _ENV_LOADED_VIA = "test"
    _DHAN_PROFILE_URL = "https://api.dhan.co/v2/profile"

    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

    def get_dhan_credentials(self):
        return {"client_id": "present", "access_token": "opaque-test-token"}

    def _rest_get(self, *_args, **_kwargs):
        raise _ProbeError(self.status_code, self.text)

    def _auth_failure_payload(self, _data):
        return False


class DhanCloudStatusProbeErrorTaxonomyTests(unittest.TestCase):
    def setUp(self):
        _reset_for_tests()

    def tearDown(self):
        _reset_for_tests()

    def test_http_401_is_affirmative_auth_failure(self):
        self.assertTrue(_http_auth_failure(401, "unauthorized"))

    def test_dhan_808_is_affirmative_auth_failure(self):
        self.assertTrue(_http_auth_failure(400, '{"code":808,"message":"authentication failed"}'))

    def test_dhan_805_and_906_override_ambiguous_auth_text_as_non_auth(self):
        self.assertFalse(_http_auth_failure(429, '{"code":805,"message":"too many requests"}'))
        self.assertFalse(_http_auth_failure(400, '{"errorCode":"DH-906","message":"order error"}'))
        self.assertFalse(_http_auth_failure(400, 'DH-906 invalid token'))

    def test_known_non_auth_codes_get_explicit_upstream_classification(self):
        self.assertEqual(_non_auth_upstream_classification(429, '{"code":805}'), "DHAN_RATE_LIMITED")
        self.assertEqual(
            _non_auth_upstream_classification(400, 'DH-906 incorrect order request'),
            "DHAN_REQUEST_REJECTED_906",
        )

    def test_dh906_does_not_become_token_invalid_or_increment_auth_latch(self):
        before = snapshot()["rejection_count"]
        result = get_cloud_status(_Module(400, 'DH-906 invalid token'))
        after = snapshot()["rejection_count"]

        self.assertFalse(result["connected"])
        self.assertEqual(result["error"], "DHAN_REQUEST_REJECTED_906")
        self.assertIsNone(result["auth_classification"])
        self.assertEqual(result["upstream_classification"], "DHAN_REQUEST_REJECTED_906")
        self.assertNotEqual(result["error"], "TOKEN_EXPIRED_OR_INVALID")
        self.assertEqual(before, 0)
        self.assertEqual(after, 0)
        self.assertEqual(result["auth_rejection_trace"]["rejection_count"], 0)

    def test_805_rate_limit_preserves_legacy_http_error_and_does_not_increment_auth_latch(self):
        result = get_cloud_status(_Module(429, '{"code":805,"message":"too many requests"}'))
        self.assertEqual(result["error"], "HTTP_429")
        self.assertIsNone(result["auth_classification"])
        self.assertEqual(result["upstream_classification"], "DHAN_RATE_LIMITED")
        self.assertEqual(snapshot()["rejection_count"], 0)

    def test_808_still_becomes_token_invalid_and_latches_once(self):
        result = get_cloud_status(_Module(400, '{"code":808,"message":"authentication failed"}'))
        self.assertEqual(result["error"], "TOKEN_EXPIRED_OR_INVALID")
        self.assertIn(
            result["auth_classification"],
            {"DHAN_TOKEN_REJECTED", "DHAN_TOKEN_REJECTED_CLOCK_UNKNOWN", "TOKEN_CLOCK_EXPIRED"},
        )
        self.assertIsNone(result["upstream_classification"])
        trace = snapshot()
        self.assertEqual(trace["rejection_count"], 1)
        self.assertEqual(trace["upstream_code"], 808)


if __name__ == "__main__":
    unittest.main()
