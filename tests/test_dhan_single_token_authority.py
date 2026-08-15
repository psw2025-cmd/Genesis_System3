from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "scripts" / "gcp_dhan_token_rotation_job.py"
RUNTIME_PATCH = ROOT / "core" / "brokers" / "dhan" / "cloud_runtime_patch.py"


class DhanSingleAuthorityTests(unittest.TestCase):
    def test_legacy_token_manager_is_status_only(self):
        text = (ROOT / "core" / "brokers" / "dhan" / "token_manager.py").read_text(encoding="utf-8")
        forbidden = [
            "Dhan" + "Login(",
            ".generate" + "_token(",
            ".renew" + "_token(",
            ".consume" + "_token_id(",
            "add_secret" + "_version(",
            "system3-dhan-" + "access-token",
            "py" + "otp",
        ]
        for marker in forbidden:
            self.assertNotIn(marker, text, marker)
        self.assertIn('"strategy": "RETIRED"', text)
        self.assertIn('"mutation_attempted": False', text)

    def test_preflight_and_watchdog_cannot_refresh(self):
        paths = [
            ROOT / "core" / "brokers" / "dhan" / "preflight.py",
            ROOT / "scripts" / "system3_self_healing_watchdog.py",
        ]
        refresh_call = "refresh" + "_token("
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(refresh_call, text, str(path))
            self.assertNotIn("Dhan" + "Login(", text, str(path))

    def test_only_canonical_job_contains_dhan_mint_primitives(self):
        allowed = CANONICAL.resolve()
        markers = [
            "Dhan" + "Login(",
            ".generate" + "_token(",
            ".renew" + "_token(",
            ".consume" + "_token_id(",
            "generateAccess" + "Token",
        ]
        offenders: list[str] = []
        roots = [ROOT / "core", ROOT / "scripts", ROOT / "tools"]
        for scan_root in roots:
            if not scan_root.exists():
                continue
            for path in scan_root.rglob("*.py"):
                if path.resolve() == allowed:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if any(marker in text for marker in markers):
                    offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [], f"competing Dhan token authorities: {offenders}")

    def test_obsolete_render_secret_sync_is_deleted(self):
        self.assertFalse((ROOT / "tools" / "sync_render_secrets.py").exists())

    def test_canonical_job_is_locked_to_one_secret(self):
        text = CANONICAL.read_text(encoding="utf-8")
        self.assertIn('AUTHORITY = "gcp-cloud-run-job"', text)
        self.assertIn('SECRET_ID = os.getenv("DHAN_ACCESS_TOKEN_SECRET_ID", "dhan-access-token")', text)
        self.assertNotIn("system3-dhan-" + "access-token", text)
        self.assertIn("add_secret" + "_version", text)


class DhanRotationVersionCoordinationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.job = CANONICAL.read_text(encoding="utf-8")
        cls.patch = RUNTIME_PATCH.read_text(encoding="utf-8")
        ast.parse(cls.job)
        ast.parse(cls.patch)

    def test_web_self_heal_passes_non_secret_expected_version_override(self):
        self.assertIn("DHAN_ROTATION_EXPECTED_VERSION", self.patch)
        self.assertIn('"overrides"', self.patch)
        self.assertIn('"containerOverrides"', self.patch)
        self.assertIn('"expected_secret_version"', self.patch)
        self.assertNotIn('"DHAN_PIN"', self.patch)
        self.assertNotIn('"DHAN_TOTP_SECRET"', self.patch)

    def test_job_uses_authoritative_latest_secret_not_mounted_access_token_snapshot(self):
        self.assertIn("_latest_token_snapshot", self.job)
        self.assertIn("versions/latest", self.job)
        self.assertNotIn('token = os.getenv("DHAN_ACCESS_TOKEN"', self.job)
        self.assertIn('"raw_token_exposed": False', self.job)

    def test_cloud_run_execution_provides_bounded_stagger_and_recheck(self):
        self.assertIn("CLOUD_RUN_EXECUTION", self.job)
        self.assertIn("_execution_stagger_s", self.job)
        self.assertIn("hashlib.sha256(execution.encode", self.job)
        self.assertIn("time.sleep(settle_s)", self.job)
        self.assertIn("settled_token, settled_secret = _latest_token_snapshot()", self.job)
        self.assertIn("SKIPPED_CONCURRENT_ROTATION_WON", self.job)
        self.assertIn("post_stagger_latest_valid", self.job)

    def test_coordination_never_weakens_trading_safety_or_order_boundary(self):
        for text in (self.job, self.patch):
            self.assertIn('"live_trading_enabled": False', text)
            self.assertIn('"raw_token_exposed": False', text)
        self.assertIn('os.environ["LIVE_TRADING_ENABLED"] = "0"', self.job)
        self.assertIn('os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"', self.job)
        self.assertIn('os.environ["AUTO_EXECUTE_TRADES"] = "0"', self.job)
        self.assertIn('"order_endpoints_called": False', self.job)
        for marker in ("place_order(", "modify_order(", "cancel_order("):
            self.assertNotIn(marker, self.job)
            self.assertNotIn(marker, self.patch)

    def test_expected_version_is_metadata_not_a_token_payload(self):
        self.assertIn('before_version = str(before.get("secret_version")', self.patch)
        self.assertIn('"value": before_version', self.patch)
        self.assertIn('expected_version = os.getenv("DHAN_ROTATION_EXPECTED_VERSION"', self.job)
        self.assertIn("expected_secret_version=expected_version", self.job)


class DhanRotationTriStateGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.job = CANONICAL.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.job)

        decision_nodes = [
            node
            for node in cls.tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in {"_near_expiry", "_should_rotate", "_non_rotation_status"}
        ]
        module = ast.Module(body=decision_nodes, type_ignores=[])
        ast.fix_missing_locations(module)
        cls.ns = {
            "MIN_HOURS": 6.0,
            "PROFILE_VALID": "VALID",
            "PROFILE_AUTH_INVALID": "AUTH_INVALID",
            "PROFILE_TRANSIENT_ERROR": "TRANSIENT_ERROR",
            "PROFILE_CONFIG_ERROR": "CONFIG_ERROR",
        }
        exec(compile(module, str(CANONICAL), "exec"), cls.ns)

    def test_transient_network_error_does_not_authorize_mint(self):
        should_rotate = self.ns["_should_rotate"]
        before = {"auth_state": "TRANSIENT_ERROR", "hours_remaining": 12.0, "valid": False}
        self.assertFalse(should_rotate(before))

    def test_explicit_auth_rejection_authorizes_mint(self):
        should_rotate = self.ns["_should_rotate"]
        before = {"auth_state": "AUTH_INVALID", "hours_remaining": 12.0, "valid": False}
        self.assertTrue(should_rotate(before))

    def test_proven_near_expiry_authorizes_rotation_even_when_profile_probe_is_transient(self):
        should_rotate = self.ns["_should_rotate"]
        before = {"auth_state": "TRANSIENT_ERROR", "hours_remaining": 1.0, "valid": False}
        self.assertTrue(should_rotate(before))

    def test_config_error_without_expiry_cannot_mint(self):
        should_rotate = self.ns["_should_rotate"]
        before = {"auth_state": "CONFIG_ERROR", "hours_remaining": None, "valid": False}
        self.assertFalse(should_rotate(before))

    def test_transient_non_rotation_is_visible_failure_not_false_green(self):
        status, rc = self.ns["_non_rotation_status"](
            {"auth_state": "TRANSIENT_ERROR"}, "SKIPPED_TOKEN_HEALTHY"
        )
        self.assertEqual(status, "BLOCKED_TRANSIENT_PROFILE_ERROR")
        self.assertEqual(rc, 2)

    def test_exception_classification_is_conservative(self):
        self.assertIn("PROFILE_TRANSIENT_ERROR", self.job)
        self.assertIn("PROFILE_AUTH_INVALID if auth_invalid else PROFILE_TRANSIENT_ERROR", self.job)
        self.assertIn("status_code == 401", self.job)
        self.assertIn('"transient_errors_authorize_mint": False', self.job)
        self.assertIn("BLOCKED_STAGGER_REVALIDATION_ERROR", self.job)
        self.assertIn("BLOCKED_MINT_NOT_AUTHORIZED", self.job)

    def test_generated_token_is_validated_once_before_persistence(self):
        self.assertEqual(self.job.count("generated_check = _profile_probe(client_id, new_token)"), 1)
        persist_index = self.job.index("new_version = _persist_authoritative_token(new_token)")
        generated_index = self.job.index("generated_check = _profile_probe(client_id, new_token)")
        self.assertLess(generated_index, persist_index)
        self.assertIn('"post_persist_profile_reprobe_performed": False', self.job)


if __name__ == "__main__":
    unittest.main()
