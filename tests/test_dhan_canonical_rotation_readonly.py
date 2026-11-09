"""Offline safety tests for the GitHub WIF Dhan metadata audit."""
import json
import unittest
from unittest.mock import patch

from scripts import dhan_canonical_rotation_readonly as probe


class DhanCanonicalReadOnlyContractTests(unittest.TestCase):
    def test_broker_response_never_exports_account_or_token(self):
        payload = {
            "connected": False,
            "error": "SENSITIVE_FREE_TEXT",
            "auth_classification": "TOKEN_EXPIRED_OR_INVALID",
            "source": "GCP_SECRET_MANAGER_DYNAMIC",
            "access_token": "HIGHLY_PRIVATE_TOKEN_STRING",
            "dhanClientId": "SENSITIVE_CLIENT_ID",
            "orders": [{"id": "SENSITIVE_ORDER_ID"}],
        }
        result = probe._broker_summary(payload)
        self.assertEqual(result["connected"], False)
        self.assertTrue(result["error_present"])
        self.assertEqual(result["auth_classification"], "TOKEN_EXPIRED_OR_INVALID")
        out = json.dumps(result)
        for forbidden in ("HIGHLY_PRIVATE", "CLIENT_ID", "ORDER_ID", "SENSITIVE_FREE_TEXT"):
            self.assertNotIn(forbidden, out)

    def test_runtime_config_discards_token_value(self):
        doc = {"spec": {"template": {"spec": {"containers": [{
            "env": [
                {"name": "DHAN_ACCESS_TOKEN", "value": "PRIVATE_TOKEN"},
                {"name": "DHAN_ACCESS_TOKEN_SECRET_ID", "value": "dhan-access-token"},
                {"name": "DHAN_TOKEN_SOURCE", "value": "gcp-secret-manager-dynamic"},
            ]}]}}}, "status": {"latestReadyRevisionName": "genesis-system3-web-00113-dip"}}
        result = probe._runtime_token_source(doc)
        self.assertEqual(result["canonical_secret_id"], "CANONICAL")
        self.assertTrue(result["static_token_value_configured"])
        self.assertEqual(result["token_provider_mode"], "SECRET_MANAGER")
        self.assertNotIn("PRIVATE_TOKEN", json.dumps(result))

    def test_rotator_config_sanitized_and_not_mutating(self):
        doc = {"spec": {"template": {"spec": {"template": {"spec": {"containers": [
            {"image": "registry.example/repo@sha256:" + "a" * 64,
             "command": ["python", "scripts/gcp_dhan_token_rotation_job.py"],
             "env": [
                 {"name": "DHAN_CLIENT_ID", "value": "PRIVATE_CLIENT_ID"},
                 {"name": "PAPER_MODE", "value": "1"}]}
        ]}}}}}}
        result = probe._executable_metadata(doc)
        self.assertTrue(result["single_container"])
        self.assertTrue(result["image_digest_pinned"])
        self.assertTrue(result["command_configured"])
        self.assertNotIn("PRIVATE_CLIENT_ID", json.dumps(result))

    def test_production_autoheal_blocks_even_a_get_probe(self):
        doc = {"spec": {"template": {"spec": {"containers": [{
            "env": [
                {"name": "DHAN_CANONICAL_ROTATION_SELF_HEAL", "value": "1"},
                {"name": "DHAN_STATUS_AUTO_REFRESH", "value": "0"},
            ]}]}}},
            "status": {"url": "https://valid-service.a.run.app"}}
        config = probe._runtime_token_source(doc)
        self.assertIs(config["broker_status_get_without_autoheal"], False)
        with patch.object(probe, "_production_broker_status") as get_status, \
             patch.object(probe, "_gcloud_json") as gcloud:
            gcloud.side_effect = [(doc, "PASS")] + [(None, "DENIED_OR_UNAVAILABLE")] * 4
            out = probe.audit()
            get_status.assert_not_called()
            self.assertEqual(out["production_broker"]["http_status"],
                             "NOT_PROBED_AUTOHEAL_MAY_ROTATE_TOKEN")

    def test_broker_probe_disabled_on_unknown_secret_backed_flag(self):
        doc = {"spec": {"template": {"spec": {"containers": [{
            "env": [{"name": "DHAN_CANONICAL_ROTATION_SELF_HEAL",
                     "valueFrom": {"secretKeyRef": {"name": "flag"}}}]
        }]}}}}
        self.assertFalse(
            probe._runtime_token_source(doc)["broker_status_get_without_autoheal"]
        )

    def test_unknown_auth_classification_fails_closed(self):
        result = probe._broker_summary({
            "connected": "yes",
            "auth_classification": "CUSTOM_PRIVATE_ERROR",
            "source": "PRIVATE_SOURCE_FIELD",
        })
        self.assertEqual(result["connected"], "UNREPORTED")
        self.assertEqual(result["auth_classification"], "UNREPORTED")
        self.assertEqual(result["source"], "UNREPORTED")
        self.assertEqual(probe._status_code(True), "UNREPORTED")

    @patch.object(probe, "_gcloud_json", return_value=(None, "DENIED_OR_UNAVAILABLE"))
    def test_missing_authority_returns_no_success_claim(self, fake):
        report = probe.audit()
        self.assertEqual(report["service_read"], "DENIED_OR_UNAVAILABLE")
        self.assertEqual(report["rotation_job_read"], "DENIED_OR_UNAVAILABLE")
        self.assertNotIn("production_broker", report)
        self.assertNotIn("canonical_secret_versions", report)
        self.assertEqual(report["scope"], "READ_ONLY_NO_TOKEN_PAYLOAD_NO_ORDERS")
        self.assertEqual(fake.call_count, 5)

    def test_only_validated_production_url_may_be_probed(self):
        with patch.object(probe, "_gcloud_json") as fake:
            result = probe._production_broker_status(
                {"status": {"url": "http://example.invalid/path"}}
            )
        self.assertEqual(result["http_status"], "URL_NOT_VERIFIED")
        fake.assert_not_called()


if __name__ == "__main__":
    unittest.main()
