from __future__ import annotations

import base64
import importlib.util
import json
import os
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

_PROVIDER_PATH = Path("core/brokers/dhan/cloud_token_provider.py")
_SPEC = importlib.util.spec_from_file_location("system3_cloud_token_provider_test", _PROVIDER_PATH)
assert _SPEC and _SPEC.loader
provider = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(provider)


def _jwt(hours: int = 12) -> str:
    payload = {"exp": int((datetime.now(timezone.utc) + timedelta(hours=hours)).timestamp())}
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    return f"header.{body}.signature"


class _FakeClient:
    def __init__(self):
        self.version = 7
        self.token = _jwt()
        self.access_calls = 0

    def access_secret_version(self, request):
        self.access_calls += 1
        return SimpleNamespace(
            name=f"projects/test/secrets/dhan-access-token/versions/{self.version}",
            payload=SimpleNamespace(data=self.token.encode()),
        )

    def get_secret_version(self, request):
        return SimpleNamespace(create_time=datetime.now(timezone.utc))


class DynamicTokenProviderTests(unittest.TestCase):
    def setUp(self):
        self.original = dict(os.environ)
        os.environ["DHAN_TOKEN_SOURCE"] = "gcp-secret-manager-dynamic"
        os.environ["GOOGLE_CLOUD_PROJECT"] = "test"
        os.environ["DHAN_ACCESS_TOKEN_SECRET_ID"] = "dhan-access-token"
        os.environ["DHAN_TOKEN_CACHE_TTL_S"] = "30"
        self.client = _FakeClient()
        provider._set_client_factory_for_tests(lambda: self.client)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original)
        provider._set_client_factory_for_tests(None)

    def test_fetches_latest_version_and_exposes_only_safe_metadata(self):
        token = provider.get_access_token(force_refresh=True, reason="unit_test")
        self.assertEqual(token, self.client.token)
        meta = provider.token_metadata()
        self.assertEqual(meta["source"], "GCP_SECRET_MANAGER_DYNAMIC")
        self.assertEqual(meta["secret_version"], "7")
        self.assertTrue(meta["token_present"])
        self.assertFalse(meta["token_value_exposed"])
        self.assertNotIn(token, json.dumps(meta))

    def test_cache_bounds_secret_manager_reads(self):
        provider.get_access_token(force_refresh=True, reason="initial")
        provider.get_access_token(reason="second_read")
        provider.get_access_token(reason="third_read")
        self.assertEqual(self.client.access_calls, 1)

    def test_force_reload_requires_an_actual_change(self):
        provider.get_access_token(force_refresh=True, reason="initial")
        self.assertFalse(provider.force_reload("same_version"))
        self.client.version = 8
        self.client.token = _jwt(20)
        self.assertTrue(provider.force_reload("auth_failure"))
        meta = provider.token_metadata()
        self.assertEqual(meta["secret_version"], "8")
        self.assertEqual(meta["last_reload_reason"], "auth_failure")


class StaticSafetyContractTests(unittest.TestCase):
    def test_rotation_job_keeps_live_money_disabled_and_requires_persistence(self):
        text = Path("scripts/gcp_dhan_token_rotation_job.py").read_text(encoding="utf-8")
        self.assertIn('os.environ["LIVE_TRADING_ENABLED"] = "0"', text)
        self.assertIn('os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"', text)
        self.assertIn('"order_endpoints_called": False', text)
        self.assertIn("secret_version_advanced", text)
        forbidden_calls = [
            "place" + "_order(",
            "modify" + "_order(",
            "cancel" + "_order(",
        ]
        for marker in forbidden_calls:
            self.assertNotIn(marker, text)

    def test_ui_proof_never_requests_raw_token(self):
        text = Path("dashboard/frontend/src/components/BrokerProofPanel.tsx").read_text(encoding="utf-8")
        self.assertIn("Raw token exposed: NO", text)
        self.assertNotIn("access_token", text.lower())

    def test_github_rotation_is_manual_and_cloud_scheduler_is_authoritative(self):
        manual = Path(".github/workflows/gcp-dhan-token-rotation.yml").read_text(encoding="utf-8")
        deploy = Path(".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch", manual)
        self.assertNotIn("schedule:", manual)
        self.assertIn('gcloud scheduler jobs create http', deploy)
        self.assertIn('--time-zone="Asia/Kolkata"', deploy)
        self.assertIn('--schedule="30 7 * * *"', deploy)

    def test_public_paper_dashboard_contract_across_gcp_deploy_paths(self):
        workflow = Path(".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
        deploy_script = Path("scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
        manual_script = Path("deploy/gcp/deploy_web.sh").read_text(encoding="utf-8")
        recovery = Path(".github/workflows/gcp-dhan-token-rotation.yml").read_text(encoding="utf-8")

        # PAPER/ANALYZER dashboard reads are public and the reusable dashboard
        # API key must not be mounted or reintroduced by any GCP deploy path.
        self.assertIn("REQUIRE_API_KEY=false", workflow)
        self.assertIn("--remove-secrets=API_KEY", workflow)
        self.assertNotIn("API_KEY_SECRET_ID", workflow)
        self.assertNotIn("system3-dashboard-api-key", workflow)
        self.assertIn("WORKER_PUSH_TOKEN_SECRET_ID", workflow)
        self.assertIn("system3-dashboard-worker-push-token", workflow)

        # Post-deploy read proof must explicitly require auth-disabled mode.
        self.assertIn('.required == false', workflow)
        self.assertIn('.mode == "auth_disabled"', workflow)
        self.assertIn('"API_KEY" in secret_env_names', workflow)
        self.assertIn('"WORKER_PUSH_TOKEN" not in secret_env_names', workflow)

        # Live-trading flags stay off regardless of public dashboard visibility.
        self.assertIn("LIVE_TRADING_ENABLED=0", workflow)
        self.assertIn("SYSTEM3_LIVE_TRADING_ALLOWED=0", workflow)
        self.assertIn("AUTO_EXECUTE_TRADES=0", workflow)

        self.assertIn('("REQUIRE_API_KEY", "false")', deploy_script)
        self.assertNotIn("API_KEY_SECRET_ID", deploy_script)
        self.assertIn("WORKER_PUSH_TOKEN_SECRET_ID", deploy_script)
        self.assertIn('env_map.pop("API_KEY", None)', deploy_script)
        self.assertIn("DASHBOARD_PUBLIC_READONLY enforced", deploy_script)

        self.assertIn("--allow-unauthenticated", manual_script)
        self.assertIn("REQUIRE_API_KEY=false", manual_script)
        self.assertIn("--remove-secrets=API_KEY", manual_script)
        self.assertNotIn("API_KEY_SECRET_ID", manual_script)
        self.assertIn("WORKER_PUSH_TOKEN", manual_script)

        # Manual Dhan recovery proves broker status through anonymous read-only
        # GET and must never read/send the dashboard key.
        self.assertNotIn("system3-dashboard-api-key", recovery)
        self.assertNotIn("X-API-Key", recovery)
        self.assertIn('/api/broker/status', recovery)

    def test_runtime_evidence_lock_requires_public_dashboard_and_no_api_key_mount(self):
        workflow = Path(".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
        # In public PAPER mode, api_key_required/api_key_mounted being true is a
        # deployment failure; worker auth remains separate.
        self.assertIn('"api_key_required",', workflow)
        self.assertIn('"api_key_mounted",', workflow)
        self.assertIn("if safety.get(key):", workflow)
        self.assertNotIn('for key in ("api_key_required", "api_key_mounted"):', workflow)


if __name__ == "__main__":
    unittest.main()
