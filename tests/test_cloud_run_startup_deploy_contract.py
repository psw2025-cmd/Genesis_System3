from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CloudRunStartupDeployContractTests(unittest.TestCase):
    def test_launcher_binds_all_interfaces_and_uses_port_env(self) -> None:
        text = (ROOT / "scripts/start_cloud_run.py").read_text(encoding="utf-8")
        self.assertIn('host="0.0.0.0"', text)
        self.assertIn('os.getenv("PORT", "8080")', text)

    def test_broker_bootstrap_cannot_block_main_server_thread(self) -> None:
        text = (ROOT / "scripts/start_cloud_run.py").read_text(encoding="utf-8")
        tree = ast.parse(text)
        main = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "main"
        )
        main_text = ast.get_source_segment(text, main) or ""
        self.assertIn("threading.Thread", main_text)
        self.assertIn("daemon=True", main_text)
        self.assertNotIn("proof = install()", main_text)
        self.assertIn("uvicorn.run", main_text)

    def test_deployer_uses_zero_traffic_candidate_and_exact_revision_promotion(self) -> None:
        text = (ROOT / "scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
        self.assertIn('"--no-traffic"', text)
        self.assertIn('f"--tag={CANDIDATE_TAG}"', text)
        self.assertIn('f"--to-revisions={candidate}=100"', text)
        self.assertNotIn('if not cur.get("reconciling") and rev:', text)

    def test_failed_candidate_must_preserve_previous_ready_revision(self) -> None:
        text = (ROOT / "scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
        self.assertIn("CANDIDATE_DEPLOY_FAILED", text)
        self.assertIn("if still_ready != previous_ready", text)

    def test_live_flags_are_forced_off_in_deployer(self) -> None:
        text = (ROOT / "scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
        for marker in (
            '("LIVE_TRADING_ENABLED", "0")',
            '("SYSTEM3_LIVE_TRADING_ALLOWED", "0")',
            '("AUTO_EXECUTE_TRADES", "0")',
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
