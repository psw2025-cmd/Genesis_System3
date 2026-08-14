from __future__ import annotations

import ast
import unittest
from pathlib import Path


JOB = Path("scripts/gcp_dhan_token_rotation_job.py")
PATCH = Path("core/brokers/dhan/cloud_runtime_patch.py")


class DhanRotationVersionCoordinationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.job = JOB.read_text(encoding="utf-8")
        cls.patch = PATCH.read_text(encoding="utf-8")
        ast.parse(cls.job)
        ast.parse(cls.patch)

    def test_web_self_heal_passes_non_secret_expected_version_override(self):
        self.assertIn("DHAN_ROTATION_EXPECTED_VERSION", self.patch)
        self.assertIn('"overrides"', self.patch)
        self.assertIn('"containerOverrides"', self.patch)
        self.assertIn('"expected_secret_version"', self.patch)
        self.assertNotIn('"DHAN_PIN"', self.patch)
        self.assertNotIn('"DHAN_TOTP_SECRET"', self.patch)

    def test_job_uses_authoritative_latest_secret_not_mounted_access_token_snapshot(self):
        self.assertIn("_latest_token_snapshot", self.job)
        self.assertIn('versions/latest', self.job)
        self.assertNotIn('token = os.getenv("DHAN_ACCESS_TOKEN"', self.job)
        self.assertIn('"raw_token_exposed": False', self.job)

    def test_cloud_run_execution_provides_bounded_stagger_and_recheck(self):
        self.assertIn("CLOUD_RUN_EXECUTION", self.job)
        self.assertIn("_execution_stagger_s", self.job)
        self.assertIn("hashlib.sha256(execution.encode", self.job)
        self.assertIn("time.sleep(settle_s)", self.job)
        self.assertIn("settled_token, settled_secret = _latest_token_snapshot()", self.job)
        self.assertIn("SKIPPED_CONCURRENT_ROTATION_WON", self.job)
        self.assertIn("post_stagger_latest_valid", self.job)

    def test_coordination_never_weakens_trading_safety_or_order_boundary(self):
        for text in (self.job, self.patch):
            self.assertIn('"live_trading_enabled": False', text)
            self.assertIn('"raw_token_exposed": False', text)
        self.assertIn('os.environ["LIVE_TRADING_ENABLED"] = "0"', self.job)
        self.assertIn('os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"', self.job)
        self.assertIn('os.environ["AUTO_EXECUTE_TRADES"] = "0"', self.job)
        self.assertIn('"order_endpoints_called": False', self.job)
        for marker in ("place_order(", "modify_order(", "cancel_order("):
            self.assertNotIn(marker, self.job)
            self.assertNotIn(marker, self.patch)

    def test_expected_version_is_only_metadata_and_not_a_token_value(self):
        self.assertIn("before_version = str(before.get(\"secret_version\")", self.patch)
        self.assertIn('"value": before_version', self.patch)
        self.assertIn("expected_version = os.getenv(\"DHAN_ROTATION_EXPECTED_VERSION\"", self.job)
        self.assertIn("expected_secret_version=expected_version", self.job)


if __name__ == "__main__":
    unittest.main()
