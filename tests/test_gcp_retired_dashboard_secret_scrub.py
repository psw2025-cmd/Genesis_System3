from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPTS = Path("scripts").resolve()
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

_SPEC = importlib.util.spec_from_file_location(
    "system3_cloud_run_deploy_wrapper_test", SCRIPTS / "gcp_cloud_run_auto_deploy.py"
)
assert _SPEC and _SPEC.loader
wrapper = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(wrapper)


class RetiredDashboardSecretScrubTests(unittest.TestCase):
    def test_candidate_deploy_adds_retired_dashboard_secret_to_remove_list(self):
        args = [
            "gcloud", "run", "deploy", "genesis-system3-web",
            "--remove-secrets=API_KEY,DHAN_PIN,DHAN_TOTP_SECRET,DHAN_TOTP",
            "--update-secrets=WORKER_PUSH_TOKEN=worker-secret:latest",
        ]
        scrubbed = wrapper._scrub_retired_dashboard_secret_arg(args)
        remove_arg = next(x for x in scrubbed if x.startswith("--remove-secrets="))
        names = remove_arg.split("=", 1)[1].split(",")
        self.assertIn("API_KEY", names)
        self.assertIn("DASHBOARD_API_KEY", names)
        self.assertIn("DHAN_PIN", names)
        self.assertIn("DHAN_TOTP_SECRET", names)
        self.assertIn("DHAN_TOTP", names)
        self.assertEqual(names.count("DASHBOARD_API_KEY"), 1)

    def test_scrub_is_idempotent(self):
        args = [
            "gcloud", "run", "deploy", "genesis-system3-web",
            "--remove-secrets=API_KEY,DASHBOARD_API_KEY",
        ]
        once = wrapper._scrub_retired_dashboard_secret_arg(args)
        twice = wrapper._scrub_retired_dashboard_secret_arg(once)
        self.assertEqual(once, twice)

    def test_non_deploy_command_is_unchanged(self):
        args = ["gcloud", "run", "services", "describe", "genesis-system3-web"]
        self.assertEqual(args, wrapper._scrub_retired_dashboard_secret_arg(args))

    def test_missing_remove_secrets_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "candidate_remove_secrets_contract_invalid"):
            wrapper._scrub_retired_dashboard_secret_arg(
                ["gcloud", "run", "deploy", "genesis-system3-web"]
            )

    def test_missing_api_key_scrub_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "candidate_api_key_scrub_missing"):
            wrapper._scrub_retired_dashboard_secret_arg(
                [
                    "gcloud", "run", "deploy", "genesis-system3-web",
                    "--remove-secrets=DHAN_PIN,DHAN_TOTP_SECRET,DHAN_TOTP",
                ]
            )


if __name__ == "__main__":
    unittest.main()
