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
    def test_secret_manager_ref_is_mounted_not_plaintext(self):
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
        # The leaked value itself must never be captured into the report.
        self.assertNotIn("not-a-secret-ref", str(env) + str(secret_refs) + str(plaintext))


class SafetySemanticsTests(unittest.TestCase):
    def _secure_env(self) -> dict:
        return {
            "ANALYZE_MODE": "true",
            "LIVE_TRADING_ENABLED": "0",
            "SYSTEM3_LIVE_TRADING_ALLOWED": "0",
            "AUTO_EXECUTE_TRADES": "0",
            "REQUIRE_API_KEY": "true",
        }

    def test_secure_state_requires_auth_enabled_and_mounted(self):
        safety = evidence.evaluate_safety(self._secure_env(), ["API_KEY"], [])
        self.assertTrue(safety["api_key_required"])
        self.assertTrue(safety["api_key_mounted"])
        self.assertFalse(safety["api_key_plaintext_exposed"])
        self.assertTrue(evidence.safety_passes(safety))
        self.assertEqual(evidence.safety_blockers(safety), [])

    def test_disabled_auth_fails_and_reports_missing_auth_blocker(self):
        env = self._secure_env(); env["REQUIRE_API_KEY"] = "false"
        safety = evidence.evaluate_safety(env, ["API_KEY"], [])
        self.assertFalse(safety["api_key_required"])
        self.assertFalse(evidence.safety_passes(safety))
        blockers = evidence.safety_blockers(safety)
        self.assertTrue(any("missing or disabled" in b for b in blockers))
        self.assertFalse(any("enabled" in b and "missing" not in b for b in blockers))

    def test_unmounted_secret_fails_and_reports_not_mounted_blocker(self):
        safety = evidence.evaluate_safety(self._secure_env(), [], [])
        self.assertFalse(safety["api_key_mounted"])
        self.assertFalse(evidence.safety_passes(safety))
        self.assertTrue(any("not mounted from Secret Manager" in b for b in evidence.safety_blockers(safety)))

    def test_plaintext_api_key_fails_even_when_required_flag_is_true(self):
        safety = evidence.evaluate_safety(self._secure_env(), [], ["API_KEY"])
        self.assertTrue(safety["api_key_plaintext_exposed"])
        self.assertFalse(evidence.safety_passes(safety))
        self.assertTrue(any("plaintext" in b for b in evidence.safety_blockers(safety)))

    def test_live_trading_flags_still_block_regardless_of_auth_posture(self):
        env = self._secure_env(); env["LIVE_TRADING_ENABLED"] = "true"
        safety = evidence.evaluate_safety(env, ["API_KEY"], [])
        self.assertFalse(evidence.safety_passes(safety))
        self.assertTrue(any("Live-trading-off" in b for b in evidence.safety_blockers(safety)))


if __name__ == "__main__":
    unittest.main()
