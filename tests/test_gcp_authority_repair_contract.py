from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "deploy/gcp/system3_iam_baseline.json"
REPAIR_SCRIPT = ROOT / "scripts/gcp_authority_repair.py"
REPAIR_WORKFLOW = ROOT / ".github/workflows/gcp-authority-repair.yml"
BOOTSTRAP = ROOT / "deploy/gcp/bootstrap_autonomous_authority.sh"


class GcpAuthorityRepairContractTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(BASELINE.read_text(encoding="utf-8"))
        self.primary = "serviceAccount:gs3-iam-repair@system3-openalgo-safe.iam.gserviceaccount.com"
        self.fallback = "serviceAccount:gs3-iam-repair-b@system3-openalgo-safe.iam.gserviceaccount.com"
        self.repair = {self.primary, self.fallback}

    def test_dual_repair_identities_have_recovery_but_not_runtime_admin(self):
        bindings = self.data["project_bindings"]
        by_member = {}
        for item in bindings:
            by_member.setdefault(item["member"], set()).add(item["role"])
        for member in self.repair:
            roles = by_member.get(member, set())
            self.assertIn("roles/resourcemanager.projectIamAdmin", roles)
            self.assertIn("roles/iam.roleAdmin", roles)
            self.assertIn("projects/system3-openalgo-safe/roles/GenesisSystem3IamRepair", roles)
            self.assertNotIn("roles/run.admin", roles)
            self.assertNotIn("roles/owner", roles)
            self.assertNotIn("roles/editor", roles)

    def test_repair_identities_have_no_broker_secret_payload_authority(self):
        for item in self.data["secret_bindings"]:
            if item["member"] in self.repair:
                self.fail(f"repair identity unexpectedly present in secret payload binding: {item}")

    def test_repair_identities_cannot_invoke_dhan_rotator(self):
        dhan = self.data["dhan_job"]
        required = set(dhan["required_invokers"])
        forbidden = set(dhan["forbidden_invokers"])
        self.assertTrue(self.repair.isdisjoint(required))
        self.assertTrue(self.repair.issubset(forbidden))

    def test_custom_role_excludes_secret_payload_job_execute_and_key_creation(self):
        permissions = set(self.data["repair"]["custom_role_permissions"])
        forbidden = {
            "run.jobs.run",
            "run.jobs.runWithOverrides",
            "secretmanager.versions.access",
            "secretmanager.versions.add",
            "iam.serviceAccountKeys.create",
        }
        self.assertTrue(permissions.isdisjoint(forbidden))
        self.assertIn("iam.serviceAccounts.setIamPolicy", permissions)
        self.assertIn("secretmanager.secrets.setIamPolicy", permissions)
        self.assertIn("run.jobs.setIamPolicy", permissions)

    def test_reconciler_is_secret_safe_and_non_trading(self):
        text = REPAIR_SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("access_secret_version", text)
        self.assertEqual(text.count("secretmanager.versions.access"), 1)
        self.assertEqual(text.count("secretmanager.versions.add"), 1)
        self.assertEqual(text.count("iam.serviceAccountKeys.create"), 1)
        self.assertNotIn("AUTO_EXECUTE_TRADES=1", text)
        self.assertNotIn("LIVE_TRADING_ENABLED=1", text)
        self.assertNotIn('"execute"', text)
        for marker in (
            '"secret_payloads_accessed": False',
            '"service_account_keys_created": False',
            '"dhan_rotation_job_executed": False',
            '"live_trading_changed": False',
            '"order_action_performed": False',
        ):
            self.assertIn(marker, text)

    def test_repair_workflow_has_primary_fallback_and_bounded_retry(self):
        text = REPAIR_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('workflows: ["Cloud Run Auto Deploy"]', text)
        self.assertIn("gs3-iam-repair@system3-openalgo-safe.iam.gserviceaccount.com", text)
        self.assertIn("gs3-iam-repair-b@system3-openalgo-safe.iam.gserviceaccount.com", text)
        self.assertIn("needs.primary-repair.result == 'failure'", text)
        self.assertIn("needs.primary-repair.outputs.changed == 'true'", text)
        self.assertIn("needs.fallback-repair.outputs.changed == 'true'", text)
        self.assertEqual(text.count("gh workflow run cloud-run-auto-deploy.yml"), 1)
        self.assertNotIn("gcloud run jobs execute", text)

    def test_bootstrap_uses_exact_repair_workflow_claim_and_keyless_identities(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn("attribute.workflow_ref=assertion.workflow_ref", text)
        self.assertIn("attribute.authority=assertion.workflow_ref==", text)
        self.assertIn(".github/workflows/gcp-authority-repair.yml@refs/heads/main", text)
        self.assertIn("attribute.authority/repair", text)
        self.assertIn("gs3-iam-repair@", text)
        self.assertIn("gs3-iam-repair-b@", text)
        self.assertNotIn("service-account-key", text.lower())
        self.assertNotIn("gcloud run jobs execute", text)

    def test_policy_keeps_gcp_authority_and_live_off(self):
        policy = self.data["policy"]
        self.assertIs(policy["gcp_is_production_authority"], True)
        self.assertIs(policy["render_is_production_authority"], False)
        self.assertIs(policy["service_account_keys_allowed"], False)
        self.assertIs(policy["live_trading_enabled"], False)
        self.assertIs(policy["auto_execute_trades"], False)
        self.assertIs(policy["dhan_web_self_heal_mint"], False)


if __name__ == "__main__":
    unittest.main()
