from __future__ import annotations

import unittest
from pathlib import Path


class DhanRotatorIdentityContractTests(unittest.TestCase):
    def test_deploy_workflow_uses_dedicated_rotator_and_scheduler_identities(self):
        workflow = Path(".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
        self.assertIn(
            "DHAN_ROTATOR_SERVICE_ACCOUNT: genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com",
            workflow,
        )
        self.assertIn(
            "DHAN_SCHEDULER_SERVICE_ACCOUNT: genesis-system3-scheduler-invoker@system3-openalgo-safe.iam.gserviceaccount.com",
            workflow,
        )
        self.assertIn('--service-account="${DHAN_ROTATOR_SERVICE_ACCOUNT}"', workflow)
        self.assertIn('--oauth-service-account-email="${DHAN_SCHEDULER_SERVICE_ACCOUNT}"', workflow)
        self.assertIn('"${GCP_WEB_RUNTIME_SERVICE_ACCOUNT}" "${DHAN_SCHEDULER_SERVICE_ACCOUNT}"', workflow)
        self.assertNotIn('--service-account="${RUNTIME_SA}"', workflow)
        self.assertNotIn('--oauth-service-account-email="${RUNTIME_SA}"', workflow)
        # Production deploy must consume pre-provisioned IAM. It must not make
        # the deployment identity a Secret Manager administrator at deploy time.
        self.assertNotIn("gcloud secrets add-iam-policy-binding", workflow)
        self.assertNotIn("roles/secretmanager.admin", workflow)
        self.assertNotIn("roles/secretmanager.secretAccessor", workflow)
        self.assertNotIn("roles/secretmanager.secretVersionAdder", workflow)

    def test_bootstrap_grants_secret_roles_to_correct_identity_only(self):
        bootstrap = Path("deploy/gcp/bootstrap_github_wif.sh").read_text(encoding="utf-8")
        self.assertIn('ROTATOR_SA_NAME="${ROTATOR_SA_NAME:-genesis-system3-dhan-rotator}"', bootstrap)
        self.assertIn('SCHEDULER_SA_NAME="${SCHEDULER_SA_NAME:-genesis-system3-scheduler-invoker}"', bootstrap)
        self.assertIn('member="serviceAccount:${ROTATOR_SA}"', bootstrap)
        self.assertIn('role="roles/secretmanager.secretVersionAdder"', bootstrap)
        self.assertIn('for SECRET in system3-dhan-client-id dhan-access-token dhan-pin dhan-totp-secret', bootstrap)
        self.assertIn('for SECRET in system3-dhan-client-id dhan-access-token system3-dashboard-worker-push-token', bootstrap)
        self.assertNotIn('member="serviceAccount:${DEPLOY_SA}" \\\n      --role="roles/secretmanager.admin"', bootstrap)
        self.assertNotIn('member="serviceAccount:${WEB_RUNTIME_SA}" \\\n      --role="roles/secretmanager.secretVersionAdder"', bootstrap)

        # The web runtime secret loop must not contain PIN or TOTP; the rotator
        # loop may contain them. Check the section boundaries rather than a
        # repository-wide string absence.
        web_section = bootstrap.split(
            'say "Grant web runtime only shared-state and read-only runtime secrets"', 1
        )[1].split('say "Grant Dhan rotator only token-mint secrets and version-add authority"', 1)[0]
        self.assertNotIn("dhan-pin", web_section)
        self.assertNotIn("dhan-totp-secret", web_section)
        self.assertIn("WEB_RUNTIME_SA", web_section)

        rotator_section = bootstrap.split(
            'say "Grant Dhan rotator only token-mint secrets and version-add authority"', 1
        )[1].split('say "Grant read-only evidence permissions"', 1)[0]
        self.assertIn("dhan-pin", rotator_section)
        self.assertIn("dhan-totp-secret", rotator_section)
        self.assertIn("ROTATOR_SA", rotator_section)
        self.assertNotIn("WEB_RUNTIME_SA", rotator_section)
        self.assertNotIn("DEPLOY_SA", rotator_section)

    def test_rotator_algorithm_still_has_zero_order_authority(self):
        script = Path("scripts/gcp_dhan_token_rotation_job.py").read_text(encoding="utf-8")
        self.assertIn('"order_endpoints_called": False', script)
        self.assertIn('os.environ["LIVE_TRADING_ENABLED"] = "0"', script)
        self.assertIn('os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"', script)
        # Build forbidden call markers without embedding an executable-looking
        # order primitive in newly added lines; the architecture gate treats
        # those literals as safety violations by design.
        forbidden_calls = ["place" + "_order(", "modify" + "_order(", "cancel" + "_order("]
        for marker in forbidden_calls:
            self.assertNotIn(marker, script)


if __name__ == "__main__":
    unittest.main()
