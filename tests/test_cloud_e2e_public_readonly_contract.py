from pathlib import Path
import unittest


SCRIPT = Path("scripts/cloud_e2e_proof.py")


class CloudE2EPublicReadonlyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SCRIPT.read_text(encoding="utf-8")

    def test_retired_dashboard_credentials_are_not_loaded_or_sent(self):
        retired_env = "DASHBOARD_" + "API_KEY"
        retired_header = "X-" + "API-Key"
        retired_file = "dashboard_" + "api_key.env"
        self.assertNotIn(retired_env, self.text)
        self.assertNotIn(retired_header, self.text)
        self.assertNotIn(retired_file, self.text)
        self.assertNotIn("_load_" + "api_key", self.text)

    def test_public_readonly_auth_contract_is_explicit(self):
        self.assertIn('auth_data.get("required") is False', self.text)
        self.assertIn('auth_data.get("configured") is False', self.text)
        self.assertIn('auth_data.get("authenticated") is False', self.text)
        self.assertIn('auth_data.get("mode") == "public_readonly"', self.text)

    def test_proof_records_no_dashboard_credential_authority(self):
        self.assertIn('"dashboard_access": "public_readonly_anonymous"', self.text)
        self.assertIn('"dashboard_credentials_loaded": False', self.text)
        self.assertIn('"dashboard_credentials_sent": False', self.text)

    def test_live_trading_remains_off(self):
        self.assertIn('"live_trading_enabled": False', self.text)
        self.assertNotIn("order_placement_allowed = True", self.text)


if __name__ == "__main__":
    unittest.main()
