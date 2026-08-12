from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CloudRunDigestGuardContractTests(unittest.TestCase):
    def test_guard_wraps_existing_deployer_instead_of_reimplementing_state_machine(self) -> None:
        text = (ROOT / "scripts/gcp_cloud_run_auto_deploy_digest_guard.py").read_text(encoding="utf-8")
        tree = ast.parse(text)
        imports = {
            alias.name
            for node in tree.body
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertIn("gcp_cloud_run_auto_deploy", imports)
        self.assertIn("deployer._assert_candidate_image = _assert_candidate_image", text)
        self.assertIn("return deployer.main()", text)

    def test_guard_uses_fail_closed_digest_provenance(self) -> None:
        text = (ROOT / "scripts/gcp_cloud_run_auto_deploy_digest_guard.py").read_text(encoding="utf-8")
        self.assertIn("from gcp_image_provenance import assert_same_artifact_image", text)
        self.assertIn("assert_same_artifact_image(image, deployed_image)", text)
        self.assertIn("candidate image missing from revision", text)
        self.assertIn("CANDIDATE_IMAGE_PROVENANCE_OK", text)

    def test_original_deployer_safety_contract_remains_present(self) -> None:
        text = (ROOT / "scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
        for marker in (
            '"--no-traffic"',
            'f"--tag={CANDIDATE_TAG}"',
            'f"--to-revisions={candidate}=100"',
            '("LIVE_TRADING_ENABLED", "0")',
            '("SYSTEM3_LIVE_TRADING_ALLOWED", "0")',
            '("AUTO_EXECUTE_TRADES", "0")',
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
