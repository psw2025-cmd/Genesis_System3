import types
import unittest

from core.brokers.dhan.cloud_status_probe import get_cloud_status


class _HTTPError(RuntimeError):
    def __init__(self, status_code, text):
        super().__init__(f"HTTP {status_code}")
        self.response = types.SimpleNamespace(status_code=status_code, text=text)


def _module(rest_impl):
    return types.SimpleNamespace(
        _STATUS_RESULT_CACHE=None,
        _STATUS_RESULT_CACHE_AT=0.0,
        _STATUS_RESULT_TTL_S=25.0,
        _DHAN_SDK_OK=True,
        _ENV_LOADED_VIA="test",
        _DHAN_PROFILE_URL="https://api.dhan.test/v2/profile",
        get_dhan_credentials=lambda: {"client_id": "client", "access_token": "token-value"},
        _auth_failure_payload=lambda data: data.get("status") == "failure",
        _rest_get=rest_impl,
    )


class CloudDhanStatusProbeTests(unittest.TestCase):
    def test_connected_status_uses_single_bounded_rest_probe_and_caches_truth(self):
        calls = []
        def rest(url, token, client_id, timeout):
            calls.append((url, token, client_id, timeout))
            return {"status": "success"}

        module = _module(rest)
        result = get_cloud_status(module, timeout_s=5)
        self.assertTrue(result["connected"])
        self.assertIsNone(result["error"])
        self.assertEqual(result["probe_strategy"], "cloud_rest_profile_bounded")
        self.assertEqual(len(calls), 1)
        self.assertLessEqual(calls[0][3], 5)

        cached = get_cloud_status(module, timeout_s=5)
        self.assertTrue(cached["connected"])
        self.assertTrue(cached["cache_hit"])
        self.assertEqual(len(calls), 1)

    def test_invalid_token_is_classified_for_existing_canonical_heal_wrapper(self):
        module = _module(lambda *args, **kwargs: {"status": "failure"})
        result = get_cloud_status(module, timeout_s=5)
        self.assertFalse(result["connected"])
        self.assertEqual(result["error"], "TOKEN_EXPIRED_OR_INVALID")
        self.assertFalse(result["live_trading_enabled"])
        self.assertFalse(result["order_placement_allowed"])

    def test_network_timeout_is_bounded_and_not_misclassified_as_auth_failure(self):
        def rest(*args, **kwargs):
            raise TimeoutError("network slow")
        module = _module(rest)
        result = get_cloud_status(module, timeout_s=5)
        self.assertFalse(result["connected"])
        self.assertEqual(result["error"], "NETWORK_ERROR:TimeoutError")

    def test_401_is_auth_failure(self):
        def rest(*args, **kwargs):
            raise _HTTPError(401, "Invalid Token")
        module = _module(rest)
        result = get_cloud_status(module, timeout_s=5)
        self.assertEqual(result["error"], "TOKEN_EXPIRED_OR_INVALID")


if __name__ == "__main__":
    unittest.main()
