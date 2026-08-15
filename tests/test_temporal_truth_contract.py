from __future__ import annotations

import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.system3_temporal_truth_guard import evaluate_manifest

ROOT = Path(__file__).resolve().parents[1]


class TemporalTruthContractTests(unittest.TestCase):
    def _manifest(self, started: datetime, captured: datetime) -> dict:
        return {
            "evidence_class": "REQUEST_SCOPED_LIVE_BROWSER",
            "capture_started_at_utc": started.isoformat(),
            "captured_at_utc": captured.isoformat(),
            "max_age_seconds": 300,
            "safety": {
                "read_only_capture": True,
                "mutation_endpoints_called": False,
                "order_endpoints_called": False,
                "secret_values_exposed": False,
            },
        }

    def test_fresh_request_scoped_browser_evidence_can_be_current(self):
        now = datetime(2026, 8, 15, 21, 10, tzinfo=timezone.utc)
        requested = now - timedelta(seconds=60)
        manifest = self._manifest(now - timedelta(seconds=50), now - timedelta(seconds=5))
        verdict = evaluate_manifest(manifest, requested_at=requested, now=now)
        self.assertTrue(verdict["current_live_allowed"])
        self.assertEqual(verdict["state"], "CURRENT_LIVE")

    def test_newest_but_old_artifact_is_not_current(self):
        now = datetime(2026, 8, 15, 21, 10, tzinfo=timezone.utc)
        manifest = self._manifest(now - timedelta(hours=1), now - timedelta(hours=1))
        verdict = evaluate_manifest(manifest, now=now)
        self.assertFalse(verdict["current_live_allowed"])
        self.assertIn("EVIDENCE_TOO_OLD_FOR_CURRENT_VERDICT", verdict["reasons"])

    def test_capture_before_request_cannot_answer_now(self):
        now = datetime(2026, 8, 15, 21, 10, tzinfo=timezone.utc)
        requested = now - timedelta(seconds=30)
        manifest = self._manifest(now - timedelta(seconds=90), now - timedelta(seconds=20))
        verdict = evaluate_manifest(manifest, requested_at=requested, now=now)
        self.assertFalse(verdict["current_live_allowed"])
        self.assertIn("CAPTURE_STARTED_BEFORE_CURRENT_REQUEST", verdict["reasons"])

    def test_reports_latest_name_has_no_temporal_authority(self):
        now = datetime(2026, 8, 15, 21, 10, tzinfo=timezone.utc)
        manifest = {
            "evidence_class": "REPORTS_LATEST",
            "captured_at_utc": now.isoformat(),
            "capture_started_at_utc": now.isoformat(),
            "safety": {},
        }
        verdict = evaluate_manifest(manifest, now=now)
        self.assertFalse(verdict["current_live_allowed"])
        self.assertIn("EVIDENCE_CLASS_NOT_LIVE", verdict["reasons"])

    def test_missing_capture_time_fails_closed(self):
        verdict = evaluate_manifest({"evidence_class": "REQUEST_SCOPED_LIVE_BROWSER"})
        self.assertFalse(verdict["current_live_allowed"])
        self.assertIn("CAPTURE_TIME_MISSING_OR_INVALID", verdict["reasons"])

    def test_agent_entry_points_reference_temporal_policy(self):
        required = [
            ROOT / "AGENTS.md",
            ROOT / "GEMINI.md",
            ROOT / ".cursorrules",
            ROOT / ".github" / "CLAUDE_INSTRUCTIONS.md",
            ROOT / "GOVERNANCE.md",
            ROOT / "docs" / "authority" / "AUTONOMOUS_OPERATIONS_POLICY.md",
            ROOT / "docs" / "project_control" / "SYSTEM3_MASTER_GOAL_LOCK.md",
        ]
        for path in required:
            text = path.read_text(encoding="utf-8", errors="replace")
            self.assertIn("SYSTEM3_TEMPORAL_TRUTH_V1", text, str(path))
            self.assertIn("TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md", text, str(path))

    def test_live_ui_script_captures_all_canonical_tabs_and_brackets_apis(self):
        text = (ROOT / "scripts" / "gcp_live_ui_snapshot.py").read_text(encoding="utf-8")
        for marker in [
            "from frontend_local_runtime_smoke import Browser, TABS, _wait_tab",
            '"evidence_class": "REQUEST_SCOPED_LIVE_BROWSER"',
            '"api_start": api_start',
            '"api_end": api_end',
            '"tabs_expected": list(TABS)',
            '"new_current_request_requires_new_capture": True',
        ]:
            self.assertIn(marker, text)

    def test_frontend_workflow_runs_temporal_contract_before_live_capture(self):
        text = (ROOT / ".github" / "workflows" / "frontend-runtime-smoke.yml").read_text(encoding="utf-8")
        self.assertIn("tests.test_temporal_truth_contract", text)
        self.assertIn("system3_temporal_truth_guard.py", text)
        self.assertIn("gcp_live_ui_snapshot.py", text)


if __name__ == "__main__":
    unittest.main()
