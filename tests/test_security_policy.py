import unittest
from pathlib import Path

from dashboard.backend.security_policy import evaluate_request


RISKY_MUTATIONS = [
    ("DELETE", "/order/example"),
    ("POST", "/agent-full-control"),
    ("POST", "/api/agent/apply-upgrade"),
    ("POST", "/api/agent/rollback"),
    ("POST", "/api/forensic/run"),
    ("POST", "/api/live-trading/approve"),
    ("POST", "/api/orders/create"),
    ("POST", "/api/orders/example/cancel"),
    ("POST", "/api/positions/example/close"),
    ("POST", "/api/runner/start"),
    ("POST", "/api/runner/stop"),
    ("POST", "/emergency-exit"),
    ("POST", "/place-order"),
]


class SecurityPolicyTests(unittest.TestCase):
    def test_all_public_dashboard_mutations_fail_closed(self):
        for method, path in RISKY_MUTATIONS:
            with self.subTest(method=method, path=path):
                decision = evaluate_request(method=method, path=path)
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.status_code, 403)
                self.assertEqual(decision.code, "PUBLIC_DASHBOARD_READ_ONLY")

    def test_public_analyzer_reads_are_allowed(self):
        for path in ("/api/state", "/api/broker/status", "/api/health", "/ui"):
            with self.subTest(path=path):
                decision = evaluate_request(method="GET", path=path)
                self.assertTrue(decision.allowed)

    def test_obsolete_dashboard_credential_fields_cannot_change_read_or_write_decision(self):
        # Compatibility kwargs from the large legacy middleware are accepted but
        # ignored. They cannot reactivate browser credential authority.
        read = evaluate_request(
            method="GET",
            path="/api/state",
            require_api_key=True,
            api_key_configured=True,
            dashboard_access=True,
            header_api_key_present=True,
        )
        self.assertTrue(read.allowed)

        write = evaluate_request(
            method="POST",
            path="/api/runner/start",
            require_api_key=True,
            api_key_configured=True,
            dashboard_access=True,
            header_api_key_present=True,
            idempotency_key_present=True,
        )
        self.assertFalse(write.allowed)
        self.assertEqual(write.code, "PUBLIC_DASHBOARD_READ_ONLY")

    def test_worker_push_requires_configured_token(self):
        decision = evaluate_request(method="POST", path="/api/chain/push")
        self.assertEqual(decision.status_code, 503)
        self.assertEqual(decision.code, "WORKER_AUTH_NOT_CONFIGURED")

    def test_worker_push_rejects_invalid_token(self):
        decision = evaluate_request(
            method="POST",
            path="/api/chain/push",
            worker_token_configured=True,
            worker_token_valid=False,
        )
        self.assertEqual(decision.status_code, 401)
        self.assertEqual(decision.code, "WORKER_AUTH_INVALID")

    def test_worker_push_accepts_only_dedicated_valid_worker_authority(self):
        decision = evaluate_request(
            method="POST",
            path="/api/chain/push",
            worker_token_configured=True,
            worker_token_valid=True,
        )
        self.assertTrue(decision.allowed)

    def test_cors_and_agent_exemption_remain_restricted(self):
        source = Path("dashboard/backend/app.py").read_text(encoding="utf-8")
        self.assertNotIn('allow_origins=["*"]', source)
        self.assertIn("allow_origins=_allowed_origins", source)
        self.assertNotIn('"/agent-full-control",', source)


if __name__ == "__main__":
    unittest.main()
