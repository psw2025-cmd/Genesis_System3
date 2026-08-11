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
        self.assertIn('os.environ["DHAN_TOKEN_ROTATION_AUTHORITY"] = AUTHORITY', text)
        self.assertIn('AUTHORITY = "gcp-cloud-run-job"', text)
        self.assertIn('SECRET_ID = os.getenv("DHAN_ACCESS_TOKEN_SECRET_ID", "dhan-access-token")', text)
        self.assertIn('"order_endpoints_called": False', text)
        self.assertIn("secret_version_advanced", text)
        self.assertIn("_persist_authoritative_token", text)
        self.assertIn("DhanLogin(client_id).generate_token", text)
        self.assertNotIn("from core.brokers.dhan.token_manager", text)
        self.assertNotIn("system3-dhan-access-token", text)
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

    def test_legacy_token_writers_are_permanently_non_mutating(self):
        codespace = Path("scripts/codespace_startup.sh").read_text(encoding="utf-8")
        daemon = Path("scripts/dhan_token_auto_refresh.py").read_text(encoding="utf-8")
        startup = Path("scripts/dhan_startup_check.py").read_text(encoding="utf-8")
        watchdog = Path("core/brokers/dhan/token_watchdog.py").read_text(encoding="utf-8")
        runner = Path("scripts/dhan_watchdog_runner.py").read_text(encoding="utf-8")
        setup = Path("scripts/setup_dhan_automation.py").read_text(encoding="utf-8")
        legacy_worker = Path("scripts/cloud_worker.py").read_text(encoding="utf-8")

        self.assertIn('pkill -f "dhan_token_auto_refresh.py"', codespace)
        self.assertNotIn('nohup "$PY" -u "$PROJ/scripts/dhan_token_auto_refresh.py"', codespace)
        self.assertNotIn('"$PY" "$PROJ/scripts/dhan_startup_check.py"', codespace)

        for text in (daemon, startup, watchdog, runner, setup, legacy_worker):
            self.assertNotIn("refresh_token(", text)
            self.assertNotIn("generate_token(", text)
            self.assertNotIn("renew_token(", text)

        self.assertIn('"status": "RETIRED"', legacy_worker)
        self.assertNotIn("run_watchdog_loop", legacy_worker)
        self.assertNotIn("run_daemon()", legacy_worker)

    def test_cloud_runtime_escalates_only_to_canonical_rotation_job(self):
        patch = Path("core/brokers/dhan/cloud_runtime_patch.py").read_text(encoding="utf-8")
        self.assertIn("_invoke_canonical_rotation", patch)
        self.assertIn("jobs/{job}:run", patch)
        self.assertIn("metadata.google.internal", patch)
        self.assertIn("SecretVersionDidNotAdvance", patch)
        self.assertIn("_live_is_locked", patch)
        self.assertIn("SINGLE_FLIGHT_BUSY", patch)
        self.assertIn("COOLDOWN", patch)
        self.assertNotIn("refresh_token(", patch)
        for marker in ("place_order(", "modify_order(", "cancel_order("):
            self.assertNotIn(marker, patch)

    def test_public_paper_dashboard_contract_across_gcp_deploy_paths(self):
        workflow = Path(".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
        deploy_script = Path("scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
        manual_script = Path("deploy/gcp/deploy_web.sh").read_text(encoding="utf-8")
        recovery = Path(".github/workflows/gcp-dhan-token-rotation.yml").read_text(encoding="utf-8")

        self.assertIn("REQUIRE_API_KEY=false", workflow)
        self.assertIn("--remove-secrets=API_KEY", workflow)
        self.assertNotIn("API_KEY_SECRET_ID", workflow)
        self.assertNotIn("system3-dashboard-api-key", workflow)
        self.assertIn("WORKER_PUSH_TOKEN_SECRET_ID", workflow)
        self.assertIn("system3-dashboard-worker-push-token", workflow)

        self.assertIn('.required == false', workflow)
        self.assertIn('.mode == "auth_disabled"', workflow)
        self.assertIn('"API_KEY" in secret_env_names', workflow)
        self.assertIn('"WORKER_PUSH_TOKEN" not in secret_env_names', workflow)

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

        self.assertNotIn("system3-dashboard-api-key", recovery)
        self.assertNotIn("X-API-Key", recovery)
        self.assertIn('/api/broker/status', recovery)

    def test_runtime_evidence_lock_requires_public_dashboard_and_no_api_key_mount(self):
        workflow = Path(".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
        self.assertIn('"api_key_required",', workflow)
        self.assertIn('"api_key_mounted",', workflow)
        self.assertIn("if safety.get(key):", workflow)
        self.assertNotIn('for key in ("api_key_required", "api_key_mounted"):', workflow)


if __name__ == "__main__":
    unittest.main()
