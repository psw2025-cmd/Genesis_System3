from __future__ import annotations

import unittest
from pathlib import Path


class ObsoleteDashboardAuthWarmupTests(unittest.TestCase):
    def test_authenticated_dashboard_warmup_tool_is_removed(self):
        self.assertFalse(Path("tools/dashboard_authenticated_shell_warmup.mjs").exists())

    def test_cloud_e2e_proof_does_not_reintroduce_retired_dashboard_auth(self):
        text = Path("scripts/cloud_e2e_proof.py").read_text(encoding="utf-8")
        retired_header = "X-" + "API-Key"
        retired_session_path = "/api/auth/" + "session"
        retired_env = "DASHBOARD_" + "API_KEY"
        self.assertNotIn(retired_header, text)
        self.assertNotIn(retired_session_path, text)
        self.assertNotIn(retired_env, text)
        self.assertIn("public_readonly", text)


if __name__ == "__main__":
    unittest.main()
