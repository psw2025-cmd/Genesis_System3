import base64
import json
import time
import types
import unittest

from core.brokers.dhan.cloud_status_probe import get_cloud_status
from core.brokers.dhan.first_rejection_trace import _reset_for_tests, snapshot


def _jwt(exp):
    payload = base64.urlsafe_b64encode(json.dumps({"exp": exp}).encode()).decode().rstrip("=")
    return f"x.{payload}.y"


def _http_error(status_code, text):
    exc = RuntimeError(f"http {status_code}")
    exc.response = types.SimpleNamespace(status_code=status_code, text=text)
    return exc


def _module(handler):
    token = _jwt(time.time() + 3600)
    module = types.SimpleNamespace(
        _STATUS_RESULT_CACHE=None,
        _STATUS_RESULT_CACHE_AT=0.0,
        _STATUS_RESULT_TTL_S=25.0,
        _PROFILE_HEADER_CONTRACT_CACHE="",
        _DHAN_SDK_OK=True,
        _ENV_LOADED_VIA="test",
        _DHAN_PROFILE_URL="https://dhan.test/profile",
        get_dhan_credentials=lambda: {"client_id": "CLIENT_SECRET_VALUE", "access_token": token},
        _profile_probe_request=handler,
    )
    return module, token


class DhanProfileHeaderReconcileTests(unittest.TestCase):
    def setUp(self):
        _reset_for_tests()

    def tearDown(self):
        _reset_for_tests()

    def test_docs_contract_success_uses_one_request(self):
        calls = []

        def handler(access_token, client_id, *, timeout_s, contract):
            calls.append(contract)
            return {"dhanClientId": "safe", "status": "success"}

        module, _ = _module(handler)
        result = get_cloud_status(module)

        self.assertTrue(result["connected"])
        self.assertEqual(calls, ["docs-access-token-only"])
        self.assertEqual(result["probe_header_contract"], "access-token-only")
        self.assertEqual(result["probe_header_variant"], "docs-access-token-only")
        self.assertEqual(len(result["probe_header_attempts"]), 1)
        self.assertEqual(snapshot()["rejection_count"], 0)

    def test_docs_906_reconciles_once_to_official_sdk_contract_without_auth_latch(self):
        calls = []

        def handler(access_token, client_id, *, timeout_s, contract):
            calls.append(contract)
            if contract == "docs-access-token-only":
                raise _http_error(400, "DH-906 incorrect request")
            return {"dhanClientId": "safe", "status": "success"}

        module, _ = _module(handler)
        result = get_cloud_status(module)

        self.assertTrue(result["connected"])
        self.assertIsNone(result["error"])
        self.assertEqual(calls, ["docs-access-token-only", "sdk-dhanClientId"])
        self.assertEqual(result["probe_header_contract"], "access-token-plus-dhanClientId")
        self.assertEqual(result["probe_header_variant"], "sdk-dhanClientId")
        self.assertEqual(len(result["probe_header_attempts"]), 2)
        self.assertEqual(snapshot()["rejection_count"], 0)
        self.assertTrue(all(item["credential_value_exposed"] is False for item in result["probe_header_attempts"]))

    def test_two_906_contract_failures_remain_non_auth_and_are_ttl_cached(self):
        calls = []

        def handler(access_token, client_id, *, timeout_s, contract):
            calls.append(contract)
            raise _http_error(400, "DH-906 incorrect request")

        module, _ = _module(handler)
        first = get_cloud_status(module)

        self.assertFalse(first["connected"])
        self.assertEqual(first["error"], "DHAN_REQUEST_REJECTED_906")
        self.assertEqual(first["upstream_classification"], "DHAN_REQUEST_REJECTED_906")
        self.assertEqual(first["upstream_code"], 906)
        self.assertEqual(calls, ["docs-access-token-only", "sdk-dhanClientId"])
        self.assertEqual(first["probe_header_variant"], "docs-access-token-only")
        self.assertEqual(snapshot()["rejection_count"], 0)

        calls.clear()
        second = get_cloud_status(module)
        self.assertFalse(second["connected"])
        self.assertTrue(second["cache_hit"])
        self.assertEqual(second["error"], "DHAN_REQUEST_REJECTED_906")
        self.assertEqual(calls, [])
        self.assertEqual(len(second["probe_header_attempts"]), 2)

    def test_rate_limit_never_multiplies_requests_and_is_ttl_cached(self):
        calls = []

        def handler(access_token, client_id, *, timeout_s, contract):
            calls.append(contract)
            raise _http_error(429, '{"code":805,"message":"Too many requests"}')

        module, _ = _module(handler)
        first = get_cloud_status(module)

        self.assertFalse(first["connected"])
        self.assertEqual(first["error"], "DHAN_RATE_LIMITED")
        self.assertEqual(calls, ["docs-access-token-only"])
        self.assertEqual(snapshot()["rejection_count"], 0)

        calls.clear()
        second = get_cloud_status(module)
        self.assertTrue(second["cache_hit"])
        self.assertEqual(second["error"], "DHAN_RATE_LIMITED")
        self.assertEqual(calls, [])

    def test_auth_failure_never_retries_header_variant_and_latches_once(self):
        calls = []

        def handler(access_token, client_id, *, timeout_s, contract):
            calls.append(contract)
            raise _http_error(401, '{"code":808,"message":"Invalid Access Token"}')

        module, _ = _module(handler)
        result = get_cloud_status(module)

        self.assertFalse(result["connected"])
        self.assertEqual(result["error"], "TOKEN_EXPIRED_OR_INVALID")
        self.assertEqual(calls, ["docs-access-token-only"])
        self.assertEqual(snapshot()["rejection_count"], 1)
        self.assertEqual(snapshot()["upstream_code"], 808)

    def test_client_id_810_can_reconcile_to_sdk_contract_without_token_recovery(self):
        calls = []

        def handler(access_token, client_id, *, timeout_s, contract):
            calls.append(contract)
            if contract == "docs-access-token-only":
                raise _http_error(400, '{"code":810,"message":"Client ID is invalid"}')
            return {"dhanClientId": "safe", "status": "success"}

        module, _ = _module(handler)
        result = get_cloud_status(module)

        self.assertTrue(result["connected"])
        self.assertEqual(calls, ["docs-access-token-only", "sdk-dhanClientId"])
        self.assertEqual(result["probe_header_contract"], "access-token-plus-dhanClientId")
        self.assertEqual(result["probe_header_variant"], "sdk-dhanClientId")
        self.assertEqual(snapshot()["rejection_count"], 0)

    def test_two_810_failures_report_configuration_not_token_failure(self):
        calls = []

        def handler(access_token, client_id, *, timeout_s, contract):
            calls.append(contract)
            raise _http_error(400, '{"code":810,"message":"Client ID is invalid"}')

        module, _ = _module(handler)
        result = get_cloud_status(module)

        self.assertFalse(result["connected"])
        self.assertEqual(result["error"], "CLIENT_ID_INVALID")
        self.assertEqual(result["upstream_classification"], "DHAN_CLIENT_ID_INVALID")
        self.assertEqual(calls, ["docs-access-token-only", "sdk-dhanClientId"])
        self.assertEqual(snapshot()["rejection_count"], 0)

    def test_proven_sdk_contract_is_cached_for_next_probe(self):
        calls = []

        def handler(access_token, client_id, *, timeout_s, contract):
            calls.append(contract)
            if contract == "docs-access-token-only":
                raise _http_error(400, '{"code":810,"message":"Client ID is invalid"}')
            return {"dhanClientId": "safe", "status": "success"}

        module, _ = _module(handler)
        first = get_cloud_status(module)
        self.assertTrue(first["connected"])
        self.assertEqual(module._PROFILE_HEADER_CONTRACT_CACHE, "sdk-dhanClientId")

        module._STATUS_RESULT_CACHE = None
        module._STATUS_RESULT_CACHE_AT = 0.0
        calls.clear()
        second = get_cloud_status(module)

        self.assertTrue(second["connected"])
        self.assertEqual(calls, ["sdk-dhanClientId"])
        self.assertEqual(second["probe_header_contract"], "access-token-plus-dhanClientId")
        self.assertEqual(second["probe_header_variant"], "sdk-dhanClientId")
        self.assertTrue(second["probe_contract_cached"])

    def test_safe_attempt_metadata_never_contains_credentials(self):
        token_marker = "TOKEN_DO_NOT_EXPOSE"
        client_marker = "CLIENT_DO_NOT_EXPOSE"
        calls = []

        def handler(access_token, client_id, *, timeout_s, contract):
            calls.append(contract)
            self.assertEqual(access_token, token_marker)
            self.assertEqual(client_id, client_marker)
            raise _http_error(400, "DH-906 incorrect request")

        module = types.SimpleNamespace(
            _STATUS_RESULT_CACHE=None,
            _STATUS_RESULT_CACHE_AT=0.0,
            _STATUS_RESULT_TTL_S=25.0,
            _PROFILE_HEADER_CONTRACT_CACHE="",
            _DHAN_SDK_OK=True,
            _ENV_LOADED_VIA="test",
            _DHAN_PROFILE_URL="https://dhan.test/profile",
            get_dhan_credentials=lambda: {"client_id": client_marker, "access_token": token_marker},
            _profile_probe_request=handler,
        )
        result = get_cloud_status(module)
        serialized = json.dumps(result, sort_keys=True)

        self.assertNotIn(token_marker, serialized)
        self.assertNotIn(client_marker, serialized)
        self.assertEqual(calls, ["docs-access-token-only", "sdk-dhanClientId"])
        self.assertTrue(all(item["credential_value_exposed"] is False for item in result["probe_header_attempts"]))


if __name__ == "__main__":
    unittest.main()
