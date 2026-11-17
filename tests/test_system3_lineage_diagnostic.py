from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.system3_lineage_diagnostic import diagnose


class LineageDiagnosticTests(unittest.TestCase):
    def test_missing_receipt_never_passes_even_with_public_sha(self):
        with tempfile.TemporaryDirectory() as directory:
            result = diagnose(Path(directory), lambda: {"git_sha": "a" * 40, "revision": "test"})
            self.assertFalse(result["production_pass"])
            self.assertEqual(result["gate_reason"], "DEPLOYMENT_LINEAGE_RECEIPT_MISSING")
            self.assertEqual(result["public_serving_sha"], "a" * 40)
            self.assertEqual(result["order_calls"], 0)

    def test_untrusted_public_payload_never_proves_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            result = diagnose(Path(directory), lambda: {"data": {"git_sha": "invalid", "revision": "test"}})
            self.assertIsNone(result["public_serving_sha"])
            self.assertEqual(result["state"], "NOT_VERIFIED")
            self.assertFalse(result["production_pass"])


if __name__ == "__main__":
    unittest.main()
