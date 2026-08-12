from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "system3_gcp_runtime_evidence_test", Path("scripts/gcp_runtime_evidence.py")
)
assert _SPEC and _SPEC.loader
evidence = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(evidence)


def _resource(env_rows: list[dict]) -> dict:
    return {"spec": {"containers": [{"env": env_rows}]}}


class SafeEnvSecretSourceTests(unittest.TestCase):
    def test_retired_secret_manager_ref_is_detected_without_exposing_value(self):
        resource = _resource([
            {
                "name": "DASHBOARD_API_KEY",
                "valueFrom": {"secretKeyRef": {"name": "obsolete-secret", "key": "latest"}},
            },
        ])
        env, secret_refs, plaintext, names = evidence.safe_env(resource)
        self.assertIn("DASHBOARD_API_KEY", secret_refs)
        self.assertIn("DASHBOARD_API_KEY", names)
        self.assertNotIn("DASHBOARD_API_KEY", plaintext)
        self.assertNotIn("DASHBOARD_API_KEY", env)

    def test_retired_plain_value_is_flagged_without_capturing_value(self):
        resource = _resource([{"name": "API_KEY", "value": "dummy-sensitive"}])
        env, secret_refs, plaintext, names = evidence.safe_env(resource)
        self.assertNotIn("API_KEY", secret_refs)
        self.assertIn("API_KEY", plaintext)
        self.assertIn("API_KEY", names)
        self.assertNotIn("dummy-sensitive", str(env) + str(secret_refs) + str(plaintext) + str(names))


class SafetySemanticsTests(unittest.TestCase):
    def _public_paper_env(self) -> dict:
        return {
            "ANALYZE_MODE": "true",
            "LIVE_TRADING_ENABLED": "0",
            "SYSTEM3_LIVE_TRADING_ALLOWED": "0",
            "AUTO_EXECUTE_TRADES": "0",
        }

    def test_expected_state_requires_dashboard_credential_surface_absence(self):
        env = self._public_paper_env()
        safety = evidence.evaluate_safety(env, [], [], list(env))
        self.assertFalse(safety["api_key_required"])
        self.assertFalse(safety["api_key_mounted"])
        self.assertFalse(safety["api_key_plaintext_exposed"])
        self.assertTrue(safety["dashboard_credential_surface_absent"])
        self.assertTrue(safety["dashboard_public_readonly"])
        self.assertTrue(evidence.safety_passes(safety))
        self.assertEqual(evidence.safety_blockers(safety), [])

    def test_even_false_retired_requirement_variable_is_a_contract_violation(self):
        env = self._public_paper_env()
        env["REQUIRE_API_KEY"] = "false"
        safety = evidence.evaluate_safety(env, [], [], list(env))
        self.assertTrue(safety["api_key_required"])
        self.assertFalse(safety["dashboard_credential_surface_absent"])
        self.assertFalse(evidence.safety_passes(safety))

    def test_retired_dashboard_secret_mount_is_a_contract_violation(self):
        env = self._public_paper_env()
        safety = evidence.evaluate_safety(env, ["DASHBOARD_API_KEY"], [], list(env) + ["DASHBOARD_API_KEY"])
        self.assertTrue(safety["api_key_mounted"])
        self.assertFalse(safety["dashboard_public_readonly"])
        self.assertFalse(evidence.safety_passes(safety))
        self.assertTrue(any("secret mount" in b for b in evidence.safety_blockers(safety)))

    def test_retired_plaintext_dashboard_secret_always_fails(self):
        env = self._public_paper_env()
        safety = evidence.evaluate_safety(env, [], ["API_KEY"], list(env) + ["API_KEY"])
        self.assertTrue(safety["api_key_plaintext_exposed"])
        self.assertFalse(safety["dashboard_public_readonly"])
        self.assertFalse(evidence.safety_passes(safety))
        self.assertTrue(any("plaintext" in b for b in evidence.safety_blockers(safety)))

    def test_live_trading_flags_still_block_independently(self):
        env = self._public_paper_env()
        env["LIVE_TRADING_ENABLED"] = "true"
        safety = evidence.evaluate_safety(env, [], [], list(env))
        self.assertFalse(evidence.safety_passes(safety))
        self.assertTrue(any("Live-trading-off" in b for b in evidence.safety_blockers(safety)))


if __name__ == "__main__":
    unittest.main()
