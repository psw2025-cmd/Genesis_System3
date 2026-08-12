import unittest
from pathlib import Path


class SecureAppContractTests(unittest.TestCase):
    def test_cloud_run_uses_secure_public_readonly_wrapper(self):
        launcher = Path("scripts/start_cloud_run.py").read_text(encoding="utf-8")
        self.assertIn('"dashboard.backend.secure_app:app"', launcher)
        self.assertNotIn('"dashboard.backend.app:app"', launcher)

    def test_wrapper_scrubs_retired_dashboard_auth_before_legacy_import(self):
        source = Path("dashboard/backend/secure_app.py").read_text(encoding="utf-8")
        import_pos = source.index("from dashboard.backend import app as legacy")
        scrub_pos = source.index("os.environ.pop")
        self.assertLess(scrub_pos, import_pos)
        self.assertIn("RETIRED_DASHBOARD_ENV", source)
        self.assertIn("legacy._REQUIRE_API_KEY = False", source)
        self.assertIn('legacy._API_KEY = ""', source)
        self.assertIn("strip_retired_dashboard_credentials", source)

    def test_login_logout_and_server_session_authority_are_removed(self):
        source = Path("dashboard/backend/secure_app.py").read_text(encoding="utf-8")
        self.assertFalse(Path("dashboard/backend/session_truth.py").exists())
        self.assertNotIn("get_session_truth_store", source)
        self.assertNotIn("SessionTruth", source)
        self.assertNotIn("set_cookie(", source)
        self.assertNotIn("delete_cookie(", source)
        self.assertNotIn("hmac.compare_digest", source)
        self.assertNotIn("create_dashboard_session", source)
        self.assertNotIn("dashboard_auth_logout", source)

    def test_only_auth_status_survives_as_informational_read(self):
        source = Path("dashboard/backend/secure_app.py").read_text(encoding="utf-8")
        self.assertIn('@app.get("/api/auth/status")', source)
        self.assertIn('"mode": "public_readonly"', source)
        self.assertIn('"credential_surface": "REMOVED"', source)
        self.assertIn('"required": False', source)
        self.assertIn('"configured": False', source)
        self.assertIn('"authenticated": False', source)

    def test_mutation_boundary_is_independent_of_dashboard_visibility(self):
        source = Path("dashboard/backend/secure_app.py").read_text(encoding="utf-8")
        self.assertIn("control_authorized=False", source)
        self.assertIn('"live_mutation": "HARD_DENY"', source)
        self.assertIn('"live_approval": "HARD_DENY"', source)
        self.assertIn('"worker_authority": "DEDICATED_WORKER_TOKEN"', source)
        self.assertIn('"dashboard_credential_authority": "REMOVED"', source)

    def test_obsolete_browser_login_components_are_absent(self):
        self.assertFalse(Path("dashboard/frontend/src/components/LoginPage.tsx").exists())
        self.assertFalse(Path("dashboard/frontend/src/hooks/useAuth.ts").exists())


if __name__ == "__main__":
    unittest.main()
