import unittest

from scripts.gcp_dhan_rotator_forensic import (
    _runtime_trace_classification,
    _safe_auth_rejection_trace,
)


class DhanRotatorForensicTraceTests(unittest.TestCase):
    def test_allowlist_keeps_safe_first_rejection_fields_only(self):
        raw = {
            "first_rejected_at_utc": "2026-08-17T02:31:00+00:00",
            "last_rejected_at_utc": "2026-08-17T02:32:00+00:00",
            "rejection_count": 3,
            "secret_version": "260",
            "auth_classification": "DHAN_TOKEN_REJECTED",
            "http_status": 401,
            "upstream_code": 808,
            "runtime_instance": "genesis-system3-web-00422-yec",
            "raw_token_exposed": False,
            "client_id_exposed": False,
            "access_token": "must-never-project",
            "authorization": "must-never-project",
            "request_body": {"secret": "must-never-project"},
        }
        safe = _safe_auth_rejection_trace(raw)
        self.assertEqual(safe["secret_version"], "260")
        self.assertEqual(safe["http_status"], 401)
        self.assertEqual(safe["upstream_code"], 808)
        self.assertEqual(safe["rejection_count"], 3)
        self.assertNotIn("access_token", safe)
        self.assertNotIn("authorization", safe)
        self.assertNotIn("request_body", safe)

    def test_affirmative_401_808_runtime_trace_classifies_when_marker_missing(self):
        trace = {
            "rejection_count": 1,
            "auth_classification": "DHAN_TOKEN_REJECTED",
            "http_status": 401,
            "upstream_code": 808,
            "raw_token_exposed": False,
            "client_id_exposed": False,
        }
        self.assertEqual(
            _runtime_trace_classification(trace),
            "RUNTIME_FIRST_AUTH_REJECTION:DHAN_TOKEN_REJECTED",
        )

    def test_empty_or_nonaffirmative_trace_stays_unclassified(self):
        self.assertIsNone(_runtime_trace_classification({"rejection_count": 0}))
        self.assertIsNone(
            _runtime_trace_classification(
                {
                    "rejection_count": 1,
                    "auth_classification": "",
                    "http_status": 429,
                    "upstream_code": 805,
                    "raw_token_exposed": False,
                    "client_id_exposed": False,
                }
            )
        )

    def test_trace_marked_as_exposing_sensitive_identity_is_rejected(self):
        self.assertIsNone(
            _runtime_trace_classification(
                {
                    "rejection_count": 1,
                    "auth_classification": "DHAN_TOKEN_REJECTED",
                    "http_status": 401,
                    "upstream_code": 808,
                    "raw_token_exposed": True,
                    "client_id_exposed": False,
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
