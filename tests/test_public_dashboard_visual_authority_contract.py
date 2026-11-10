from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


class PublicDashboardVisualAuthorityContractTests(unittest.TestCase):
    def test_public_dashboard_proof_has_no_redundant_raw_chrome_precheck(self):
        proof = Path("scripts/gcp_public_dashboard_runtime_proof.py").read_text(encoding="utf-8")
        self.assertNotIn("--dump-dom", proof)
        self.assertNotIn("--virtual-time-budget", proof)
        self.assertNotIn("google-chrome", proof)
        self.assertNotIn("def _render_dom", proof)
        self.assertNotIn("def _capture(", proof)

    def test_rendered_ui_authority_is_fail_closed_webdriver_matrix(self):
        proof = Path("scripts/gcp_public_dashboard_runtime_proof.py").read_text(encoding="utf-8")
        self.assertIn('CANONICAL_VISUAL_TAB = "decision-intel"', proof)
        self.assertIn('"visual_authority": "webdriver_tab_matrix"', proof)
        self.assertIn('"source": "webdriver_tab_matrix"', proof)
        self.assertIn("ui_tab_visual_matrix_sha_mismatch", proof)
        self.assertIn("canonical_visual_screenshot_hash_mismatch", proof)
        self.assertIn("canonical_visual_dashboard_key_prompt_rendered", proof)
        self.assertIn("canonical_visual_system3_marker_missing", proof)
        self.assertIn("ui_tab_visual_matrix_count_mismatch", proof)

    def test_tab_matrix_subprocess_receives_reconciled_expected_sha(self):
        import scripts.gcp_public_dashboard_runtime_proof as proof

        expected_sha = "a" * 40
        old_out, old_expected = proof.OUT, proof.EXPECTED_SHA
        try:
            with tempfile.TemporaryDirectory() as tmp:
                proof.OUT = Path(tmp)
                proof.EXPECTED_SHA = expected_sha
                (proof.OUT / "tab_visual_matrix.json").write_text(
                    json.dumps({"state": "PASS", "expected_sha": expected_sha}),
                    encoding="utf-8",
                )
                with patch.object(
                    proof.subprocess,
                    "run",
                    return_value=SimpleNamespace(returncode=0, stdout="", stderr=""),
                ) as run:
                    matrix = proof._run_tab_matrix()
                self.assertEqual(matrix["expected_sha"], expected_sha)
                self.assertEqual(run.call_args.kwargs["env"]["GITHUB_SHA"], expected_sha)
        finally:
            proof.OUT, proof.EXPECTED_SHA = old_out, old_expected

    def test_matrix_runs_before_canonical_visual_materialization(self):
        proof = Path("scripts/gcp_public_dashboard_runtime_proof.py").read_text(encoding="utf-8")
        matrix_pos = proof.index("matrix = _run_tab_matrix()")
        visual_pos = proof.index("_materialize_canonical_visual(matrix")
        self.assertLess(matrix_pos, visual_pos)

    def test_proof_remains_read_only_and_live_off(self):
        proof = Path("scripts/gcp_public_dashboard_runtime_proof.py").read_text(encoding="utf-8")
        self.assertIn('"live_trading_enabled": False', proof)
        self.assertIn('"api_key_sent_for_dashboard_reads": False', proof)
        self.assertIn('"cookie_sent_for_dashboard_reads": False', proof)
        for marker in ("place" + "_order(", "modify" + "_order(", "cancel" + "_order("):
            self.assertNotIn(marker, proof)


if __name__ == "__main__":
    unittest.main()
