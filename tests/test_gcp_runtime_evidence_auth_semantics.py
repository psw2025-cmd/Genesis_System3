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


def _service(env_rows: list[dict]) -> dict:
    return {"spec": {"template": {"spec": {"containers": [{"env": env_rows}]}}}}


class SafeEnvSecretSourceTests(unittest.TestCase):
    def test_secret_manager_ref_is_detected_without_exposing_value(self):
        service = _service([
            {"name": "API_KEY", "valueFrom": {"secretKeyRef": {"name": "system3-dashboard-api-key", "key": "latest"}}},
        ])
        env, secret_refs, plaintext = evidence.safe_env(service)
        self.assertIn("API_KEY", secret_refs)
        self.assertNotIn("API_KEY", plaintext)
        self.assertNotIn("API_KEY", env)

    def test_plain_value_is_flagged_as_plaintext_leak(self):
        service = _service([{"name": "API_KEY", "value": "not-a-secret-ref"}])
        env, secret_refs, plaintext = evidence.safe_env(service)
        self.assertNotIn("API_KEY", secret_refs)
        self.assertIn("API_KEY", plaintext)
        self.assertNotIn("not-a-secret-ref", str(env) + str(secret_refs) + str(plaintext))


class SafetySemanticsTests(unittest.TestCase):
    def _public_paper_env(self) -> dict:
        return {
            "ANALYZE_MODE": "true",
            "LIVE_TRADING_ENABLED": "0",
            "SYSTEM3_LIVE_TRADING_ALLOWED": "0",
            "AUTO_EXECUTE_TRADES": "0",
            "REQUIRE_API_KEY": "false",
        }

    def test_expected_state_is_public_readonly_without_dashboard_key(self):
        safety = evidence.evaluate_safety(self._public_paper_env(), [], [])
        self.assertFalse(safety["api_key_required"])
        self.assertFalse(safety["api_key_mounted"])
        self.assertFalse(safety["api_key_plaintext_exposed"])
        self.assertTrue(safety["dashboard_public_readonly"])
        self.assertTrue(evidence.safety_passes(safety))
        self.assertEqual(evidence.safety_blockers(safety), [])

    def test_reenabling_dashboard_key_requirement_is_a_contract_violation(self):
        env = self._public_paper_env(); env["REQUIRE_API_KEY"] = "true"
        safety = evidence.evaluate_safety(env, [], [])
        self.assertTrue(safety["api_key_required"])
        self.assertFalse(safety["dashboard_public_readonly"])
        self.assertFalse(evidence.safety_passes(safety))
        self.assertTrue(any("re-enabled" in b for b in evidence.safety_blockers(safety)))

    def test_mounting_dashboard_api_key_is_a_contract_violation(self):
        safety = evidence.evaluate_safety(self._public_paper_env(), ["API_KEY"], [])
        self.assertTrue(safety["api_key_mounted"])
        self.assertFalse(safety["dashboard_public_readonly"])
        self.assertFalse(evidence.safety_passes(safety))
        self.assertTrue(any("unexpectedly mounted" in b for b in evidence.safety_blockers(safety)))

    def test_plaintext_api_key_always_fails(self):
        safety = evidence.evaluate_safety(self._public_paper_env(), [], ["API_KEY"])
        self.assertTrue(safety["api_key_plaintext_exposed"])
        self.assertFalse(safety["dashboard_public_readonly"])
        self.assertFalse(evidence.safety_passes(safety))
        self.assertTrue(any("plaintext" in b for b in evidence.safety_blockers(safety)))

    def test_live_trading_flags_still_block_regardless_of_dashboard_auth_posture(self):
        env = self._public_paper_env(); env["LIVE_TRADING_ENABLED"] = "true"
        safety = evidence.evaluate_safety(env, [], [])
        self.assertFalse(evidence.safety_passes(safety))
        self.assertTrue(any("Live-trading-off" in b for b in evidence.safety_blockers(safety)))


if __name__ == "__main__":
    unittest.main()
