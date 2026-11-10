from __future__ import annotations

import os
import subprocess
import sys
import unittest


class CloudRunSecureAppImportTests(unittest.TestCase):
    def test_exact_cloud_run_entrypoint_imports_with_zero_unknown_mutations(self):
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
                "REQUIRE_API_KEY": "false",
                "DEFER_INSTRUMENT_WARMUP": "1",
                # CI must validate route ownership without requiring external GCP
                # state. Production deploy separately locks Firestore as required.
                "SYSTEM3_STATE_BACKEND": "local",
                "SYSTEM3_STATE_BACKEND_REQUIRED": "0",
                "SYSTEM3_SYNC_INTERVAL_S": "0",
            }
        )
        code = r'''
from dashboard.backend.secure_app import app
from dashboard.backend.mutation_policy import duplicate_write_routes, unclassified_write_routes
unknown = unclassified_write_routes(app)
duplicates = duplicate_write_routes(app)
assert not unknown, [(row.method, row.path) for row in unknown]
assert not duplicates, duplicates
print("SECURE_APP_IMPORT_AND_MUTATION_MANIFEST_OK", len(app.routes))
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
        self.assertIn("SECURE_APP_IMPORT_AND_MUTATION_MANIFEST_OK", proc.stdout)
        # The failed Cloud Run revision spent startup time loading 116,507 rows.
        # With the deploy contract, eager instrument warm-up must not run in CI.
        self.assertNotIn("[startup] instruments:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
