from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


_SPEC = importlib.util.spec_from_file_location(
    "system3_gcp_ui_tab_visual_retry_test", Path("scripts/gcp_ui_tab_visual_proof.py")
)
assert _SPEC and _SPEC.loader
proof = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(proof)


class _Response:
    status_code = 200


class _FakeBrowser:
    created: list[int] = []

    def __init__(self, *, page_load_timeout_s: int):
        self.page_load_timeout_s = page_load_timeout_s
        self.created.append(page_load_timeout_s)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


class UiTabRetryContractTests(unittest.TestCase):
    def setUp(self):
        _FakeBrowser.created = []

    @staticmethod
    def _pass_row(index: int, tab_id: str, label: str, dashboard_url: str, retry: bool):
        return index, {
            "id": tab_id,
            "label": label,
            "url": f"{dashboard_url}?tab={tab_id}",
            "proof_state": "PASS",
            "review_state": "PENDING_USER_REVIEW",
            "failures": [],
            "capture_retry": retry,
            "active_tab_proven": True,
            "mobile_active_tab_proven": True,
            "dashboard_api_key_prompt_rendered": False,
            "system3_marker": True,
            "desktop_file": f"tabs/{index:02d}-{tab_id}-desktop.png",
            "desktop_sha256": "a" * 64,
            "mobile_file": f"tabs/{index:02d}-{tab_id}-mobile.png",
            "mobile_sha256": "b" * 64,
            "browser_transport": "webdriver_single_session",
            "mobile_reload_required": False,
        }, []

    def test_failed_tabs_retry_once_in_fresh_single_browser_and_close_matrix(self):
        fail_first = {"truth", "e2e-proof", "signals", "trade"}
        calls: dict[str, list[bool]] = {tab_id: [] for tab_id, _ in proof.TABS}

        def fake_capture(browser, index, tab_id, label, dashboard_url, *, retry=False):
            self.assertIsInstance(browser, _FakeBrowser)
            calls[tab_id].append(retry)
            if tab_id in fail_first and not retry:
                return index, {
                    "id": tab_id,
                    "label": label,
                    "url": f"{dashboard_url}?tab={tab_id}",
                    "proof_state": "FAIL",
                    "review_state": "PENDING_USER_REVIEW",
                    "failures": ["synthetic_timeout"],
                    "capture_retry": False,
                }, [f"{tab_id}:capture_failed"]
            return self._pass_row(index, tab_id, label, dashboard_url, retry)

        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            with (
                patch.object(proof, "OUT", out),
                patch.object(proof, "TABS_OUT", out / "tabs"),
                patch.object(proof, "EXPECTED_SHA", "1" * 40),
                patch.object(proof, "_service_url", return_value="https://example.invalid"),
                patch.object(proof.requests, "get", return_value=_Response()),
                patch.object(proof, "ChromeDriverSession", _FakeBrowser),
                patch.object(proof, "_capture_tab", side_effect=fake_capture),
            ):
                self.assertEqual(proof.main(), 0)

            matrix = json.loads((out / "tab_visual_matrix.json").read_text(encoding="utf-8"))
            self.assertEqual(matrix["state"], "PASS")
            self.assertEqual(matrix["pass_count"], 22)
            self.assertEqual(matrix["fail_count"], 0)
            self.assertEqual(matrix["initial_fail_count"], 4)
            self.assertEqual(matrix["retry_count"], 4)
            self.assertEqual(matrix["browser_transport"], "webdriver_single_session")
            self.assertFalse(matrix["mobile_reload_required"])
            self.assertEqual(
                _FakeBrowser.created,
                [proof.PAGE_LOAD_TIMEOUT_S, proof.RETRY_PAGE_LOAD_TIMEOUT_S],
            )
            for tab_id, _ in proof.TABS:
                expected = [False, True] if tab_id in fail_first else [False]
                self.assertEqual(calls[tab_id], expected)

    def test_retry_remains_fail_closed_when_retry_fails(self):
        target = "truth"

        def fake_capture(browser, index, tab_id, label, dashboard_url, *, retry=False):
            if tab_id == target:
                return index, {
                    "id": tab_id,
                    "label": label,
                    "url": f"{dashboard_url}?tab={tab_id}",
                    "proof_state": "FAIL",
                    "review_state": "PENDING_USER_REVIEW",
                    "failures": ["synthetic_timeout"],
                    "capture_retry": retry,
                }, [f"{tab_id}:capture_failed"]
            return self._pass_row(index, tab_id, label, dashboard_url, retry)

        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            with (
                patch.object(proof, "OUT", out),
                patch.object(proof, "TABS_OUT", out / "tabs"),
                patch.object(proof, "EXPECTED_SHA", "2" * 40),
                patch.object(proof, "_service_url", return_value="https://example.invalid"),
                patch.object(proof.requests, "get", return_value=_Response()),
                patch.object(proof, "ChromeDriverSession", _FakeBrowser),
                patch.object(proof, "_capture_tab", side_effect=fake_capture),
            ):
                self.assertEqual(proof.main(), 1)

            matrix = json.loads((out / "tab_visual_matrix.json").read_text(encoding="utf-8"))
            self.assertEqual(matrix["state"], "FAIL")
            self.assertEqual(matrix["pass_count"], 21)
            self.assertEqual(matrix["retry_count"], 1)
            self.assertIn("truth:capture_failed", matrix["failures"])

    def test_source_uses_webdriver_single_session_not_per_capture_chrome_cli(self):
        source = Path("scripts/gcp_ui_tab_visual_proof.py").read_text(encoding="utf-8")
        self.assertIn("class ChromeDriverSession", source)
        self.assertIn('pageLoadStrategy\": \"eager', source)
        self.assertIn("CHROMEWEBDRIVER", source)
        self.assertIn("/window/rect", source)
        self.assertIn("/screenshot", source)
        self.assertIn('"mobile_reload_required": False', source)
        self.assertNotIn("ThreadPoolExecutor", source)
        self.assertNotIn("--dump-dom", source)
        self.assertNotIn("--screenshot=", source)
        self.assertEqual(source.count("(\"decision-intel\", \"Decision Intel\")"), 1)


if __name__ == "__main__":
    unittest.main()
