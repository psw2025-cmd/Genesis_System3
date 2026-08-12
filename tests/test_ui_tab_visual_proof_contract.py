from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path


class UiTabVisualProofContractTests(unittest.TestCase):
    def test_visual_proof_covers_every_sidebar_tab_exactly_once(self):
        sidebar = Path("dashboard/frontend/src/components/Sidebar.tsx").read_text(encoding="utf-8")
        proof = Path("scripts/gcp_ui_tab_visual_proof.py").read_text(encoding="utf-8")

        sidebar_ids = re.findall(r"\{ id: '([^']+)',\s*label:", sidebar)
        self.assertEqual(len(sidebar_ids), 22)
        self.assertEqual(len(sidebar_ids), len(set(sidebar_ids)))

        tree = ast.parse(proof)
        proof_ids: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "TABS":
                        value = ast.literal_eval(node.value)
                        proof_ids = [str(row[0]) for row in value]
        self.assertEqual(proof_ids, sidebar_ids)
        self.assertEqual(len(proof_ids), 22)

    def test_app_supports_only_canonical_tab_deep_links(self):
        app = Path("dashboard/frontend/src/App.tsx").read_text(encoding="utf-8")
        sidebar = Path("dashboard/frontend/src/components/Sidebar.tsx").read_text(encoding="utf-8")
        self.assertIn("DASHBOARD_TAB_IDS", app)
        self.assertIn("URLSearchParams(window.location.search).get('tab')", app)
        self.assertIn("DASHBOARD_TAB_IDS.has(requested)", app)
        self.assertIn("useRef(false)", app)
        self.assertIn("initialized.current = true", app)
        self.assertIn("window.history.replaceState", app)
        self.assertIn("export const DASHBOARD_TAB_IDS", sidebar)

    def test_visual_proof_is_read_only_and_has_desktop_mobile_evidence(self):
        proof = Path("scripts/gcp_ui_tab_visual_proof.py").read_text(encoding="utf-8")
        self.assertIn('"trading_mutations_called": False', proof)
        self.assertIn('"desktop": "1600x1000"', proof)
        self.assertIn('"mobile": "430x932"', proof)
        self.assertIn("PENDING_USER_REVIEW", proof)
        self.assertIn("dashboard_api_key_prompt_rendered", proof)
        for marker in ("place" + "_order(", "modify" + "_order(", "cancel" + "_order("):
            self.assertNotIn(marker, proof)

    def test_public_dashboard_proof_invokes_tab_matrix_after_serving_revision_binding(self):
        proof = Path("scripts/gcp_public_dashboard_runtime_proof.py").read_text(encoding="utf-8")
        self.assertIn("single_100_percent_serving_revision", proof)
        self.assertIn("serving_deploy_git_sha_mismatch", proof)
        self.assertIn("scripts/gcp_ui_tab_visual_proof.py", proof)
        self.assertIn("tab_visual_pass_count", proof)


if __name__ == "__main__":
    unittest.main()
