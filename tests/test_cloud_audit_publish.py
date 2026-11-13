"""Offline tests for immutable, fail-closed GCS audit publication."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.cloud_audit_publish import FILES, authorized_files, copy_and_verify, publish, gcloud


class InMemoryGcs:
    def __init__(self):
        self.objects = {}
    def __call__(self, command, *args):
        assert command == "cp"
        assert "--quiet" in args
        src, dst = args[-2:]
        if src.startswith("gs://"):
            Path(dst).write_bytes(self.objects[src])
        else:
            data = Path(src).read_bytes()
            if dst not in self.objects:  # --no-clobber
                self.objects[dst] = data


class AuditPublicationTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        audit = self.root / "audit_results"
        audit.mkdir()
        for name in FILES:
            (audit / name).write_text("Evidence for " + name, encoding="utf-8")
        (audit / "executive_summary.json").write_text(json.dumps({"source_sha": "b" * 40}))

    def test_verified_exact_13_and_receipt(self):
        storage = InMemoryGcs()
        receipt = publish(self.root, "a" * 40, storage)
        self.assertEqual(receipt["object_count"], 13)
        self.assertEqual(len(storage.objects), 14)
        self.assertFalse(receipt["production_traffic_mutated"])
        self.assertTrue(all("/genesis-audits/" + "a" * 40 + "/" in k for k in storage.objects))

    def test_duplicate_same_contents_is_idempotent(self):
        storage = InMemoryGcs()
        publish(self.root, "a" * 40, storage)
        publish(self.root, "a" * 40, storage)
        self.assertEqual(len(storage.objects), 14)

    def test_conflicting_write_rejected_by_readback(self):
        storage = InMemoryGcs()
        publish(self.root, "a" * 40, storage)
        (self.root / "audit_results" / FILES[0]).write_text("changed")
        with self.assertRaisesRegex(RuntimeError, "SHA256_MISMATCH"):
            publish(self.root, "a" * 40, storage)

    def test_cli_error_reports_only_sanitized_class(self):
        class Failed:
            returncode = 1
            stderr = "PERMISSION_DENIED: private-account@example.com not authorized"
            stdout = ""
        with patch("scripts.cloud_audit_publish.subprocess.run", return_value=Failed()):
            with self.assertRaisesRegex(RuntimeError, "GCS_PERMISSION_DENIED_OP_CP") as caught:
                gcloud("cp", "a", "b")
        self.assertNotIn("private-account@", str(caught.exception))

    def test_missing_file_blocks_publication(self):
        (self.root / "audit_results" / FILES[0]).unlink()
        with self.assertRaises(ValueError):
            authorized_files(self.root)

    def test_invalid_sha_blocks_publication(self):
        with self.assertRaises(ValueError):
            publish(self.root, "not-a-sha", InMemoryGcs())


if __name__ == "__main__":
    unittest.main()
