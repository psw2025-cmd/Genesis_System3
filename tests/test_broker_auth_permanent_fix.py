from __future__ import annotations

import types
import unittest
from pathlib import Path
from unittest.mock import patch

from core.brokers.dhan.cloud_runtime_patch import _auth_failed, _strict_cloud_status


class PermanentBrokerAuthFixTests(unittest.TestCase):
    def test_normalized_dh906_invalid_token_is_auth_failure(self):
        self.assertTrue(
            _auth_failed(
                {
                    "error": "TOKEN_EXPIRED_OR_INVALID",
                    "auth_classification": "DHAN_TOKEN_REJECTED",
                    "upstream_code": 906,
                    "message": "DH-906 Invalid Token",
                }
            )
        )

    def test_bare_dh906_request_rejection_does_not_trigger_token_churn(self):
        self.assertFalse(
            _auth_failed(
                {
                    "error": "DHAN_REQUEST_REJECTED_906",
                    "upstream_classification": "DHAN_REQUEST_REJECTED_906",
                    "message": "DH-906 request rejected",
                }
            )
        )

    def test_strict_status_requires_profile_funds_holdings_and_positions(self):
        urls = {
            "funds": "https://dhan.test/funds",
            "holdings": "https://dhan.test/holdings",
            "positions": "https://dhan.test/positions",
        }

        def rest_get(url, token, client_id, **kwargs):
            self.assertEqual(token, "token")
            self.assertEqual(client_id, "client")
            if url == urls["funds"]:
                return {"availableBalance": 100.0}
            if url == urls["holdings"]:
                return []
            if url == urls["positions"]:
                return []
            raise AssertionError(url)

        module = types.SimpleNamespace(
            get_dhan_credentials=lambda: {"client_id": "client", "access_token": "token"},
            _rest_get=rest_get,
            _payload_error=lambda data: None,
            _exception_error=lambda exc: f"ERR:{type(exc).__name__}",
            _DHAN_FUNDS_URL=urls["funds"],
            _DHAN_HOLDINGS_URL=urls["holdings"],
            _DHAN_POSITIONS_URL=urls["positions"],
            _STATUS_RESULT_CACHE=None,
            _STATUS_RESULT_CACHE_AT=0.0,
        )
        base = {
            "broker": "dhan",
            "connected": True,
            "error": None,
            "auth_classification": "AUTH_OK",
        }
        with patch("core.brokers.dhan.cloud_runtime_patch.get_cloud_status", return_value=base):
            result = _strict_cloud_status(module)

        self.assertTrue(result["connected"])
        self.assertTrue(result["broker_truth_complete"])
        self.assertEqual(result["broker_truth_contract"], "profile+funds+holdings+positions")
        for name in ("profile", "funds", "holdings", "positions"):
            self.assertTrue(result["account_read_proof"][name]["ok"])
        self.assertFalse(result["raw_account_payload_exposed"])

    def test_strict_status_fails_closed_when_funds_rejects_token(self):
        def rest_get(url, token, client_id, **kwargs):
            if url.endswith("funds"):
                return {"status": "failure", "errorCode": "DH-906", "errorMessage": "Invalid Token"}
            return []

        def payload_error(data):
            if isinstance(data, dict) and data.get("errorCode") == "DH-906":
                return "TOKEN_EXPIRED_OR_INVALID"
            return None

        module = types.SimpleNamespace(
            get_dhan_credentials=lambda: {"client_id": "client", "access_token": "token"},
            _rest_get=rest_get,
            _payload_error=payload_error,
            _exception_error=lambda exc: f"ERR:{type(exc).__name__}",
            _DHAN_FUNDS_URL="https://dhan.test/funds",
            _DHAN_HOLDINGS_URL="https://dhan.test/holdings",
            _DHAN_POSITIONS_URL="https://dhan.test/positions",
            _STATUS_RESULT_CACHE=None,
            _STATUS_RESULT_CACHE_AT=0.0,
        )
        with patch(
            "core.brokers.dhan.cloud_runtime_patch.get_cloud_status",
            return_value={"broker": "dhan", "connected": True, "error": None, "auth_classification": "AUTH_OK"},
        ):
            result = _strict_cloud_status(module)

        self.assertFalse(result["connected"])
        self.assertEqual(result["error"], "TOKEN_EXPIRED_OR_INVALID")
        self.assertEqual(result["auth_classification"], "DHAN_TOKEN_REJECTED")
        self.assertFalse(result["broker_truth_complete"])

    def test_rotator_invalid_cooldown_is_nonzero_and_validation_precedes_persistence(self):
        text = Path("scripts/gcp_dhan_token_rotation_job.py").read_text(encoding="utf-8")
        self.assertIn('if state == PROFILE_AUTH_INVALID:', text)
        self.assertIn('return "BLOCKED_AUTH_INVALID_REMINT_COOLDOWN", 2', text)
        self.assertIn('"BLOCKED_AUTH_INVALID_REMINT_COOLDOWN"', text)
        validate_at = text.index('generated_check = _profile_probe(client_id, new_token)')
        candidate_at = text.index('candidate_version = _persist_candidate_token(new_token)')
        canonical_at = text.index('new_version = _persist_authoritative_token(new_token)')
        self.assertLess(validate_at, candidate_at)
        self.assertLess(candidate_at, canonical_at)
        self.assertIn('"candidate_persisted_before_validation": False', text)


if __name__ == "__main__":
    unittest.main()
