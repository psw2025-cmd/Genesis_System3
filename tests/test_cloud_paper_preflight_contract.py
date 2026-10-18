"""Read-only cloud deployment preflight must report—not conceal—missing authority."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from system3_cloud_paper_preflight import (  # noqa: E402
    CANONICAL_DOCKERFILE, ROOT_MARKER, check_repo
)


class CloudPaperPreflightTests(unittest.TestCase):
    def test_repository_is_blocked_until_manual_deploy_and_separate_owner_approval(self):
        report = check_repo(ROOT, "test-source-sha")
        gates = {c["id"]: c for c in report["checks"]}
        self.assertEqual(report["project"], "system3-openalgo-safe")
        self.assertEqual(report["project_number"], "802404398783")
        self.assertEqual(report["canonical_dockerfile"], CANONICAL_DOCKERFILE)
        self.assertEqual(report["source_sha"], "test-source-sha")
        self.assertEqual(report["overall"], "BLOCKED")
        self.assertEqual(gates["ROOT_IMAGE_NONPRODUCTION"]["status"], "PASS")
        self.assertEqual(gates["CANONICAL_IMAGE_SOURCE"]["status"], "PASS")
        self.assertEqual(gates["CLOUD_PORT_AND_SECURE_APP"]["status"], "PASS")
        self.assertEqual(gates["GCP_MUTATION_AUTHORITY"]["status"], "BLOCKED")
        self.assertEqual(gates["LIVE_PRODUCTION_EVIDENCE"]["status"], "UNKNOWN")
        self.assertIn(gates["MANUAL_ONLY_DEPLOY_WORKFLOW"]["status"], {"BLOCKED", "PASS"})
        for flag in ("gcp_mutations_performed", "broker_calls_performed", "secrets_read",
                     "live_order_authority"):
            self.assertIs(report[flag], False)
        checksum = report.pop("receipt_sha256")
        encoded = json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(checksum, hashlib.sha256(encoded).hexdigest())

    def test_missing_project_inputs_fail_closed_and_cannot_claim_production_pass(self):
        with tempfile.TemporaryDirectory() as path:
            report = check_repo(Path(path), "sha")
        gates = {c["id"]: c["status"] for c in report["checks"]}
        self.assertEqual(report["overall"], "BLOCKED")
        self.assertEqual(gates["CLOUD_ONLY_AUTHORITY"], "BLOCKED")
        self.assertEqual(gates["ROOT_IMAGE_NONPRODUCTION"], "BLOCKED")
        self.assertEqual(gates["CANONICAL_IMAGE_SOURCE"], "BLOCKED")
        self.assertEqual(gates["DEPLOY_IMPLEMENTATION"], "BLOCKED")

    def test_auto_deploy_workflow_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            candidate = root / ".github/workflows/system3-cloud-paper-deploy.yml"
            candidate.parent.mkdir(parents=True)
            candidate.write_text(
                "on:\n  push:\n    branches: [main]\n  workflow_dispatch:\n",
                encoding="utf-8",
            )
            report = check_repo(root)
        gates = {c["id"]: c["status"] for c in report["checks"]}
        self.assertEqual(gates["MANUAL_ONLY_DEPLOY_WORKFLOW"], "BLOCKED")

    def test_cli_report_exit_is_not_release_pass_and_strict_exits_two(self):
        script = ROOT / "scripts/system3_cloud_paper_preflight.py"
        result = subprocess.run(
            [sys.executable, str(script), "--repo", str(ROOT), "--strict"],
            capture_output=True, text=True, check=False, timeout=15,
        )
        self.assertEqual(result.returncode, 2, result.stderr[:500])
        report = json.loads(result.stdout)
        self.assertEqual(report["overall"], "BLOCKED")
        self.assertEqual(report["checks"][-2]["id"], "GCP_MUTATION_AUTHORITY")


if __name__ == "__main__":
    unittest.main()
