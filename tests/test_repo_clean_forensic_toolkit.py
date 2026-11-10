import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "system3_repo_clean_forensic_toolkit.py"
spec = importlib.util.spec_from_file_location("system3_repo_clean_forensic_toolkit", MODULE_PATH)
toolkit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = toolkit
assert spec.loader is not None
spec.loader.exec_module(toolkit)


class RepoCleanForensicToolkitTests(unittest.TestCase):
    def _repo(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        files = {
            "desktop.ini": "noise",
            "assets/canonical.bin": "same-binary",
            "archive/canonical.bin": "same-binary",
            "src/tool.py": "VALUE = 1\n",
            "archive/tool.py": "VALUE = 1\n",
            "assets/referenced.bin": "referenced",
            "archive/referenced.bin": "referenced",
            "docs/use.md": "keep archive/referenced.bin because it is referenced\n",
            "core/runtime.py": 'print("runtime")\n',
            "markers/empty.keep": "",
            "archive/empty.keep": "",
        }
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)
        return tmp, root

    def test_policy_helpers(self):
        self.assertTrue(toolkit.is_generated_noise("x/__pycache__/a.pyc")[0])
        self.assertTrue(toolkit.is_protected("core/brokers/dhan.py")[0])
        self.assertIn("archive", toolkit.suspicious_path("archive/old.py"))

    def test_full_report_fail_closed_decisions(self):
        tmp, root = self._repo()
        self.addCleanup(tmp.cleanup)
        out = root / "out"
        summary = toolkit.build_report(root, out, include_actions=False)
        decisions = json.loads((out / "05_all_candidate_decisions.json").read_text())
        by_path = {row["path"]: row for row in decisions}

        self.assertEqual(by_path["desktop.ini"]["decision"], "DELETE_PROVEN_100")
        self.assertEqual(by_path["archive/canonical.bin"]["decision"], "DELETE_PROVEN_100")
        self.assertEqual(by_path["archive/tool.py"]["decision"], "QUARANTINE_FIRST_SOURCE_DUPLICATE")
        self.assertNotEqual(by_path["archive/referenced.bin"]["decision"], "DELETE_PROVEN_100")
        self.assertGreaterEqual(by_path["archive/referenced.bin"]["ref_count"], 1)
        self.assertEqual(by_path["archive/empty.keep"]["decision"], "REVIEW_ZERO_BYTE_MARKER")
        self.assertEqual(by_path["archive/empty.keep"]["replacement"], None)
        self.assertTrue(summary["no_files_deleted"])
        self.assertTrue((out / "00_EXECUTIVE_DELETE_DECISION.md").exists())
        self.assertTrue((root / "archive/canonical.bin").exists())
        self.assertTrue((root / "archive/empty.keep").exists())

    def test_delete_commands_include_only_proven_rows(self):
        tmp, root = self._repo()
        self.addCleanup(tmp.cleanup)
        out = root / "out"
        toolkit.build_report(root, out, include_actions=False)
        commands = (out / "DELETE_PROVEN_100_COMMANDS.txt").read_text()
        self.assertIn("desktop.ini", commands)
        self.assertIn("archive/canonical.bin", commands)
        self.assertNotIn("archive/tool.py", commands)
        self.assertNotIn("archive/referenced.bin", commands)
        self.assertNotIn("archive/empty.keep", commands)

    def test_github_storage_schema_when_unavailable(self):
        old_token = toolkit.os.environ.pop("GITHUB_TOKEN", None)
        old_repo = toolkit.os.environ.pop("GITHUB_REPOSITORY", None)
        try:
            result = toolkit.github_storage_inventory()
            self.assertFalse(result["available"])
            self.assertIn("unavailable", result["reason"])
        finally:
            if old_token is not None:
                toolkit.os.environ["GITHUB_TOKEN"] = old_token
            if old_repo is not None:
                toolkit.os.environ["GITHUB_REPOSITORY"] = old_repo


if __name__ == "__main__":
    unittest.main()
