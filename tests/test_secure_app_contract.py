import unittest
from pathlib import Path


class SecureAppContractTests(unittest.TestCase):
    def test_cloud_run_uses_secure_public_readonly_wrapper(self):
        launcher = Path("scripts/start_cloud_run.py").read_text(encoding="utf-8")
        self.assertIn('"dashboard.backend.secure_app:app"', launcher)
        self.assertNotIn('"dashboard.backend.app:app"', launcher)

    def test_wrapper_permanently_removes_dashboard_credential_authority(self):
        source = Path("dashboard/backend/secure_app.py").read_text(encoding="utf-8")
        self.assertIn("Permanent public-readonly security boundary", source)
        self.assertIn("_RETIRED_DASHBOARD_ENV", source)
        self.assertIn('"/api/auth/" + "session"', source)
        self.assertIn('"/api/auth/" + "logout"', source)
        self.assertIn('"mode": "public_readonly"', source)
        self.assertIn('"credential_surface": "REMOVED"', source)
        self.assertIn('"session": None', source)
        self.assertIn("PUBLIC_DASHBOARD_READ_ONLY", source)
        self.assertIn('"live_mutation": "HARD_DENY"', source)
        self.assertIn('"live_approval": "HARD_DENY"', source)
        self.assertNotIn("_SESSION_TRUTH", source)
        self.assertNotIn("SessionTruthStore", source)

    def test_retired_server_session_and_authenticated_helpers_are_absent(self):
        self.assertFalse(Path("dashboard/backend/session_truth.py").exists())
        self.assertFalse(Path("tests/test_session_truth.py").exists())
        self.assertFalse(Path("tools/dashboard_auth_smoke.py").exists())
        self.assertFalse(Path("tools/run_authenticated_failure_tracker.py").exists())

    def test_obsolete_browser_login_and_session_hooks_are_absent(self):
        self.assertFalse(Path("dashboard/frontend/src/components/LoginPage.tsx").exists())
        self.assertFalse(Path("dashboard/frontend/src/hooks/useAuth.ts").exists())

    def test_no_live_or_order_authority_added_to_secure_boundary(self):
        source = Path("dashboard/backend/secure_app.py").read_text(encoding="utf-8")
        self.assertNotIn("place_order(", source)
        self.assertNotIn("modify_order(", source)
        self.assertNotIn("cancel_order(", source)
        self.assertNotIn("LIVE_TRADING_ENABLED = True", source)


if __name__ == "__main__":
    unittest.main()
