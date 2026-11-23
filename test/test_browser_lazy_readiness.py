"""Focused regression tests for browser lazy-loading readiness signals.

These tests intentionally do not claim market-data or deployed-UI proof.
Run: python -m unittest discover -s test -p 'test_browser_lazy_readiness.py'
"""
import unittest

def classify(snapshot):
    """Mirror the existing smoke-test readiness contract without weakening it."""
    reasons = []
    if snapshot.get("rootChildren", 0) <= 0:
        reasons.append("react_root_empty")
    if not snapshot.get("system3"):
        reasons.append("system3_marker_missing")
    if not snapshot.get("active"):
        reasons.append("active_tab_not_proven")
    if snapshot.get("mainChars", 0) <= 10 or not snapshot.get("mainHeading"):
        reasons.append("tab_content_not_proven")
    if snapshot.get("loadingFallback"):
        reasons.append("lazy_content_still_loading")
    return reasons

class BrowserLazyReadinessTests(unittest.TestCase):
    def setUp(self):
        self.ready = dict(rootChildren=1, system3=True, active=True,
                          mainChars=120, mainHeading="Genesis", loadingFallback=False)

    def test_ready_snapshot_passes(self):
        self.assertEqual(classify(self.ready), [])

    def test_loading_fallback_is_failure_even_with_heading(self):
        self.assertIn("lazy_content_still_loading",
                      classify({**self.ready, "loadingFallback": True}))

    def test_empty_content_is_failure(self):
        self.assertIn("tab_content_not_proven",
                      classify({**self.ready, "mainChars": 0}))

    def test_inactive_route_is_failure(self):
        self.assertIn("active_tab_not_proven",
                      classify({**self.ready, "active": False}))

    def test_missing_mount_is_failure(self):
        self.assertIn("react_root_empty",
                      classify({**self.ready, "rootChildren": 0}))

if __name__ == "__main__":
    unittest.main()
