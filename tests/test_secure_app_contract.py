import unittest
from pathlib import Path


class SecureAppContractTests(unittest.TestCase):
    def test_cloud_run_uses_secure_auth_wrapper(self):
        launcher = Path("scripts/start_cloud_run.py").read_text(encoding="utf-8")
        self.assertIn('"dashboard.backend.secure_app:app"', launcher)
        self.assertNotIn('"dashboard.backend.app:app"', launcher)

    def test_wrapper_replaces_legacy_auth_routes_and_access_check(self):
        source = Path("dashboard/backend/secure_app.py").read_text(encoding="utf-8")
        self.assertIn("legacy._has_dashboard_api_access = _has_dashboard_api_access", source)
        self.assertIn("app.router.routes = [", source)
        self.assertIn("_SESSION_TRUTH.issue", source)
        self.assertIn("_SESSION_TRUTH.validate", source)
        self.assertIn("_SESSION_TRUTH.revoke", source)
        self.assertIn('secure=_forwarded_scheme(request) == "https"', source)
        self.assertIn("_AUTH_MAX_FAILURES = 10", source)

    def test_no_deterministic_session_derivation_in_secure_boundary(self):
        source = Path("dashboard/backend/secure_app.py").read_text(encoding="utf-8")
        self.assertNotIn("system3-dashboard-session-v1", source)
        self.assertNotIn("hashlib.sha256", source)

    def test_browser_key_replay_remains_removed(self):
        login = Path("dashboard/frontend/src/components/LoginPage.tsx").read_text(encoding="utf-8")
        auth = Path("dashboard/frontend/src/hooks/useAuth.ts").read_text(encoding="utf-8")
        self.assertNotIn("sessionStorage.setItem", login)
        self.assertNotIn("s3_api_key", login)
        self.assertNotIn("X-API-Key", auth)
        self.assertIn("credentials:'include'", auth.replace(' ', ''))


if __name__ == "__main__":
    unittest.main()
