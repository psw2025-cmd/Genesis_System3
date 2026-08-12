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
    def test_all_dashboard_mutations_fail_closed(self):
        for method, path in RISKY_MUTATIONS:
            with self.subTest(method=method, path=path):
                decision = evaluate_request(
                    method=method,
                    path=path,
                    require_api_key=False,
                    api_key_configured=False,
                    dashboard_access=False,
                )
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.status_code, 403)
                self.assertEqual(decision.code, "PUBLIC_DASHBOARD_READ_ONLY")

    def test_safe_read_is_public_even_if_legacy_auth_flags_drift_on(self):
        decision = evaluate_request(
            method="GET",
            path="/api/state",
            require_api_key=True,
            api_key_configured=True,
            dashboard_access=False,
        )
        self.assertTrue(decision.allowed)

    def test_retired_login_and_logout_paths_fail_closed(self):
        for method, path in (("POST", "/api/auth/session"), ("POST", "/api/auth/logout")):
            with self.subTest(method=method, path=path):
                decision = evaluate_request(
                    method=method,
                    path=path,
                    require_api_key=True,
                    api_key_configured=True,
                    dashboard_access=True,
                    header_api_key_present=True,
                )
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.status_code, 404)
                self.assertEqual(decision.code, "DASHBOARD_AUTH_RETIRED")

    def test_worker_push_requires_configured_token(self):
        decision = evaluate_request(
            method="POST",
            path="/api/chain/push",
            require_api_key=False,
            api_key_configured=False,
            dashboard_access=False,
        )
        self.assertEqual(decision.status_code, 503)
        self.assertEqual(decision.code, "WORKER_AUTH_NOT_CONFIGURED")

    def test_worker_push_rejects_invalid_token(self):
        decision = evaluate_request(
            method="POST",
            path="/api/chain/push",
            require_api_key=False,
            api_key_configured=False,
            dashboard_access=False,
            worker_token_configured=True,
            worker_token_valid=False,
        )
        self.assertEqual(decision.status_code, 401)
        self.assertEqual(decision.code, "WORKER_AUTH_INVALID")

    def test_worker_push_accepts_only_valid_dedicated_worker_token(self):
        decision = evaluate_request(
            method="POST",
            path="/api/chain/push",
            require_api_key=True,
            api_key_configured=True,
            dashboard_access=True,
            worker_token_configured=True,
            worker_token_valid=True,
            header_api_key_present=True,
        )
        self.assertTrue(decision.allowed)

    def test_legacy_dashboard_credentials_cannot_restore_order_authority(self):
        decision = evaluate_request(
            method="POST",
            path="/api/orders/create",
            require_api_key=True,
            api_key_configured=True,
            dashboard_access=True,
            header_api_key_present=True,
            origin="https://system3.example",
            same_origin="https://system3.example",
            idempotency_key_present=True,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.status_code, 403)
        self.assertEqual(decision.code, "PUBLIC_DASHBOARD_READ_ONLY")

    def test_cors_and_agent_exemption_removed(self):
        source = Path("dashboard/backend/app.py").read_text(encoding="utf-8")
        self.assertNotIn('allow_origins=["*"]', source)
        self.assertIn("allow_origins=_allowed_origins", source)
        self.assertNotIn('"/agent-full-control",', source)


if __name__ == "__main__":
    unittest.main()
