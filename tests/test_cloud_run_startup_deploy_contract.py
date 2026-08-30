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

    def test_cloud_paper_engine_starts_alongside_dashboard(self) -> None:
        text = (ROOT / "scripts/start_cloud_run.py").read_text(encoding="utf-8")
        self.assertIn('os.getenv("CLOUD_PAPER_ENGINE", "0")', text)
        self.assertIn("target=_run_cloud_paper_engine", text)
        self.assertIn('name="system3-cloud-paper-engine"', text)
        self.assertIn("daemon=True", text)

    def test_cloud_paper_engine_has_no_broker_order_import(self) -> None:
        text = (ROOT / "scripts/cloud_paper_engine.py").read_text(encoding="utf-8")
        self.assertIn("from src.trading.paper_executor import PaperExecutor", text)
        for forbidden in ("place_order", "submit_order", "order_placement", "dhanhq", "DhanContext"):
            self.assertNotIn(forbidden, text)
        self.assertIn('"LIVE_TRADING_ENABLED", "0"', (ROOT / "scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8"))

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

    def test_web_runtime_is_automated_paper_with_live_flags_forced_off(self) -> None:
        text = (ROOT / "scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
        for marker in (
            '"ANALYZE_MODE": "0"',
            '"SYSTEM3_MODE": "PAPER"',
            '"CLOUD_PAPER_ENGINE": "1"',
            '"AUTO_EXECUTE_TRADES": "1"',
            '"LIVE_TRADING_ENABLED": "0"',
            '"SYSTEM3_LIVE_TRADING_ALLOWED": "0"',
        ):
            self.assertIn(marker, text)
        self.assertIn("cloud_paper_runtime_refuses_live_trading", text)


if __name__ == "__main__":
    unittest.main()
