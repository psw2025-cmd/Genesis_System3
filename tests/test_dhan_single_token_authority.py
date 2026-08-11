from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "scripts" / "gcp_dhan_token_rotation_job.py"


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


if __name__ == "__main__":
    unittest.main()
