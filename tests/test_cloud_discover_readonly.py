"""Offline safety and ambiguity checks for read-only GCP discovery."""
import unittest
from scripts.cloud_discover_readonly import discover, service_name, select_production_target


def service(name, env):
    return {"metadata": {"name": name}, "spec": {"template": {"spec": {"containers": [{"env": [
        {"name": key, "value": value} for key, value in env.items()
    ]}]}}}}


SAFE = {"PAPER_MODE": "1", "LIVE_ORDER_AUTHORITY": "0", "REAL_BROKER_ORDERS": "0"}


class DiscoveryTests(unittest.TestCase):
    def test_actual_identity_comes_from_service_inventory(self):
        projects = [{"projectId": "real-project"}]
        result = discover(projects, {"real-project": [service("real-genesis-service", SAFE)]})
        self.assertEqual(result, [("real-project", "real-genesis-service")])

    def test_wrong_safety_not_selected(self):
        bad = {**SAFE, "LIVE_ORDER_AUTHORITY": "1"}
        self.assertEqual(discover([{"projectId": "p"}], {"p": [service("genesis", bad)]}), [])

    def test_ambiguous_candidates_not_silently_chosen(self):
        projects = [{"projectId": "p"}]
        result = discover(projects, {"p": [service("genesis", SAFE), service("genesis-system3-web", SAFE)]})
        self.assertEqual(len(result), 2)

    def test_known_production_wins_over_multiple_safe_services(self):
        project = "system3-openalgo-safe"
        services = [
            service("genesis-system3", SAFE),
            service("genesis-system3-web-staging", SAFE),
            service("genesis-system3-web", SAFE),
        ]
        matches = discover([{"projectId": project}], {project: services})
        self.assertEqual(
            select_production_target(matches),
            ("system3-openalgo-safe", "genesis-system3-web"),
        )

    def test_unknown_or_missing_canonical_fails_closed(self):
        self.assertIsNone(
            select_production_target([("other-project", "genesis-system3-web")])
        )
        self.assertIsNone(
            select_production_target([("system3-openalgo-safe", "genesis-system3-web-staging")])
        )
        self.assertIsNone(select_production_target([]))

    def test_canonical_safety_mismatch_cannot_be_bypassed(self):
        project = "system3-openalgo-safe"
        unsafe = {**SAFE, "LIVE_ORDER_AUTHORITY": "1"}
        matches = discover([{"projectId": project}], {project: [
            service("genesis-system3-web", unsafe),
            service("genesis-system3", SAFE),
        ]})
        self.assertIsNone(select_production_target(matches))

    def test_other_services_not_selected(self):
        self.assertEqual(discover([{"projectId": "p"}], {"p": [service("other-app", SAFE)]}), [])


if __name__ == "__main__":
    unittest.main()
