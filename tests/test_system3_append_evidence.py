"""Protect persistent evidence from duplicate IDs and mutation of historical records."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "SYSTEM3/10_HANDOVER"))
from append_evidence import append_receipt

URL = "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/39093854982"
BASE = "1dbae834605b7cbabd57eda82a9db182deb0822c"


class AppendOnlyEvidenceTests(unittest.TestCase):
    def test_appending_preserves_every_byte_and_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "EVIDENCE.ndjson"
            original = {"id": "old", "schema": "system3-evidence-v1",
                        "status": "UNKNOWN", "evidence_url": URL, "source_sha": BASE}
            old = (json.dumps(original)+"\n").encode()
            p.write_bytes(old)
            item = {"id":"new","status":"PASS","claim":"test receipt","evidence_url":URL,"source_sha":BASE}
            append_receipt(p,item)
            self.assertTrue(p.read_bytes().startswith(old))
            self.assertEqual(len(p.read_text().splitlines()),2)
            prior = p.read_bytes()
            with self.assertRaisesRegex(ValueError,"duplicate"):
                append_receipt(p,item)
            self.assertEqual(p.read_bytes(),prior)

    def test_invalid_status_source_or_url_cannot_be_appended(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"EVIDENCE.ndjson";p.write_bytes(b"")
            valid={"id":"x","status":"PASS","claim":"verified","evidence_url":URL,"source_sha":BASE}
            for key,val in (("status","VERIFIED"),("source_sha","abcdef"),
                            ("evidence_url","https://example.com/fake")):
                with self.assertRaises(ValueError):
                    append_receipt(p,{**valid,key:val})
            self.assertEqual(p.read_bytes(),b"")

    def test_committed_ledger_extends_main_instead_of_replacing_prior_records(self):
        current=(ROOT/"SYSTEM3/02_EVIDENCE/EVIDENCE.ndjson").read_bytes()
        probe=subprocess.run(["git","show","origin/main:SYSTEM3/02_EVIDENCE/EVIDENCE.ndjson"],
                             cwd=ROOT,capture_output=True,check=False)
        if probe.returncode == 0:
            self.assertTrue(current.startswith(probe.stdout),"Evidence history was rewritten or truncated")
        else:
            self.assertGreaterEqual(len(current.splitlines()),8)

if __name__=="__main__":
    unittest.main()
