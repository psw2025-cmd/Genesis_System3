from __future__ import annotations

import unittest
from pathlib import Path


class PublicReadonlyRuntimeSentinelTests(unittest.TestCase):
    def test_deploy_runtime_proof_matches_serving_auth_status_contract(self):
        workflow = Path(".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
        secure_app = Path("dashboard/backend/secure_app.py").read_text(encoding="utf-8")

        for marker in (
            '"required": False',
            '"configured": False',
            '"authenticated": False',
            '"mode": "public_readonly"',
            '"credential_surface": "REMOVED"',
            '"session": None',
        ):
            self.assertIn(marker, secure_app)

        for marker in (
            '.required == false',
            '.configured == false',
            '.authenticated == false',
            '.mode == "public_readonly"',
            '.credential_surface == "REMOVED"',
            '.session == null',
        ):
            self.assertIn(marker, workflow)

        self.assertNotIn('.mode == "auth_disabled"', workflow)


if __name__ == "__main__":
    unittest.main()
