from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "deploy/gcp/system3_iam_baseline.json"
REPAIR_SCRIPT = ROOT / "scripts/gcp_authority_repair.py"
REPAIR_WORKFLOW = ROOT / ".github/workflows/gcp-authority-repair.yml"
CLOUD_DEPLOY_WORKFLOW = ROOT / ".github/workflows/cloud-run-auto-deploy.yml"
BOOTSTRAP = ROOT / "deploy/gcp/bootstrap_autonomous_authority.sh"
BOOTSTRAP_ALL = ROOT / "deploy/gcp/bootstrap_all.sh"


class GcpAuthorityRepairContractTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(BASELINE.read_text(encoding="utf-8"))
        self.deployer = "serviceAccount:genesis-system3-automation@system3-openalgo-safe.iam.gserviceaccount.com"
        self.primary = "serviceAccount:gs3-iam-repair@system3-openalgo-safe.iam.gserviceaccount.com"
        self.fallback = "serviceAccount:gs3-iam-repair-b@system3-openalgo-safe.iam.gserviceaccount.com"
        self.repair = {self.primary, self.fallback}

    def test_dual_repair_identities_have_recovery_but_not_runtime_admin(self):
        by_member = {}
        for item in self.data["project_bindings"]:
            by_member.setdefault(item["member"], set()).add(item["role"])
        for member in self.repair:
            roles = by_member.get(member, set())
            self.assertIn("roles/resourcemanager.projectIamAdmin", roles)
            self.assertIn("roles/iam.roleAdmin", roles)
            self.assertIn("projects/system3-openalgo-safe/roles/GenesisSystem3IamRepair", roles)
            self.assertTrue({"roles/run.admin", "roles/owner", "roles/editor"}.isdisjoint(roles))

    def test_secret_payload_denylist_exactly_covers_deployer_and_repairs(self):
        safety = self.data["secret_safety"]
        self.assertEqual(
            set(safety["forbidden_payload_members"]),
            {self.deployer, self.primary, self.fallback},
        )
        self.assertEqual(
            set(safety["forbidden_payload_roles"]),
            {"roles/secretmanager.secretAccessor", "roles/secretmanager.secretVersionAdder"},
        )
        self.assertTrue(safety["protected_secrets"])
        forbidden_members = {self.deployer, self.primary, self.fallback}
        for item in self.data["secret_bindings"]:
            self.assertFalse(
                item["member"] in forbidden_members
                and item["role"] in set(safety["forbidden_payload_roles"]),
                item,
            )

    def test_repair_identities_cannot_invoke_dhan_rotator(self):
        dhan = self.data["dhan_job"]
        self.assertTrue(self.repair.isdisjoint(set(dhan["required_invokers"])))
        self.assertTrue(self.repair.issubset(set(dhan["forbidden_invokers"])))

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

    def test_reconciler_is_secret_safe_non_trading_and_removes_known_bad_secret_iam(self):
        text = REPAIR_SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("access_secret_version", text)
        self.assertEqual(text.count("secretmanager.versions.access"), 1)
        self.assertEqual(text.count("secretmanager.versions.add"), 1)
        self.assertEqual(text.count("iam.serviceAccountKeys.create"), 1)
        self.assertIn("remove_known_forbidden_payload_role", text)
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

    def test_repair_workflow_has_primary_fallback_and_readonly_bounded_retry(self):
        text = REPAIR_WORKFLOW.read_text(encoding="utf-8")
        deploy = CLOUD_DEPLOY_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('workflows: ["Cloud Run Auto Deploy"]', text)
        self.assertIn("gs3-iam-repair@system3-openalgo-safe.iam.gserviceaccount.com", text)
        self.assertIn("gs3-iam-repair-b@system3-openalgo-safe.iam.gserviceaccount.com", text)
        self.assertIn("needs.primary-repair.result == 'failure'", text)
        self.assertIn("needs.primary-repair.outputs.changed == 'true'", text)
        self.assertIn("needs.fallback-repair.outputs.changed == 'true'", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("gh workflow run", text)
        self.assertEqual(text.count("uses: ./.github/workflows/cloud-run-auto-deploy.yml"), 1)
        self.assertIn("workflow_call:", deploy)
        self.assertNotIn("gcloud run jobs execute", text)

    def test_bootstrap_exact_workflow_claim_keyless_and_secret_cleanup(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn("attribute.workflow_ref=assertion.workflow_ref", text)
        self.assertIn("attribute.authority=assertion.workflow_ref==", text)
        self.assertIn(".github/workflows/gcp-authority-repair.yml@refs/heads/main", text)
        self.assertIn("attribute.authority/repair", text)
        self.assertIn("gs3-iam-repair@", text)
        self.assertIn("gs3-iam-repair-b@", text)
        self.assertIn("gcloud secrets remove-iam-policy-binding", text)
        self.assertNotIn("service-account-key", text.lower())
        self.assertNotIn("gcloud run jobs execute", text)

    def test_single_entry_bootstrap_tests_applies_and_rechecks_baseline(self):
        text = BOOTSTRAP_ALL.read_text(encoding="utf-8")
        self.assertIn("bootstrap_github_wif.sh", text)
        self.assertIn("bootstrap_autonomous_authority.sh", text)
        self.assertIn("python3 -m unittest -q tests.test_gcp_authority_repair_contract", text)
        self.assertEqual(text.count("python3 scripts/gcp_authority_repair.py"), 2)
        self.assertIn("python3 scripts/gcp_authority_repair.py --apply", text)
        self.assertIn("SYSTEM3_FULL_AUTHORITY_BOOTSTRAP_OK", text)

    def test_policy_keeps_gcp_live_safety_and_declares_temporary_authority_debt(self):
        policy = self.data["policy"]
        self.assertIs(policy["gcp_is_production_authority"], True)
        self.assertIs(policy["render_is_production_authority"], False)
        self.assertIs(policy["service_account_keys_allowed"], False)
        self.assertIs(policy["live_trading_enabled"], False)
        self.assertIs(policy["auto_execute_trades"], False)
        self.assertIs(policy["dhan_web_self_heal_mint"], False)
        self.assertIs(policy["strict_scheduler_only_iam"], False)
        self.assertIs(policy["deployer_run_admin_temporary"], False)


if __name__ == "__main__":
    unittest.main()
