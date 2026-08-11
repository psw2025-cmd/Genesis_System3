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
        self.assertIn("_SESSION_TRUTH.login_allowed", source)
        self.assertIn("_SESSION_TRUTH.record_login_failure", source)
        self.assertIn("_SESSION_TRUTH.clear_login_failures", source)
        self.assertNotIn("defaultdict", source)
        self.assertNotIn("_AUTH_ATTEMPTS", source)

    def test_cloud_session_store_is_shared_and_fail_closed(self):
        source = Path("dashboard/backend/session_truth.py").read_text(encoding="utf-8")
        self.assertIn('("firestore" if cloud_runtime else "memory")', source)
        self.assertIn("Cloud Run SessionTruth requires SYSTEM3_SESSION_BACKEND=firestore", source)
        self.assertIn("system3_dashboard_sessions", source)
        self.assertIn("system3_dashboard_login_throttle", source)
        self.assertIn("firestore.Client", source)
        self.assertIn("self._hash_client_key", source)

    def test_no_deterministic_session_derivation_in_secure_boundary(self):
        source = Path("dashboard/backend/secure_app.py").read_text(encoding="utf-8")
        self.assertNotIn("system3-dashboard-session-v1", source)
        self.assertNotIn("hashlib.sha256", source)

    def test_obsolete_browser_login_and_session_hook_are_absent(self):
        # PAPER/ANALYZER viewing is public/read-only. Retaining dead credential
        # entry/session code creates a regression path where a future UI change
        # could accidentally restore a dashboard-key prompt.
        self.assertFalse(Path("dashboard/frontend/src/components/LoginPage.tsx").exists())
        self.assertFalse(Path("dashboard/frontend/src/hooks/useAuth.ts").exists())


if __name__ == "__main__":
    unittest.main()
