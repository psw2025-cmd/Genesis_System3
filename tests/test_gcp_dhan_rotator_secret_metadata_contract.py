from pathlib import Path
import unittest


class DhanRotatorSecretMetadataContractTests(unittest.TestCase):
    def test_rotator_needs_secret_payload_access_but_not_version_metadata_get(self):
        text = Path("scripts/gcp_dhan_token_rotation_job.py").read_text(encoding="utf-8")
        self.assertIn("access_secret_version", text)
        self.assertIn("add_secret_version", text)
        self.assertNotIn("get_secret_version(", text)
        self.assertIn('"created_at": None', text)

    def test_bootstrap_keeps_rotator_secret_permissions_least_privilege(self):
        text = Path("deploy/gcp/bootstrap_github_wif.sh").read_text(encoding="utf-8")
        self.assertIn("roles/secretmanager.secretAccessor", text)
        self.assertIn("roles/secretmanager.secretVersionAdder", text)
        self.assertNotIn("roles/secretmanager.viewer", text)
        self.assertNotIn("roles/secretmanager.admin", text)


if __name__ == "__main__":
    unittest.main()
