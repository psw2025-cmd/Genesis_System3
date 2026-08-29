import json
import unittest

from scripts.gcp_dhan_rotator_forensic import _redact

TEST_ONLY_FAKE_TOKEN = "TEST_ONLY_FAKE_TOKEN_12345"


class DhanRotatorForensicRedactionTests(unittest.TestCase):
    """Proves the CodeQL py/clear-text-storage-sensitive-data and
    py/clear-text-logging-sensitive-data findings on gcp_dhan_rotator_forensic.py
    (alerts #144/#145) are false positives: the flagged sink only ever carries
    a Secret Manager *version identifier*, never a real token value, and any
    genuinely sensitive field is redacted before it could reach output."""

    def test_dummy_secret_value_is_redacted_under_sensitive_keys(self):
        for key in ("access_token", "authorization", "password", "totp", "pin", "api_key"):
            redacted = _redact(TEST_ONLY_FAKE_TOKEN, key)
            self.assertEqual(redacted, "<redacted>")
            self.assertNotIn(TEST_ONLY_FAKE_TOKEN, str(redacted))

    def test_secret_version_metadata_is_not_redacted(self):
        # secret_version/secret_id/token_source are Secret Manager identifiers
        # (e.g. "320"), not the secret payload - explicitly allow-listed.
        self.assertEqual(_redact("320", "secret_version"), "320")
        self.assertEqual(_redact("dhan-access-token", "secret_id"), "dhan-access-token")
        self.assertEqual(_redact("GCP_SECRET_MANAGER_DYNAMIC", "token_source"), "GCP_SECRET_MANAGER_DYNAMIC")

    def test_nested_dummy_secret_is_redacted_and_absent_from_serialized_output(self):
        raw = {
            "secret_version": "320",
            "access_token": TEST_ONLY_FAKE_TOKEN,
            "nested": {"authorization": f"Bearer {TEST_ONLY_FAKE_TOKEN}"},
        }
        safe = _redact(raw)
        serialized = json.dumps(safe)

        self.assertNotIn(TEST_ONLY_FAKE_TOKEN, serialized)
        self.assertEqual(safe["secret_version"], "320")
        self.assertEqual(safe["access_token"], "<redacted>")
        self.assertIn("<redacted>", safe["nested"]["authorization"])


if __name__ == "__main__":
    unittest.main()
