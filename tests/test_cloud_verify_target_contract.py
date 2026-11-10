"""Guard the read-only Genesis Cloud Run verification target and PAPER safety."""
from pathlib import Path
import unittest

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/cloud-verify.yml"


class CloudVerifyTargetContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_target_is_discovered_not_hardcoded(self):
        self.assertIn("name-discovery:", self.workflow)
        self.assertIn("needs: name-discovery", self.workflow)
        self.assertIn("python scripts/cloud_discover_readonly.py", self.workflow)
        self.assertIn("needs.name-discovery.outputs.project", self.workflow)
        self.assertIn("needs.name-discovery.outputs.service", self.workflow)
        self.assertIn('gcloud run services describe "$DISCOVERED_SERVICE"', self.workflow)
        self.assertNotIn("project_id: system3-openalgo-safe", self.workflow)
        self.assertNotIn("services describe genesis-system3-web --project", self.workflow)

    def test_read_only_wif_and_paper_safety_preserved(self):
        for marker in (
            "id-token: write",
            "vars.GCP_WIF_PROVIDER",
            "vars.GCP_WIF_SERVICE_ACCOUNT",
            "secrets.GCP_SERVICE_ACCOUNT_JSON",
            "needs.name-discovery.outputs.auth_mode",
            "PAPER_MODE: '1'",
            "LIVE_ORDER_AUTHORITY: '0'",
            "REAL_BROKER_ORDERS: '0'",
            "LIVE_TRADING_ENABLED: '0'",
            "ORDER_PLACEMENT_ALLOWED: 'false'",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.workflow)


if __name__ == "__main__":
    unittest.main()
