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
    def test_all_anonymous_mutations_fail_closed(self):
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
                self.assertEqual(decision.status_code, 503)
                self.assertEqual(
                    decision.code,
                    "AUTH_REQUIRED_FOR_MUTATION",
                )

    def test_public_analyzer_mode_allows_read_only_route(self):
        decision = evaluate_request(
            method="GET",
            path="/api/state",
            require_api_key=False,
            api_key_configured=False,
            dashboard_access=False,
        )
        self.assertTrue(decision.allowed)

    def test_auth_enabled_rejects_anonymous_read(self):
        decision = evaluate_request(
            method="GET",
            path="/api/state",
            require_api_key=True,
            api_key_configured=True,
            dashboard_access=False,
        )
        self.assertEqual(decision.status_code, 401)
        self.assertEqual(decision.code, "AUTH_INVALID")

    def test_worker_push_requires_configured_token(self):
        decision = evaluate_request(
            method="POST",
            path="/api/chain/push",
            require_api_key=False,
            api_key_configured=False,
            dashboard_access=False,
        )
        self.assertEqual(decision.status_code, 503)
        self.assertEqual(
            decision.code,
            "WORKER_AUTH_NOT_CONFIGURED",
        )

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

    def test_cookie_mutation_requires_allowed_origin(self):
        decision = evaluate_request(
            method="POST",
            path="/api/runner/start",
            require_api_key=True,
            api_key_configured=True,
            dashboard_access=True,
            origin="https://evil.example",
            same_origin="https://system3.example",
            allowed_origins={"https://system3.example"},
        )
        self.assertEqual(decision.status_code, 403)
        self.assertEqual(
            decision.code,
            "CSRF_ORIGIN_REJECTED",
        )

    def test_order_requires_idempotency_key(self):
        decision = evaluate_request(
            method="POST",
            path="/api/orders/create",
            require_api_key=True,
            api_key_configured=True,
            dashboard_access=True,
            header_api_key_present=True,
        )
        self.assertEqual(decision.status_code, 428)
        self.assertEqual(
            decision.code,
            "IDEMPOTENCY_KEY_REQUIRED",
        )

    def test_authenticated_idempotent_order_reaches_inner_gates(self):
        decision = evaluate_request(
            method="POST",
            path="/api/orders/create",
            require_api_key=True,
            api_key_configured=True,
            dashboard_access=True,
            header_api_key_present=True,
            idempotency_key_present=True,
        )
        self.assertTrue(decision.allowed)

    def test_cors_and_agent_exemption_removed(self):
        source = Path(
            "dashboard/backend/app.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('allow_origins=["*"]', source)
        self.assertIn(
            "allow_origins=_allowed_origins",
            source,
        )
        self.assertNotIn(
            '"/agent-full-control",',
            source,
        )


if __name__ == "__main__":
    unittest.main()
