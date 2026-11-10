import unittest

from dashboard.backend.mutation_policy import (
    Capability,
    WRITE_METHODS,
    assert_runtime_manifest,
    classify_mutation,
    duplicate_write_routes,
    evaluate_runtime_mutation,
    inventory_write_routes,
    unclassified_write_routes,
)
from dashboard.backend.secure_app import app


class MutationCapabilityManifestTests(unittest.TestCase):
    def test_every_write_route_is_classified(self):
        unknown = unclassified_write_routes(app)
        self.assertEqual(
            unknown,
            [],
            "Unclassified write routes: "
            + ", ".join(f"{row.method} {row.path}" for row in unknown),
        )

    def test_inventory_has_no_duplicate_method_path_owner(self):
        rows = inventory_write_routes(app)
        keys = [(row.method, row.path) for row in rows]
        self.assertEqual(len(keys), len(set(keys)), f"Duplicate write route owners: {keys}")
        self.assertEqual(duplicate_write_routes(app), [])
        assert_runtime_manifest(app)

    def test_live_order_paths_are_never_classified_as_non_live(self):
        for path in (
            "/api/orders/create",
            "/api/orders/ABC/cancel",
            "/api/live-trading/execute",
            "/place-order",
            "/api/security/mutation-policy/probe/live",
        ):
            self.assertEqual(classify_mutation("POST", path), Capability.LIVE_MUTATION)

    def test_paper_close_is_separate_from_live_mutation(self):
        self.assertEqual(
            classify_mutation("POST", "/api/positions/PAPER-1/close"),
            Capability.PAPER_MUTATION,
        )
        self.assertEqual(
            classify_mutation("POST", "/api/security/mutation-policy/probe/paper"),
            Capability.PAPER_MUTATION,
        )

    def test_reads_have_no_mutation_capability(self):
        for method in ("GET", "HEAD", "OPTIONS"):
            self.assertNotIn(method, WRITE_METHODS)
            self.assertIsNone(classify_mutation(method, "/api/orders/create"))
            self.assertIsNone(evaluate_runtime_mutation(method, "/api/state"))

    def test_unknown_write_is_hard_denied(self):
        decision = evaluate_runtime_mutation("POST", "/api/not-classified")
        self.assertIsNotNone(decision)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.capability, Capability.UNKNOWN)
        self.assertEqual(decision.status_code, 403)
        self.assertEqual(decision.code, "MUTATION_CAPABILITY_UNKNOWN")

    def test_live_mutation_and_approval_are_hard_denied(self):
        for path, capability, code in (
            ("/api/orders/create", Capability.LIVE_MUTATION, "LIVE_MUTATION_LOCKED"),
            ("/api/live-trading/approve", Capability.LIVE_APPROVAL, "LIVE_APPROVAL_LOCKED"),
        ):
            with self.subTest(path=path):
                decision = evaluate_runtime_mutation(
                    "POST",
                    path,
                    worker_token_configured=True,
                    worker_token_valid=True,
                    control_authorized=True,
                )
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.capability, capability)
                self.assertEqual(decision.status_code, 423)
                self.assertEqual(decision.code, code)

    def test_public_paper_control_mutation_requires_separate_authority(self):
        decision = evaluate_runtime_mutation("POST", "/api/paper/tick")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.capability, Capability.PAPER_MUTATION)
        self.assertEqual(decision.status_code, 403)
        self.assertEqual(decision.authority, "CONTROL_PLANE")
        self.assertEqual(decision.code, "PAPER_MUTATION_AUTHORITY_REQUIRED")

    def test_worker_ingest_uses_only_dedicated_worker_authority(self):
        missing = evaluate_runtime_mutation(
            "POST",
            "/api/security/mutation-policy/probe/worker",
            worker_token_configured=False,
        )
        self.assertFalse(missing.allowed)
        self.assertEqual(missing.status_code, 503)
        self.assertEqual(missing.code, "WORKER_AUTH_NOT_CONFIGURED")

        invalid = evaluate_runtime_mutation(
            "POST",
            "/api/security/mutation-policy/probe/worker",
            worker_token_configured=True,
            worker_token_valid=False,
        )
        self.assertFalse(invalid.allowed)
        self.assertEqual(invalid.status_code, 401)
        self.assertEqual(invalid.code, "WORKER_AUTH_INVALID")

        valid = evaluate_runtime_mutation(
            "POST",
            "/api/security/mutation-policy/probe/worker",
            worker_token_configured=True,
            worker_token_valid=True,
        )
        self.assertTrue(valid.allowed)
        self.assertEqual(valid.capability, Capability.WORKER_INGEST)
        self.assertEqual(valid.authority, "WORKER_TOKEN")

    def test_session_compatibility_routes_only_reach_downstream_policy(self):
        for path in ("/api/auth/session", "/api/auth/logout"):
            decision = evaluate_runtime_mutation("POST", path)
            self.assertTrue(decision.allowed)
            self.assertEqual(decision.state, "ALLOW_DOWNSTREAM")
            self.assertEqual(decision.authority, "SESSION_ROUTE")


if __name__ == "__main__":
    unittest.main()
