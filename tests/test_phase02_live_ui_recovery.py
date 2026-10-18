"""Phase 0.2: harden production evidence references and fail closed without deployment."""
import importlib
import json
import os
from pathlib import Path
import py_compile
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from system3_release_proof_gate import IDENTITY, RECEIPT, main as gate_main, resolve


class ProductionProofRecoveryTests(unittest.TestCase):
    def test_workflow_references_existing_compilable_proof(self):
        workflow = (ROOT / ".github/workflows/frontend-runtime-smoke.yml").read_text(encoding="utf-8")
        self.assertIn("python scripts/system3_release_proof_gate.py --write-github-env", workflow)
        self.assertIn("timeout 900s python scripts/gcp_live_ui_snapshot.py", workflow)
        for name in ("system3_release_proof_gate.py", "gcp_live_ui_snapshot.py"):
            script = ROOT / "scripts" / name
            self.assertTrue(script.is_file(), name)
            py_compile.compile(str(script), doraise=True)

    def test_missing_receipt_fails_closed_and_creates_nonpass_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(gate_main(["--repo", str(root)]), 2)
            manifest = json.loads((root / "live-production-ui-proof/manifest.json").read_text())
            self.assertEqual(manifest["state"], "BLOCKED")
            self.assertEqual(manifest["reason"], "DEPLOYMENT_LINEAGE_RECEIPT_MISSING")
            self.assertIs(manifest["production_pass"], False)
            self.assertEqual(manifest["gcp_mutations"], 0)
            self.assertEqual(manifest["order_calls"], 0)

    def test_receipt_requires_correct_project_full_sha_digest_and_approval_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / RECEIPT
            path.parent.mkdir(parents=True)
            value = {**IDENTITY, "source_sha": "a"*40,
                     "image_digest": "sha256:" + "b"*64,
                     "state": "DEPLOYED", "owner_approval_ref": "receipt-id"}
            for key, invalid in (
                ("project_id", "fno-angel-prod-1790444589"),
                ("source_sha", "a"*7),
                ("image_digest", "sha256:invalid"),
                ("owner_approval_ref", ""),
            ):
                path.write_text(json.dumps({**value, key: invalid}), encoding="utf-8")
                self.assertEqual(resolve(root)["state"], "BLOCKED", key)
            path.write_text(json.dumps(value), encoding="utf-8")
            result = resolve(root)
            self.assertEqual(result["state"], "EXPECTED_SHA_RESOLVED")
            self.assertIs(result["production_pass"], False)
            self.assertEqual(result["source_authority"], "RECEIPT_HINT_ONLY_NOT_SERVING_PROOF")

    def test_restored_live_capture_rejects_abbreviated_sha(self):
        proof = importlib.import_module("gcp_live_ui_snapshot")
        self.assertTrue(proof._sha_matches("a"*40, "a"*40))
        self.assertFalse(proof._sha_matches("a"*40, "a"*7))
        self.assertFalse(proof._sha_matches("a"*40, "b"*40))
        self.assertFalse(proof._sha_matches("", "a"*40))

    def test_unavailable_public_runtime_never_converges(self):
        proof = importlib.import_module("gcp_live_ui_snapshot")
        with patch.dict(os.environ, {"SYSTEM3_EXPECTED_SERVING_SHA": "a"*40}):
            with patch.object(proof, "_json_get", return_value={}):
                with patch.object(proof, "DEPLOY_WAIT_SECONDS", 0):
                    good, _, details = proof._wait_for_expected_serving_sha()
        self.assertIs(good, False)
        self.assertEqual(details["reason"], "EXPECTED_SERVING_SHA_NOT_CONVERGED")


if __name__ == "__main__":
    unittest.main()
