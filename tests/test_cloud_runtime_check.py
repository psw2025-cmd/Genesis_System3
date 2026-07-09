import unittest

from tools.cloud_runtime_check import analyze


def _endpoint(ok: bool, status_code=None, payload=None, error=None):
    return {
        "url_path": "/mock",
        "url": "https://example.test/mock",
        "ok": ok,
        "status_code": status_code,
        "latency_ms": 1.0,
        "json": payload,
        "text_preview": None,
        "error": error,
    }


def _base_results():
    results = {
        "deploy_info": _endpoint(False, 401, error="HTTPError: 401"),
        "health": _endpoint(True, 200, payload={"status": "ok"}),
        "auth_status": _endpoint(True, 200, payload={"required": True, "authenticated": False}),
        "memory_before": _endpoint(False, 401, error="HTTPError: 401"),
        "broker_status": _endpoint(False, 401, error="HTTPError: 401"),
        "broker_dhan_status": _endpoint(False, 401, error="HTTPError: 401"),
        "broker_deps": _endpoint(False, 401, error="HTTPError: 401"),
        "scheduler_health": _endpoint(False, 401, error="HTTPError: 401"),
        "portfolio_unified": _endpoint(False, 401, error="HTTPError: 401"),
        "memory_after_portfolio": _endpoint(False, 401, error="HTTPError: 401"),
        "chain_nifty": _endpoint(False, 401, error="HTTPError: 401"),
        "memory_after_chain": _endpoint(False, 401, error="HTTPError: 401"),
        "underlyings": _endpoint(False, 401, error="HTTPError: 401"),
        "state": _endpoint(False, 401, error="HTTPError: 401"),
    }
    return results


class CloudRuntimeCheckAnalyzeTests(unittest.TestCase):
    def test_auth_required_401s_are_reported_as_limited_visibility(self):
        report = analyze("https://example.test", _base_results(), expected_commit="")
        warning_keys = {w["key"] for w in report["warnings"]}

        self.assertIn("auth_required_limited_visibility", warning_keys)
        self.assertNotIn("endpoint_broker_status", warning_keys)
        self.assertNotIn("broker_not_connected", warning_keys)
        self.assertEqual(report["key_facts"]["api_auth_required"], True)
        self.assertEqual(report["key_facts"]["api_auth_authenticated"], False)
        self.assertIn("broker_status_auth_protected", report["passed"])

    def test_broker_warning_remains_when_auth_not_required(self):
        results = _base_results()
        results["auth_status"] = _endpoint(True, 200, payload={"required": False, "authenticated": True})

        report = analyze("https://example.test", results, expected_commit="")
        warning_keys = {w["key"] for w in report["warnings"]}

        self.assertIn("endpoint_broker_status", warning_keys)
        self.assertIn("broker_not_connected", warning_keys)
        self.assertNotIn("auth_required_limited_visibility", warning_keys)

    def test_auth_can_be_inferred_from_401_session_message(self):
        results = _base_results()
        results["auth_status"] = _endpoint(False, 404, error="HTTPError: 404")
        for name, item in results.items():
            if name in {
                "deploy_info",
                "memory_before",
                "broker_status",
                "broker_dhan_status",
                "broker_deps",
                "scheduler_health",
                "portfolio_unified",
                "memory_after_portfolio",
                "chain_nifty",
                "memory_after_chain",
                "underlyings",
                "state",
            }:
                item["text_preview"] = '{"detail":"Missing or invalid dashboard API session"}'

        report = analyze("https://example.test", results, expected_commit="")
        warning_keys = {w["key"] for w in report["warnings"]}

        self.assertIn("auth_required_limited_visibility", warning_keys)
        self.assertNotIn("endpoint_broker_status", warning_keys)


if __name__ == "__main__":
    unittest.main()
