from __future__ import annotations

import unittest
from pathlib import Path


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
