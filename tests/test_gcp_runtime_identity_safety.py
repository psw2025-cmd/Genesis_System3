from __future__ import annotations

import unittest
from pathlib import Path

from scripts.gcp_runtime_identity_safety import prove_runtime_safety, rotator_service_account

ROTATOR_SA = "genesis-system3-dhan-rotator@example.iam.gserviceaccount.com"
SCHEDULER_SA = "gs3-scheduler@example.iam.gserviceaccount.com"


def _service() -> dict:
    return {
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "env": [
                                {"name": "LIVE_TRADING_ENABLED", "value": "0"},
                                {"name": "SYSTEM3_LIVE_TRADING_ALLOWED", "value": "0"},
                                {"name": "AUTO_EXECUTE_TRADES", "value": "0"},
                                {"name": "DHAN_TOKEN_SOURCE", "value": "gcp-secret-manager-dynamic"},
                                {"name": "DEFER_INSTRUMENT_WARMUP", "value": "1"},
                                {"name": "REQUIRE_API_KEY", "value": "false"},
                                {
                                    "name": "WORKER_PUSH_TOKEN",
                                    "valueFrom": {"secretKeyRef": {"name": "worker", "key": "latest"}},
                                },
                            ]
                        }
                    ]
                }
            }
        },
        "status": {"traffic": [{"revisionName": "rev-1", "percent": 100}]},
    }


def _scheduler() -> dict:
    return {
        "schedule": "*/5 * * * *",
        "timeZone": "Asia/Kolkata",
        "httpTarget": {"oauthToken": {"serviceAccountEmail": SCHEDULER_SA}},
    }


class RotatorSchemaTests(unittest.TestCase):
    def test_accepts_gcloud_v1_job_shape_seen_in_runtime_evidence(self):
        job = {
            "spec": {
                "template": {
                    "spec": {
                        "template": {"spec": {"serviceAccountName": ROTATOR_SA}}
                    }
                }
            }
        }
        self.assertEqual(rotator_service_account(job), ROTATOR_SA)

    def test_accepts_v2_task_template_shape(self):
        job = {"template": {"template": {"serviceAccount": ROTATOR_SA}}}
        self.assertEqual(rotator_service_account(job), ROTATOR_SA)

    def test_missing_identity_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "rotator_service_account_unresolved"):
            rotator_service_account({"spec": {"template": {}}})

    def test_ambiguous_identity_fails_closed(self):
        job = {
            "template": {"template": {"serviceAccount": ROTATOR_SA}},
            "spec": {
                "template": {
                    "spec": {
                        "template": {"spec": {"serviceAccountName": "other@example.iam.gserviceaccount.com"}}
                    }
                }
            },
        }
        with self.assertRaisesRegex(ValueError, "rotator_service_account_unresolved"):
            rotator_service_account(job)


class RuntimeSafetyTests(unittest.TestCase):
    def _v1_job(self, service_account: str = ROTATOR_SA) -> dict:
        return {
            "spec": {
                "template": {
                    "spec": {
                        "template": {"spec": {"serviceAccountName": service_account}}
                    }
                }
            }
        }

    def test_exact_safe_contract_passes(self):
        result = prove_runtime_safety(
            _service(),
            self._v1_job(),
            _scheduler(),
            expected_rotator_service_account=ROTATOR_SA,
            expected_scheduler_service_account=SCHEDULER_SA,
        )
        self.assertEqual(result["state"], "PASS")
        self.assertFalse(result["live_trading_enabled"])
        self.assertFalse(result["secret_values_exposed"])

    def test_wrong_rotator_identity_fails(self):
        with self.assertRaisesRegex(ValueError, "rotator_identity_mismatch"):
            prove_runtime_safety(
                _service(),
                self._v1_job("wrong@example.iam.gserviceaccount.com"),
                _scheduler(),
                expected_rotator_service_account=ROTATOR_SA,
                expected_scheduler_service_account=SCHEDULER_SA,
            )

    def test_wrong_scheduler_identity_fails(self):
        scheduler = _scheduler()
        scheduler["httpTarget"]["oauthToken"]["serviceAccountEmail"] = "wrong@example.iam.gserviceaccount.com"
        with self.assertRaisesRegex(ValueError, "scheduler_identity_mismatch"):
            prove_runtime_safety(
                _service(),
                self._v1_job(),
                scheduler,
                expected_rotator_service_account=ROTATOR_SA,
                expected_scheduler_service_account=SCHEDULER_SA,
            )

    def test_hourly_rotator_schedule_fails_closed(self):
        scheduler = _scheduler()
        scheduler["schedule"] = "30 * * * *"
        with self.assertRaisesRegex(ValueError, "scheduler_config_invalid"):
            prove_runtime_safety(
                _service(),
                self._v1_job(),
                scheduler,
                expected_rotator_service_account=ROTATOR_SA,
                expected_scheduler_service_account=SCHEDULER_SA,
            )

    def test_live_flag_fails_closed(self):
        service = _service()
        service["spec"]["template"]["spec"]["containers"][0]["env"][0]["value"] = "1"
        with self.assertRaisesRegex(ValueError, "live_flags_not_off"):
            prove_runtime_safety(
                service,
                self._v1_job(),
                _scheduler(),
                expected_rotator_service_account=ROTATOR_SA,
                expected_scheduler_service_account=SCHEDULER_SA,
            )


class DeployWorkflowSafetyTests(unittest.TestCase):
    def test_deploy_configures_business_jobs_but_never_executes_business_evidence(self):
        workflow = Path(".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
        self.assertIn('for KIND in rank forecast validate signals; do', workflow)
        self.assertIn('gcloud run jobs deploy "genesis-system3-${KIND}"', workflow)
        self.assertIn('gcloud run jobs execute genesis-system3-scheduler-collector', workflow)
        self.assertIn('gcloud run jobs execute genesis-system3-control-plane-verify', workflow)
        self.assertNotIn('for LANE in rank forecast validate signals; do', workflow)
        for lane in ("rank", "forecast", "validate", "signals"):
            self.assertNotIn(f'gcloud run jobs execute "genesis-system3-{lane}"', workflow)
            self.assertNotIn(f'gcloud run jobs execute genesis-system3-{lane}', workflow)
        self.assertNotIn("Cloud self-bootstrap", workflow)
        self.assertNotIn("gcloud run jobs execute genesis-system3-ml-history-bootstrap", workflow)


if __name__ == "__main__":
    unittest.main()
