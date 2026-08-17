import base64
import json
import os
import types
import unittest
from unittest.mock import patch

from core.brokers.dhan import cloud_token_provider as provider
from core.brokers.dhan.cloud_runtime_patch import _auth_failed, _wrap_read
from core.brokers.dhan.cloud_status_probe import get_cloud_status
from core.brokers.dhan.first_rejection_trace import _reset_for_tests, snapshot


def _jwt(exp):
    payload = base64.urlsafe_b64encode(json.dumps({"exp": exp}).encode()).decode().rstrip("=")
    return f"x.{payload}.y"


class _Client:
    def __init__(self, versions):
        self.versions = list(versions)
        self.calls = 0

    def access_secret_version(self, request):
        version, token = self.versions[min(self.calls, len(self.versions) - 1)]
        self.calls += 1
        return types.SimpleNamespace(name=f"projects/p/secrets/s/versions/{version}", payload=types.SimpleNamespace(data=token.encode()))

    def get_secret_version(self, request):
        return types.SimpleNamespace(create_time=None)


def _status_module(token, rest):
    return types.SimpleNamespace(
        _STATUS_RESULT_CACHE=None,
        _STATUS_RESULT_CACHE_AT=0.0,
        _STATUS_RESULT_TTL_S=25.0,
        _DHAN_SDK_OK=True,
        _ENV_LOADED_VIA="test",
        _DHAN_PROFILE_URL="https://dhan.test/profile",
        get_dhan_credentials=lambda: {"client_id": "c", "access_token": token},
        _auth_failure_payload=lambda d: d.get("status") == "failure",
        _rest_get=rest,
    )


def _http_error(status_code, text):
    exc = RuntimeError(f"http {status_code}")
    exc.response = types.SimpleNamespace(status_code=status_code, text=text)
    return exc


