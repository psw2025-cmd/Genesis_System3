import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_INTEGRITY = ROOT / "dashboard" / "frontend" / "src" / "components" / "workspaces" / "DataIntegrity.tsx"


class DataIntegrityFailClosedTruthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DATA_INTEGRITY.read_text(encoding="utf-8")

    def test_runtime_truth_derives_blockers_beyond_health_arrays(self):
        self.assertIn("derivedBlockers", self.text)
        self.assertIn("Broker not connected", self.text)
        self.assertIn("No verified option contracts", self.text)
        self.assertIn("QC ${qc}", self.text)

    def test_no_blockers_copy_is_only_the_empty_terminal_branch(self):
        self.assertIn("blockers.length > 0", self.text)
        self.assertIn("No active data blockers", self.text)
        self.assertLess(
            self.text.index("blockers.length > 0"),
            self.text.index("No active data blockers"),
        )


if __name__ == "__main__":
    unittest.main()
