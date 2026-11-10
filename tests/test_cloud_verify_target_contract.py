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

    def test_cloud_verify_artifact_path_is_multiline_yaml_not_literal_escape(self):
        # A literal backslash-n under path: makes GitHub reject the workflow.
        expected = "          path: |" + chr(10) + (
            "            cloud-verify-evidence.jsonl" + chr(10) +
            "            cloud-run-sanitized-evidence.json"
        )
        self.assertIn(expected, self.workflow)
        self.assertNotIn("path: |" + chr(92) + "n", self.workflow)

    def test_rotator_metadata_audit_runs_after_cloud_env_failure(self):
        marker = "      - name: Audit canonical Dhan rotator and production broker without reading token payloads"
        segment = self.workflow.split(marker, 1)[1].split("      - name:", 1)[0]
        self.assertIn("if: " + chr(36) + "{{ !cancelled() }}", segment)
        self.assertIn("run: python -S scripts/dhan_canonical_rotation_readonly.py", segment)
        self.assertNotIn("continue-on-error:", segment)
        self.assertIn("PYTHONPATH: ''", segment)

    def test_get_only_broker_proof_runs_after_cloud_safety_failure(self):
        # The existing Cloud Run env comparison must remain a blocking FAIL.
        self.assertIn("python -S scripts/cloud_run_env_contract.py", self.workflow)
        marker = "      - name: Verify deterministic PAPER lifecycle and Dhan GET orders"
        segment = self.workflow.split(marker, 1)[1].split("      - name:", 1)[0]
        self.assertIn("if: " + chr(36) + "{{ !cancelled() }}", segment)
        self.assertIn("run: python scripts/cloud_verify_readonly.py", segment)
        self.assertNotIn("continue-on-error:", segment)

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
