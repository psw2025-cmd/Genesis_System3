"""Guard the read-only Genesis Cloud Run verification target and PAPER safety."""
from pathlib import Path
import unittest

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/cloud-verify.yml"


class CloudVerifyTargetContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_cloud_run_target_matches_production_identity(self):
        self.assertIn("project_id: system3-openalgo-safe", self.workflow)
        self.assertIn(
            "gcloud run services describe genesis-system3-web --project system3-openalgo-safe --region asia-south1",
            self.workflow,
        )
        self.assertNotIn("gcloud run services describe genesis --project genesis-system3", self.workflow)

    def test_read_only_wif_and_paper_safety_preserved(self):
        for marker in (
            "id-token: write",
            "vars.GCP_WIF_PROVIDER",
            "vars.GCP_WIF_SERVICE_ACCOUNT",
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
