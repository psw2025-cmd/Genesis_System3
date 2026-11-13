"""Offline schema, privacy and fail-closed inventory regression tests."""
import unittest
from scripts.cloud_infrastructure_inventory import (
    SCOPES, _safe_gcloud_error, collect, safe_name, summarize,
)


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
            if args[:3] == ("projects", "get-iam-policy", "system3-openalgo-safe"):
                return {"bindings": [{"role": "roles/viewer", "members": ["secret@example.com"]}], "version": 1}
            if args[:3] == ("billing", "projects", "describe"):
                return {"billingEnabled": True, "billingAccountName": "SECRET_BILLING_ACCOUNT"}
            return [{"name": "projects/p/secrets/token", "payload": "NEVER_PRINT"}] if args[:2] == ("secrets", "list") else []
        proof = collect(runner)
        self.assertEqual(proof["status"], "PASS")
        self.assertTrue(proof["scopes"]["cloud_run_services"]["canonical_production_present"])
        self.assertNotIn("NEVER_PRINT", str(proof))
        self.assertNotIn("SECRET_BILLING_ACCOUNT", str(proof))
        self.assertNotIn("secret@example.com", str(proof))

    def test_missing_cloud_run_targets_fail_closed(self):
        def runner(args):
            if args[:2] == ("projects", "describe"):
                return {"projectId": "system3-openalgo-safe", "lifecycleState": "ACTIVE"}
            if args[:2] == ("projects", "get-iam-policy"):
                return {"bindings": [], "version": 1}
            if args[:2] == ("billing", "projects"):
                return {"billingEnabled": True}
            return []
        proof = collect(runner)
        self.assertEqual(proof["status"], "NOT_VERIFIED")
        self.assertEqual(proof["scopes"]["cloud_run_services"]["status"], "FAIL")

    def test_unlinked_billing_fail_closed(self):
        self.assertEqual(summarize("billing_linkage", {"billingEnabled": False})["status"], "FAIL")

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

    def test_gcloud_error_is_classified_without_echoing_provider_text(self):
        private = "PERMISSION_DENIED: private-resource and token=do-not-print"
        self.assertEqual(_safe_gcloud_error(private), "GCLOUD_PERMISSION_DENIED")
        proof = collect(lambda _args: (_ for _ in ()).throw(RuntimeError("GCLOUD_PERMISSION_DENIED")))
        self.assertNotIn("do-not-print", str(proof))
        self.assertEqual(proof["scopes"]["project"]["error_code"], "GCLOUD_PERMISSION_DENIED")

    def test_windows_launcher_uses_powershell_script(self):
        from unittest.mock import patch
        import scripts.cloud_infrastructure_inventory as inventory

        with patch.object(inventory.shutil, "which", side_effect=lambda name: {
                 "gcloud": "/opt/google-cloud-sdk/bin/gcloud.CMD",
                 "powershell.exe": "/powershell.exe",
             }.get(name)), patch.object(inventory.Path, "is_file", return_value=True):
            command = inventory._gcloud_command(("projects", "describe", "project-id"), windows=True)
        self.assertIn("-File", command)
        self.assertTrue(command[command.index("-File") + 1].endswith("gcloud.ps1"))
        self.assertEqual(command[-3:], ["project-id", "--format=json", "--quiet"])


if __name__ == "__main__":
    unittest.main()