class BR1DhanAuthReliabilityTests(unittest.TestCase):
    def setUp(self):
        _reset_for_tests()

    def tearDown(self):
        _reset_for_tests()
        provider._set_client_factory_for_tests(None)
        os.environ.pop("DHAN_TOKEN_SOURCE", None)
        os.environ.pop("DHAN_AUTH_RELOAD_BACKOFF_S", None)

    def test_clock_valid_dhan_rejection_preserves_legacy_error_and_adds_explicit_class(self):
        import time
        token = _jwt(time.time() + 3600)
        result = get_cloud_status(_status_module(token, lambda *a, **k: {"status": "failure"}))
        self.assertEqual(result["error"], "TOKEN_EXPIRED_OR_INVALID")
        self.assertEqual(result["auth_classification"], "DHAN_TOKEN_REJECTED")

    def test_clock_expired_token_is_distinguished(self):
        import time
        token = _jwt(time.time() - 60)
        result = get_cloud_status(_status_module(token, lambda *a, **k: {"status": "failure"}))
        self.assertEqual(result["auth_classification"], "TOKEN_CLOCK_EXPIRED")

    def test_http_401_code_808_clock_valid_is_dhan_rejected(self):
        import time
        token = _jwt(time.time() + 3600)

        def rest(*args, **kwargs):
            raise _http_error(401, '{"code":808,"message":"Invalid Access Token"}')

        result = get_cloud_status(_status_module(token, rest))
        self.assertEqual(result["error"], "TOKEN_EXPIRED_OR_INVALID")
        self.assertEqual(result["auth_classification"], "DHAN_TOKEN_REJECTED")
        self.assertIsNone(result["upstream_classification"])
        trace = snapshot()
        self.assertEqual(trace["rejection_count"], 1)
        self.assertEqual(trace["upstream_code"], 808)

    def test_http_400_dh906_is_non_auth_even_if_text_says_invalid_token(self):
        import time
        token = _jwt(time.time() + 3600)

        def rest(*args, **kwargs):
            raise _http_error(400, "DH-906 invalid token")

        result = get_cloud_status(_status_module(token, rest))
        self.assertEqual(result["error"], "DHAN_REQUEST_REJECTED_906")
        self.assertIsNone(result["auth_classification"])
        self.assertEqual(result["upstream_classification"], "DHAN_REQUEST_REJECTED_906")
        self.assertEqual(snapshot()["rejection_count"], 0)

    def test_non_auth_http_400_is_not_falsely_labeled_token_rejected(self):
        import time
        token = _jwt(time.time() + 3600)

        def rest(*args, **kwargs):
            raise _http_error(400, "Malformed request: unsupported profile field")

        result = get_cloud_status(_status_module(token, rest))
        self.assertEqual(result["error"], "HTTP_400")
        self.assertIsNone(result["auth_classification"])
        self.assertIsNone(result["upstream_classification"])
        self.assertEqual(snapshot()["rejection_count"], 0)

    def test_http_429_is_not_auth_failure(self):
        import time
        token = _jwt(time.time() + 3600)

        def rest(*args, **kwargs):
            raise _http_error(429, "Too Many Requests")

        result = get_cloud_status(_status_module(token, rest))
        self.assertEqual(result["error"], "HTTP_429")
        self.assertIsNone(result["auth_classification"])
        self.assertEqual(result["upstream_classification"], "DHAN_RATE_LIMITED")
        self.assertEqual(snapshot()["rejection_count"], 0)

    def test_runtime_recovery_classifier_rejects_906_and_805_even_with_auth_text(self):
        self.assertFalse(_auth_failed({
            "error": "DHAN_REQUEST_REJECTED_906",
            "upstream_classification": "DHAN_REQUEST_REJECTED_906",
            "message": "DH-906 invalid token",
        }))
        self.assertFalse(_auth_failed({
            "error": "HTTP_429",
            "upstream_classification": "DHAN_RATE_LIMITED",
            "message": "code 805 invalid token",
        }))
        self.assertTrue(_auth_failed({"error": "TOKEN_EXPIRED_OR_INVALID", "auth_classification": "DHAN_TOKEN_REJECTED"}))
        self.assertTrue(_auth_failed({"error": "HTTP_401", "message": "unauthorized"}))

    def test_runtime_wrapper_does_not_reload_or_rotate_for_dh906(self):
        module = types.SimpleNamespace(_STATUS_RESULT_CACHE=None, _STATUS_RESULT_CACHE_AT=0.0)
        original = lambda: {
            "connected": False,
            "error": "DHAN_REQUEST_REJECTED_906",
            "auth_classification": None,
            "upstream_classification": "DHAN_REQUEST_REJECTED_906",
            "message": "DH-906 invalid token",
        }
        wrapped = _wrap_read(module, "get_profile", original)
        with patch("core.brokers.dhan.cloud_runtime_patch.get_access_token") as get_token, \
             patch("core.brokers.dhan.cloud_runtime_patch.force_reload") as reload_token, \
             patch("core.brokers.dhan.cloud_runtime_patch._invoke_canonical_rotation") as rotate:
            result = wrapped()
        get_token.assert_called_once()
        reload_token.assert_not_called()
        rotate.assert_not_called()
        self.assertFalse(result["token_reload"]["attempted"])
        self.assertFalse(result["canonical_rotation"]["attempted"])

    def test_same_rejected_secret_version_force_reload_is_suppressed(self):
        client = _Client([("258", "token-a"), ("258", "token-a"), ("258", "token-a")])
        provider._set_client_factory_for_tests(lambda: client)
        os.environ["DHAN_TOKEN_SOURCE"] = "gcp"
        os.environ["DHAN_AUTH_RELOAD_BACKOFF_S"] = "60"
        provider.get_access_token(force_refresh=True, reason="startup")
        self.assertFalse(provider.force_reload("get_status_auth_failure"))
        calls_after_first = client.calls
        self.assertFalse(provider.force_reload("get_status_auth_failure"))
        self.assertEqual(client.calls, calls_after_first)
        meta = provider.token_metadata()
        self.assertEqual(meta["rejected_secret_version"], "258")
        self.assertEqual(meta["auth_reload_suppressed_count"], 1)
        self.assertFalse(meta["token_value_exposed"])

    def test_normal_ttl_refresh_can_discover_new_version_during_auth_backoff(self):
        client = _Client([("258", "token-a"), ("258", "token-a"), ("259", "token-b")])
        provider._set_client_factory_for_tests(lambda: client)
        os.environ["DHAN_TOKEN_SOURCE"] = "gcp"
        os.environ["DHAN_AUTH_RELOAD_BACKOFF_S"] = "60"
        provider.get_access_token(force_refresh=True, reason="startup")
        self.assertFalse(provider.force_reload("get_status_auth_failure"))
        with patch.object(provider, "_ttl_seconds", return_value=0.0):
            self.assertEqual(provider.get_access_token(reason="normal_ttl_refresh"), "token-b")
        self.assertEqual(provider.token_metadata()["secret_version"], "259")
        self.assertIsNone(provider.token_metadata()["rejected_secret_version"])


if __name__ == "__main__":
    unittest.main()
