"""Offline schema, privacy and fail-closed inventory regression tests."""
import unittest
from scripts.cloud_infrastructure_inventory import SCOPES, collect, safe_name, summarize


class InventoryTests(unittest.TestCase):
    def test_scopes_read_only(self):
        self.assertGreaterEqual(len(SCOPES), 10)
        self.assertTrue(all(not any(word in args for word in ("access", "delete", "deploy")) for args in SCOPES.values()))

    def test_sanitized_success(self):
        def runner(args):
            if args[:2] == ("projects", "describe"):
                return {"projectId": "system3-openalgo-safe", "lifecycleState": "ACTIVE", "secret": "NEVER_PRINT"}
            if args[:3] == ("run", "services", "list"):
                return [{"metadata": {"name": "genesis-system3-web"}},
                        {"metadata": {"name": "genesis-system3-web-staging"}}]
            return [{"name": "projects/p/secrets/token", "payload": "NEVER_PRINT"}] if args[:2] == ("secrets", "list") else []
        proof = collect(runner)
        self.assertEqual(proof["status"], "PASS")
        self.assertTrue(proof["scopes"]["cloud_run_services"]["canonical_production_present"])
        self.assertNotIn("NEVER_PRINT", str(proof))

    def test_permission_failure_not_pass(self):
        def runner(args):
            if args[:2] == ("secrets", "list"):
                raise RuntimeError("PRIVATE_UPSTREAM_ERROR")
            return {"projectId": "system3-openalgo-safe"} if args[:2] == ("projects", "describe") else []
        proof = collect(runner)
        self.assertEqual(proof["status"], "NOT_VERIFIED")
        self.assertNotIn("PRIVATE_UPSTREAM_ERROR", str(proof))

    def test_schema_error(self):
        with self.assertRaises(ValueError):
            summarize("cloud_run_jobs", {})

    def test_private_identity_filter(self):
        self.assertIsNone(safe_name({"name": "person@example.com"}))
        self.assertEqual(safe_name({"name": "projects/p/secrets/token"}), "token")


if __name__ == "__main__":
    unittest.main()
