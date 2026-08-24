"""Regression contract for same-document production semantic proof."""
from __future__ import annotations

import unittest

from scripts.gcp_live_ui_semantic_proof import (
    KEY_TAB_FORBIDDEN,
    _scan_tabs_same_document,
)


class FakeBrowser:
    session_id = "fake-session"

    def __init__(self, *, reload_after_click: int | None = None) -> None:
        self.active = next(iter(KEY_TAB_FORBIDDEN))
        self.document_id = "doc-1"
        self.clicks = 0
        self.reload_after_click = reload_after_click
        self.navigate_calls = 0

    def navigate(self, _url: str) -> None:
        self.navigate_calls += 1
        raise AssertionError("tab scan must not navigate/reload the SPA")

    def wait_for_active(self, tab_id: str) -> dict:
        self.active = tab_id
        return self.proof_snapshot(tab_id)

    def proof_snapshot(self, tab_id: str) -> dict:
        return {"active": self.active == tab_id, "system3": True}

    def _request(self, _method: str, _path: str, payload=None, **_kwargs):
        script = str((payload or {}).get("script") or "")
        args = (payload or {}).get("args") or []
        if "__SYSTEM3_SEMANTIC_PROOF_DOCUMENT_ID__" in script:
            return {
                "document_id": self.document_id,
                "time_origin": 123456.0,
                "href": f"https://example.test/ui?tab={self.active}",
                "ready_state": "complete",
            }
        if "data-dashboard-tab" in script and "button.click()" in script:
            self.clicks += 1
            self.active = str(args[0])
            if self.reload_after_click is not None and self.clicks >= self.reload_after_click:
                self.document_id = "doc-2"
            return True
        if "document.body" in script and "toUpperCase" in script:
            return "SYSTEM3 READY PAPER LIVE OFF"
        raise AssertionError(f"unexpected webdriver script: {script[:80]}")


class SameDocumentSemanticProofTests(unittest.TestCase):
    def test_tab_scan_uses_clicks_without_navigation(self) -> None:
        browser = FakeBrowser()
        result = _scan_tabs_same_document(browser, expect_open=False)
        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["navigation_mode"], "single_document_dashboard_tab_clicks")
        self.assertEqual(browser.navigate_calls, 0)
        self.assertEqual(browser.clicks, len(KEY_TAB_FORBIDDEN))
        self.assertEqual({row["document_id"] for row in result["rows"]}, {"doc-1"})

    def test_document_epoch_change_fails_closed(self) -> None:
        browser = FakeBrowser(reload_after_click=2)
        result = _scan_tabs_same_document(browser, expect_open=False)
        self.assertEqual(result["state"], "FAIL")
        self.assertTrue(
            any("document_reloaded_during_tab_scan" in failure for failure in result["failures"]),
            result["failures"],
        )


if __name__ == "__main__":
    unittest.main()
