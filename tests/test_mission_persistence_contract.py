"""Fail if the mission control and independent-proof state are missing or dishonest."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "SYSTEM3"
PNG_NAMES = ("Architecture.png", "DependencyGraph.png", "RiskHeatmap.png",
             "RootCauseGraph.png", "DeploymentGraph.png", "DigitalTwin.png",
             "DataLineage.png", "ServiceMap.png", "APIMap.png")
REQUIRED = (
    "01_MASTER_STATE/SYSTEM3_MASTER_STATE.json",
    "02_EVIDENCE/EVIDENCE.ndjson",
    "04_OWNER/OWNER_STATUS.md",
    "05_AGENT_MEMORY/AGENT_MEMORY.md",
    "06_BLOCKERS/BLOCKERS.yaml",
    "07_DECISIONS/DECISIONS.md",
    "08_REPORTS/GITHUB_REPAIR_REPORT.md",
    "08_REPORTS/ARCHITECTURE_DISCOVERY_REPORT.md",
    "08_REPORTS/EVIDENCE_MATRIX.md",
    "08_REPORTS/RECOVERY_BLUEPRINT.md",
    "08_REPORTS/SAFETY_CERTIFICATION_REPORT.md",
    "08_REPORTS/FOUNDATION_AUDIT.md",
    "08_REPORTS/DIGITAL_TWIN_REPORT.md",
    "08_REPORTS/DEPENDENCY_INTELLIGENCE_REPORT.md",
    "08_REPORTS/OBSERVABILITY_PACKAGE.md",
    "08_REPORTS/DEPLOYMENT_CANDIDATE_REPORT.md",
    "10_HANDOVER/HANDOVER.md",
)


class MissionPersistenceTests(unittest.TestCase):
    def test_all_mandatory_artifacts_exist(self):
        for rel in REQUIRED:
            with self.subTest(path=rel):
                self.assertTrue((BASE / rel).is_file(), rel)
        for name in PNG_NAMES:
            image = BASE / "09_DIAGRAMS" / name
            self.assertTrue(image.is_file(), name)
            self.assertEqual(image.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            self.assertGreater(image.stat().st_size, 500)

    def test_master_production_and_broker_orders_are_not_falsely_passed(self):
        state=json.loads((BASE/"01_MASTER_STATE/SYSTEM3_MASTER_STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(state["repo"],"psw2025-cmd/Genesis_System3")
        self.assertEqual(state["overall"],"BLOCKED")
        self.assertNotEqual(state["production"],"PASS")
        self.assertEqual(state["safety"]["LIVE_TRADING_ENABLED"],"0")
        self.assertEqual(state["safety"]["AUTO_EXECUTE_TRADES"],"0")
        self.assertTrue(state["safety"]["real_orders"].startswith("UNKNOWN"))
        self.assertIn(state["phase_status"]["6"],("BLOCKED","UNKNOWN"))

    def test_evidence_ledger_is_nonempty_unique_and_never_fakes_production(self):
        lines=(BASE/"02_EVIDENCE/EVIDENCE.ndjson").read_text(encoding="utf-8").splitlines()
        rows=[json.loads(x) for x in lines]
        self.assertGreaterEqual(len(rows),8)
        ids=[r["id"] for r in rows]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(all(r["status"] in ("PASS","FAIL","UNKNOWN","BLOCKED") for r in rows))
        self.assertTrue(all(r["evidence_url"].startswith("https://github.com/psw2025-cmd/Genesis_System3/") for r in rows))
        self.assertNotIn("PASS",[r["status"] for r in rows if r["id"] in ("cloud-production","order-safety")])

    def test_owner_and_deployment_remain_separately_gated(self):
        owner=(BASE/"04_OWNER/OWNER_STATUS.md").read_text(encoding="utf-8")
        candidate=(BASE/"08_REPORTS/DEPLOYMENT_CANDIDATE_REPORT.md").read_text(encoding="utf-8")
        self.assertIn("NONE NOW",owner)
        self.assertIn("BLOCKED",candidate)
        self.assertIn("approval",candidate.lower())


if __name__=="__main__":
    unittest.main()
