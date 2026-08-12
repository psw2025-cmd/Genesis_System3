from __future__ import annotations

import os
import subprocess
import sys
import unittest


class CloudRunSecureAppImportTests(unittest.TestCase):
    def test_exact_cloud_run_entrypoint_scrubs_dashboard_auth_drift_and_has_zero_unknown_mutations(self):
        env = dict(os.environ)
        env.update(
            {
                "LIVE_TRADING_ENABLED": "0",
                "SYSTEM3_LIVE_TRADING_ALLOWED": "0",
                "AUTO_EXECUTE_TRADES": "0",
                "ANALYZE_MODE": "1",
                "SYSTEM3_MODE": "ANALYZER",
                "SYSTEM3_REAL_ONLY": "1",
                "CLOUD_PAPER_ENGINE": "0",
                # Adversarial legacy drift: serving architecture must erase these
                # before importing the large legacy backend.
                "REQUIRE_API_KEY": "true",
                "API_KEY": "dummy-must-never-be-authority",
                "DASHBOARD_API_KEY": "dummy-must-never-be-authority",
                "ENABLE_DASHBOARD_AUTH": "true",
                "DEFER_INSTRUMENT_WARMUP": "1",
                # CI validates route ownership without external GCP state.
                "SYSTEM3_STATE_BACKEND": "local",
                "SYSTEM3_STATE_BACKEND_REQUIRED": "0",
                "SYSTEM3_SYNC_INTERVAL_S": "0",
            }
        )
        code = r'''
import os
from dashboard.backend.secure_app import app
from dashboard.backend import app as legacy
from dashboard.backend.mutation_policy import duplicate_write_routes, unclassified_write_routes

for name in ("REQUIRE_API_KEY", "API_KEY", "DASHBOARD_API_KEY", "ENABLE_DASHBOARD_AUTH"):
    assert name not in os.environ, (name, "was not scrubbed")
assert legacy._REQUIRE_API_KEY is False
assert legacy._API_KEY == ""

unknown = unclassified_write_routes(app)
duplicates = duplicate_write_routes(app)
assert not unknown, [(row.method, row.path) for row in unknown]
assert not duplicates, duplicates

route_methods = {
    (getattr(route, "path", ""), method)
    for route in app.routes
    for method in (getattr(route, "methods", set()) or set())
}
assert ("/api/auth/session", "POST") not in route_methods
assert ("/api/auth/logout", "POST") not in route_methods
assert ("/api/auth/status", "GET") in route_methods
print("SECURE_APP_PUBLIC_READONLY_IMPORT_OK", len(app.routes))
'''
        proc = subprocess.run(
            [sys.executable, "-c", code],
            env=env,
            text=True,
            capture_output=True,
            timeout=90,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            msg=f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
        )
        self.assertIn("SECURE_APP_PUBLIC_READONLY_IMPORT_OK", proc.stdout)
        self.assertNotIn("[startup] instruments:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
