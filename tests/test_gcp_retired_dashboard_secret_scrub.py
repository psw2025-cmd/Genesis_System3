from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

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


class BusinessSchedulerContractTests(unittest.TestCase):
    def _assert_common_contract(self, command: list[str], kind: str, action: str) -> None:
        self.assertEqual(
            command[:5],
            ["gcloud", "scheduler", "jobs", action, "http"],
        )
        self.assertEqual(command[5], f"genesis-system3-{kind}-daily")
        self.assertIn(f"--project={wrapper.PROJECT}", command)
        self.assertIn(f"--location={wrapper.REGION}", command)
        self.assertIn(
            "--uri=https://run.googleapis.com/v2/projects/"
            f"{wrapper.PROJECT}/locations/{wrapper.REGION}/jobs/genesis-system3-{kind}:run",
            command,
        )
        self.assertIn("--http-method=POST", command)
        self.assertIn(
            f"--oauth-service-account-email={wrapper.SCHEDULER_SA}",
            command,
        )
        self.assertIn(
            "--oauth-token-scope=https://www.googleapis.com/auth/cloud-platform",
            command,
        )
        self.assertIn("--message-body={}", command)
        self.assertNotIn("execute", command)
        self.assertNotIn("run", command[:5])

    def test_missing_business_schedulers_are_created_without_execution(self):
        with mock.patch.object(wrapper, "_scheduler_exists", return_value=False), mock.patch.object(
            wrapper, "_ORIGINAL_RUN"
        ) as run:
            wrapper._ensure_business_scheduler_contract()

        self.assertEqual(run.call_count, 3)
        for kind, call in zip(wrapper.BUSINESS_SCHEDULES, run.call_args_list):
            command = call.args[0]
            self._assert_common_contract(command, kind, "create")
            self.assertIn("--headers=Content-Type=application/json", command)
            self.assertNotIn("--update-headers=Content-Type=application/json", command)
            self.assertIn(f"--schedule={wrapper.BUSINESS_SCHEDULES[kind]}", command)

    def test_existing_business_schedulers_are_fully_reconciled(self):
        with mock.patch.object(wrapper, "_scheduler_exists", return_value=True), mock.patch.object(
            wrapper, "_ORIGINAL_RUN"
        ) as run:
            wrapper._ensure_business_scheduler_contract()

        self.assertEqual(run.call_count, 3)
        for kind, call in zip(wrapper.BUSINESS_SCHEDULES, run.call_args_list):
            command = call.args[0]
            self._assert_common_contract(command, kind, "update")
            self.assertIn("--update-headers=Content-Type=application/json", command)
            self.assertNotIn("--headers=Content-Type=application/json", command)

    def test_scheduler_not_found_is_the_only_describe_error_treated_as_missing(self):
        missing = SimpleNamespace(
            returncode=1,
            stdout="",
            stderr="ERROR: (gcloud.scheduler.jobs.describe) NOT_FOUND: Job does not exist",
        )
        with mock.patch.object(wrapper.subprocess, "run", return_value=missing):
            self.assertFalse(wrapper._scheduler_exists("genesis-system3-rank-daily"))

        denied = SimpleNamespace(
            returncode=1,
            stdout="",
            stderr="ERROR: PERMISSION_DENIED: caller lacks cloudscheduler.jobs.get",
        )
        with mock.patch.object(wrapper.subprocess, "run", return_value=denied):
            with self.assertRaisesRegex(RuntimeError, "business_scheduler_describe_failed"):
                wrapper._scheduler_exists("genesis-system3-rank-daily")

    def test_scheduler_exists_uses_exact_project_region_and_no_mutation(self):
        ok = SimpleNamespace(returncode=0, stdout="name", stderr="")
        with mock.patch.object(wrapper.subprocess, "run", return_value=ok) as run:
            self.assertTrue(wrapper._scheduler_exists("genesis-system3-signals-daily"))

        command = run.call_args.args[0]
        self.assertEqual(
            command[:5],
            ["gcloud", "scheduler", "jobs", "describe", "genesis-system3-signals-daily"],
        )
        self.assertIn(f"--project={wrapper.PROJECT}", command)
        self.assertIn(f"--location={wrapper.REGION}", command)
        self.assertNotIn("create", command)
        self.assertNotIn("update", command)


if __name__ == "__main__":
    unittest.main()