import unittest

from dashboard.backend.mutation_policy import (
    Capability,
    WRITE_METHODS,
    classify_mutation,
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

    def test_live_order_paths_are_never_classified_as_non_live(self):
        for path in (
            "/api/orders/create",
            "/api/orders/ABC/cancel",
            "/api/live-trading/execute",
            "/place-order",
        ):
            self.assertEqual(classify_mutation("POST", path), Capability.LIVE_MUTATION)

    def test_runtime_hard_denies_live_mutation(self):
        for path in ("/api/orders/create", "/api/live-trading/execute", "/place-order"):
            decision = evaluate_runtime_mutation("POST", path)
            self.assertIsNotNone(decision)
            self.assertFalse(decision.allowed)
            self.assertEqual(decision.state, "LIVE_LOCKED")
            self.assertEqual(decision.http_status, 423)

    def test_runtime_hard_denies_live_approval(self):
        decision = evaluate_runtime_mutation("POST", "/api/live-trading/approve")
        self.assertIsNotNone(decision)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.capability, Capability.LIVE_APPROVAL)
        self.assertEqual(decision.state, "LIVE_LOCKED")

    def test_runtime_denies_unclassified_write(self):
        decision = evaluate_runtime_mutation("POST", "/api/not-approved/new-write")
        self.assertIsNotNone(decision)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.capability, Capability.UNKNOWN)
        self.assertEqual(decision.state, "DENY_UNKNOWN")

    def test_paper_close_is_separate_and_not_live_locked(self):
        self.assertEqual(
            classify_mutation("POST", "/api/positions/PAPER-1/close"),
            Capability.PAPER_MUTATION,
        )
        decision = evaluate_runtime_mutation("POST", "/api/positions/PAPER-1/close")
        self.assertIsNotNone(decision)
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.capability, Capability.PAPER_MUTATION)

    def test_reads_have_no_mutation_capability(self):
        for method in ("GET", "HEAD", "OPTIONS"):
            self.assertNotIn(method, WRITE_METHODS)
            self.assertIsNone(classify_mutation(method, "/api/orders/create"))
            self.assertIsNone(evaluate_runtime_mutation(method, "/api/orders/create"))


if __name__ == "__main__":
    unittest.main()
