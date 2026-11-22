"""Deterministic regression checks for Genesis lazy-content browser acceptance.

This test exercises the actual smoke harness wait contract, not live market/UI proof.
"""
import unittest
from unittest.mock import patch
from scripts.frontend_local_runtime_smoke import _wait_tab


class FakeBrowser:
    def __init__(self, snapshots):
        self.snapshots = list(snapshots)
        self.calls = 0

    def snapshot(self, tab_id):
        assert tab_id == "genesis"
        result = self.snapshots[min(self.calls, len(self.snapshots) - 1)]
        self.calls += 1
        return result


def snapshot(*, loading, heading="Genesis", active=True):
    return {
        "rootChildren": 1,
        "system3": True,
        "active": active,
        "mainChars": 100,
        "mainHeading": heading,
        "loadingFallback": loading,
    }


class ColdCacheAcceptanceTests(unittest.TestCase):
    def test_suspense_fallback_is_not_accepted_as_rendered(self):
        browser = FakeBrowser([snapshot(loading=True)])
        with patch("scripts.frontend_local_runtime_smoke.time.monotonic", side_effect=[0, 0, 1]), patch(
            "scripts.frontend_local_runtime_smoke.time.sleep"
        ):
            result = _wait_tab(browser, "genesis", timeout_s=1)
        self.assertTrue(result["loadingFallback"])
        self.assertEqual(browser.calls, 1)

    def test_transition_from_fallback_to_rendered_is_accepted(self):
        browser = FakeBrowser([snapshot(loading=True), snapshot(loading=False)])
        with patch("scripts.frontend_local_runtime_smoke.time.monotonic", side_effect=[0, 0, 0.2]), patch(
            "scripts.frontend_local_runtime_smoke.time.sleep"
        ):
            result = _wait_tab(browser, "genesis", timeout_s=1)
        self.assertFalse(result["loadingFallback"])
        self.assertEqual(browser.calls, 2)

    def test_missing_heading_is_not_render_proof(self):
        browser = FakeBrowser([snapshot(loading=False, heading="")])
        with patch("scripts.frontend_local_runtime_smoke.time.monotonic", side_effect=[0, 0, 1]), patch(
            "scripts.frontend_local_runtime_smoke.time.sleep"
        ):
            result = _wait_tab(browser, "genesis", timeout_s=1)
        self.assertEqual(result["mainHeading"], "")
        self.assertEqual(browser.calls, 1)


if __name__ == "__main__":
    unittest.main()
